# -*- coding: utf-8 -*-
from decimal import Decimal as D, InvalidOperation, ROUND_UP
from .models import Currency as C
from .conf import SESSION_KEY


def get_active_currencies_qs():
    return C.active.defer('info').all()


def calculate(price, to_code, **kwargs):
    """Converts a price in the default currency to another currency"""
    qs = kwargs.get('qs', get_active_currencies_qs())
    kwargs['qs'] = qs
    default_code = qs.default().code
    return convert(price, default_code, to_code, **kwargs)


def convert(amount, from_code, to_code, decimals=2, qs=None):
    """Converts from any currency to any currency"""
    if from_code == to_code:
        return amount

    if qs is None:
        qs = get_active_currencies_qs()

    from_, to = qs.get(code=from_code), qs.get(code=to_code)

    amount = D(amount) * (to.factor / from_.factor)
    return price_rounding(amount, decimals=decimals)


def get_currency_code(request):
    for attr in ('session', 'COOKIES'):
        if hasattr(request, attr):
            try:
                return getattr(request, attr)[SESSION_KEY]
            except KeyError:
                continue

    # fallback to default...
    try:
        return C.active.default().code
    except C.DoesNotExist:
        return None  # shit happens...


def price_rounding(price, decimals=2):
    """Takes a decimal price and rounds to a number of decimal places"""
    try:
        exponent = D('.' + decimals * '0')
    except InvalidOperation:
        # Currencies with no decimal places, ex. JPY, HUF
        exponent = D()
    return price.quantize(exponent, rounding=ROUND_UP)
