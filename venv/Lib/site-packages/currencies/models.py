# -*- coding: utf-8 -*-

from six import python_2_unicode_compatible
from django.db import models
from django.utils.translation import gettext_lazy as _
from jsonfield.fields import JSONField

from .managers import CurrencyManager


@python_2_unicode_compatible
class Currency(models.Model):

    code = models.CharField(_('code'), max_length=3,
                            primary_key=True)
    name = models.CharField(_('name'), max_length=55,
                            db_index=True)
    symbol = models.CharField(_('symbol'), max_length=4, blank=True,
                            db_index=True)
    factor = models.DecimalField(_('factor'), max_digits=30, decimal_places=10, default=1.0,
        help_text=_('Specifies the currency rate ratio to the base currency.'))

    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('The currency will be available.'))
    is_base = models.BooleanField(_('base'), default=False,
        help_text=_('Make this the base currency against which rate factors are calculated.'))
    is_default = models.BooleanField(_('default'), default=False,
        help_text=_('Make this the default user currency.'))

    # Used to store other available information about a currency
    info = JSONField(blank=True, default={})

    objects = models.Manager()
    active = CurrencyManager()

    class Meta:
        ordering = ['name']
        verbose_name = _('currency')
        verbose_name_plural = _('currencies')

    def __str__(self):
        return self.code

    def save(self, **kwargs):
        # Make sure the base and default currencies are unique
        if self.is_base is True:
            self.__class__._default_manager.filter(is_base=True).update(is_base=False)

        if self.is_default is True:
            self.__class__._default_manager.filter(is_default=True).update(is_default=False)

        # Make sure default / base currency is active
        if self.is_default or self.is_base:
            self.is_active = True

        super(Currency, self).save(**kwargs)
