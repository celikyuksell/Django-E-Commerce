# -*- coding: utf-8 -*-
import sys, re, json, os
import logging
# requires beautifulsoup4 and requests
from bs4 import BeautifulSoup as BS4
from requests import get, exceptions
from decimal import Decimal
from datetime import datetime

from ._currencyhandler import BaseHandler

if sys.version_info.major == 2:
    FileNotFoundError = IOError


class CurrencyHandler(BaseHandler):
    """
    Currency Handler implements public API:
    name
    endpoint
    get_allcurrencycodes()
    get_currencyname(code)
    get_currencysymbol(code)
    get_info(code)
    get_ratetimestamp(base, code)
    get_ratefactor(base, code)
    """
    name = 'Yahoo Finance'
    endpoint = 'http://finance.yahoo.com'
    onerate_url = 'http://finance.yahoo.com/d/quotes.csv?s=%s%s=X&f=l1'
    full_url = 'http://uk.finance.yahoo.com/webservice/v1/symbols/allcurrencies/quote;currency=true?view=basic&format=json&callback=YAHOO.Finance.CurrencyConverter.addConversionRates'
    ukbulk_url = 'http://uk.finance.yahoo.com/webservice/v1/symbols/allcurrencies/quote?format=json'
    bulk_url = 'http://finance.yahoo.com/webservice/v1/symbols/allcurrencies/quote?format=json'
    currencies_url = 'http://finance.yahoo.com/currency-converter/'

    _cached_currency_file = os.path.join(BaseHandler._dir, '_yahoofinance.json')

    modified = None
    _currencies = None
    _rates = None
    _base = None

    @property
    def currencies(self):
        if not self._currencies:
            self._currencies = self.get_bulkcurrencies()
            self.modified = datetime.fromtimestamp(os.path.getmtime(self._cached_currency_file))
        return self._currencies

    @property
    def rates(self):
        if not self._rates:
            self._rates = self.get_bulkrates()
        return self._rates

    @property
    def base(self):
        if not self._base:
            self._base = self.get_baserate()
        return self._base

    def get_bulkcurrencies(self):
        """
        Get the supported currencies
        Scraped from a JSON object on the html page in javascript tag
        """
        start = r'YAHOO\.Finance\.CurrencyConverter\.addCurrencies\('
        _json = r'\[[^\]]*\]'
        try:
            resp = get(self.currencies_url)
            resp.raise_for_status()
        except exceptions.RequestException as e:
            self.log(logging.ERROR, "%s Deprecated: API withdrawn in February 2018:\n%s", self.name, e)
        else:
            # Find the javascript that contains the json object
            soup = BS4(resp.text, 'html.parser')
            re_start = re.compile(start)
            try:
                jscript = soup.find('script', type='text/javascript', text=re_start).string
            except AttributeError:
                self.log(logging.WARNING, "%s: Live currency data not found, using cached copy.", self.name)
            else:
                # Separate the json object
                re_json = re.compile(_json)
                match = re_json.search(jscript)
                if match:
                    json_str = match.group(0)
                    with open(self._cached_currency_file, 'w') as fd:
                        fd.write(json_str.encode('utf-8'))

        # Parse the json file
        try:
            with open(self._cached_currency_file, 'r') as fd:
                j = json.load(fd)
        except FileNotFoundError:
            j = None
        if not j:
            raise RuntimeError("%s: JSON not found at endpoint or as cached file:\n%s" % (
                self.name, self._cached_currency_file))
        return j

    def get_bulkrates(self):
        """Get & format the rates dict"""
        try:
            resp = get(self.bulk_url)
            resp.raise_for_status()
        except exceptions.RequestException as e:
            raise RuntimeError(e)
        return resp.json()

    def get_singlerate(self, base, code):
        """Get a single rate, used as fallback"""
        try:
            url = self.onerate_url % (base, code)
            resp = get(url)
            resp.raise_for_status()
        except exceptions.HTTPError as e:
            self.log(logging.ERROR, "%s: problem with %s:\n%s", self.name, url, e)
            return None
        rate = resp.text.rstrip()

        if rate == 'N/A':
            raise RuntimeError("%s: %s not found" % (self.name, code))
        else:
            return Decimal(rate)

    def get_allcurrencycodes(self):
        """Return an iterable of 3 character ISO 4217 currency codes"""
        return (currency['shortname'] for currency in self.currencies)

    def get_currency(self, code):
        """
        Helper function
        Returns a dict containing:
        shortname (the code)
        longname
        users - a comma separated list of countries/regions/cities that use it
        alternatives - alternative names, e.g. ewro, Quid, Buck
        symbol - e.g. £, $
        highlight - ?
        """
        for currency in self.currencies:
            if currency['shortname'] == code:
                return currency
        raise RuntimeError("%s: %s not found" % (self.name, code))

    def get_currencyname(self, code):
        """Return the currency name from the code"""
        return self.get_currency(code)['longname']

    def get_currencysymbol(self, code):
        """Return the currency symbol from the code"""
        return self.get_currency(code)['symbol']

    def get_info(self, code):
        """Return a dict of information about the currency"""
        currency = self.get_currency(code)
        info = {}

        users = list(filter(None, currency['users'].split(',')))
        if users:
            info['Users'] = users

        alt = list(filter(None, currency['alternatives'].split(',')))
        if alt:
            info['Alternatives'] = alt

        if self.modified:
            info['YFUpdate'] = self.modified.isoformat()

        return info

    def get_rate(self, code):
        """
        Helper function to access the rates structure
        Returns a dict containing name, price, symbol (the code), timestamp, type, utctime & volume
        """
        rateslist = self.rates['list']['resources']
        for rate in rateslist:
            rateobj = rate['resource']['fields']
            if rateobj['symbol'].startswith(code):
                return rateobj
        raise RuntimeError("%s: %s not found" % (self.name, code))

    def get_baserate(self):
        """Helper function to populate the base rate"""
        rateslist = self.rates['list']['resources']
        for rate in rateslist:
            rateobj = rate['resource']['fields']
            if rateobj['symbol'].partition('=')[0] == rateobj['name']:
                return rateobj['name']
        raise RuntimeError("%s: baserate not found" % self.name)

    def get_ratetimestamp(self, base, code):
        """Return rate timestamp as a datetime/date or None"""
        try:
            ts = int(self.get_rate(code)['ts'])
        except RuntimeError:
            return None
        return datetime.fromtimestamp(ts)

    def check_ratebase(self, rate):
        """Helper function"""
        split = rate['name'].partition('/')
        if split[1]:
            ratebase = split[0]
            if ratebase != self.base:
                raise RuntimeError("%s: %s has different base rate:\n%s" % (
                    self.name, ratebase, rate))
        elif rate['name'] == self.base:
            pass
        # Codes beginning with 'X' are treated specially, e.g.
        # Gold (XAU), Copper (XCP), Palladium (XPD), Platinum (XPT), Silver (XAG)
        # They still appear to be based on USD but are reported with no base
        elif not rate['symbol'].startswith('X'):
            self.log(logging.WARNING, "%s: currency found with no base:\n%s", self.name, rate)


    def get_ratefactor(self, base, code):
        """
        Return the Decimal currency exchange rate factor of 'code' compared to 1 'base' unit, or RuntimeError
        Yahoo currently uses USD as base currency, but here we detect it with get_baserate
        """
        raise RuntimeError("%s Deprecated: API withdrawn in February 2018" % self.name)
        try:
            rate = self.get_rate(code)
        except RuntimeError:
            # fallback
            return self.get_singlerate(base, code)

        self.check_ratebase(rate)
        ratefactor = Decimal(rate['price'])

        if base == self.base:
            return ratefactor
        else:
            return self.ratechangebase(ratefactor, self.base, base)
