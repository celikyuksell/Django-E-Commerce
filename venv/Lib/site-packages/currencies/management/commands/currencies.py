# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from collections import OrderedDict
from importlib import import_module
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.exceptions import ImproperlyConfigured
from ...models import Currency


# The list of available backend currency sources
sources = OrderedDict([
    # oxr must remain first for backward compatibility
    ('oxr',     '._openexchangerates'),
    ('yahoo',   '._yahoofinance'),
    ('iso',     '._currencyiso'),
    #TODO:
    #('google', '._googlecalculator.py'),
    #('ecb', '._europeancentralbank.py'),
])


logger = logging.getLogger("django.currencies")


class Command(BaseCommand):
    help = "Create all missing db currencies available from the chosen source"

    _package_name = __name__.rsplit('.', 1)[0]
    _source_param = 'source'
    _source_default = next(iter(sources))
    _source_kwargs = {'action': 'store', 'nargs': '?', 'default': _source_default,
                        'choices': sources.keys(),
                        'help': 'Select the desired currency source, default is ' + _source_default}

    def add_arguments(self, parser):
        """Add command arguments"""
        parser.add_argument(self._source_param, **self._source_kwargs)
        parser.add_argument('--force', '-f', action='store_true', default=False,
            help='Update database even if currency already exists')
        parser.add_argument('--import', '-i', action='append', default=[],
            help=   'Selectively import currencies by supplying the currency codes (e.g. USD) one per switch, '
                    'or supply an uppercase settings variable name with an iterable (once only), '
                    'or looks for settings CURRENCIES or SHOP_CURRENCIES.')

    def get_imports(self, option):
        """
        See if we have been passed a set of currencies or a setting variable
        or look for settings CURRENCIES or SHOP_CURRENCIES.
        """
        if option:
            if len(option) == 1 and option[0].isupper() and len(option[0]) > 3:
                return getattr(settings, option[0])
            else:
                codes = [e for e in option if e.isupper() and len(e) == 3]
                if len(codes) != len(option):
                    raise ImproperlyConfigured("Invalid currency codes found: %s" % codes)
                return codes
        for attr in ('CURRENCIES', 'SHOP_CURRENCIES'):
            try:
                return getattr(settings, attr)
            except AttributeError:
                continue
        return option

    @property
    def verbosity(self):
        return getattr(self, '_verbosity', logging.INFO)

    @verbosity.setter
    def verbosity(self, value):
        self._verbosity = {
            0: logging.ERROR,
            1: logging.INFO,
            2: logging.DEBUG,
            3: 0
        }.get(value)

    def log(self, lvl, msg, *args, **kwargs):
        """Both prints to stdout/stderr and the django.currencies logger"""
        logger.log(lvl, msg, *args, **kwargs)

        if lvl >= self.verbosity:
            if args:
                fmsg = msg % args
            else:
                fmsg = msg % kwargs

            if lvl >= logging.WARNING:
                self.stderr.write(fmsg)
            else:
                self.stdout.write(fmsg)

    def get_handler(self, options):
        """Return the specified handler"""
        # Import the CurrencyHandler and get an instance
        handler_module = import_module(sources[options[self._source_param]], self._package_name)
        return handler_module.CurrencyHandler(self.log)

    def handle(self, *args, **options):
        """Handle the command"""
        # get the command arguments
        self.verbosity = int(options.get('verbosity', 1))
        force = options['force']
        imports = self.get_imports(options['import'])

        # Import the CurrencyHandler and get an instance
        handler = self.get_handler(options)

        self.log(logging.INFO, "Getting currency data from %s", handler.endpoint)
        timestamp = datetime.now().isoformat()

        # find available codes
        if imports:
            allcodes = set(handler.get_allcurrencycodes())
            reqcodes = set(imports)
            available = reqcodes & allcodes
            unavailable = reqcodes - allcodes
        else:
            self.log(logging.WARNING, "Importing all. Some currencies may be out-of-date (MTL) or spurious (XPD)")
            available = handler.get_allcurrencycodes()
            unavailable = None

        for code in available:
            obj, created = Currency._default_manager.get_or_create(code=code)
            name = handler.get_currencyname(code)
            description = "%r (%s)" % (name, code)
            if created or force:
                kwargs = {}
                if created:
                    kwargs['is_active'] = False
                    msg = "Creating %s"
                    obj.info.update( {'Created': timestamp} )
                else:
                    msg = "Updating %s"
                obj.info.update( {'Modified': timestamp} )

                if name:
                    kwargs['name'] = name

                symbol = handler.get_currencysymbol(code)
                if symbol:
                    kwargs['symbol'] = symbol

                try:
                    obj.info.update(handler.get_info(code))
                except AttributeError:
                    pass

                kwargs['info'] = obj.info

                self.log(logging.INFO, msg, description)
                Currency._default_manager.filter(pk=obj.pk).update(**kwargs)
            else:
                msg = "Skipping %s"
                self.log(logging.INFO, msg, description)

        if unavailable:
            raise ImproperlyConfigured("Currencies %s not found in %s source" % (unavailable, handler.name))
