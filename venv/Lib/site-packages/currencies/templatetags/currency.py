# -*- coding: utf-8 -*-

from django import template
from django.template.defaultfilters import stringfilter

from currencies.models import Currency
from currencies.utils import get_currency_code, calculate

register = template.Library()


class ChangeCurrencyNode(template.Node):

    def __init__(self, price, currency):
        self.price = template.Variable(price)
        self.currency = template.Variable(currency)

    def render(self, context):
        try:
            return calculate(self.price.resolve(context), self.currency.resolve(context))
        except template.VariableDoesNotExist:
            return ''


@register.tag(name='change_currency')
def change_currency(parser, token):
    try:
        tag_name, current_price, new_currency = token.split_contents()
    except ValueError:
        tag_name = token.contents.split()[0]
        raise template.TemplateSyntaxError(
            """%r tag requires exactly two arguments""" % tag_name)
    return ChangeCurrencyNode(current_price, new_currency)


@register.simple_tag
def show_currency(price, code, decimals=2):
    return calculate(price, code, decimals=decimals)


@stringfilter
@register.filter(name='currency')
def do_currency(price, code):
    return calculate(price, code)


def memoize_nullary(f):
    """
    Memoizes a function that takes no arguments.  The memoization lasts only as
    long as we hold a reference to the returned function.
    """
    def func():
        if not hasattr(func, 'retval'):
            func.retval = f()
        return func.retval
    return func

def get_currency(arg):
    try:
        code = arg()
    except TypeError:
        code = arg

    try:
        return Currency.active.get(code__iexact=code)
    except Currency.DoesNotExist:
        return None


@register.simple_tag(takes_context=True)
def currency_context(context):
    """
    Use instead of context processor
    Context variables are only valid within the block scope
    """
    request = context['request']
    currency_code = memoize_nullary(lambda: get_currency_code(request))

    context['CURRENCIES'] = Currency.active.all() # querysets are already lazy
    context['CURRENCY_CODE'] = currency_code # lazy
    context['CURRENCY'] = memoize_nullary(lambda: get_currency(currency_code)) # lazy

    return ''
