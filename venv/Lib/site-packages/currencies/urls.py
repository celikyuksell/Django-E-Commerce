# -*- coding: utf-8 -*-

from django.conf.urls import *
from currencies.views import set_currency

urlpatterns = [
    url(r'^setcurrency/$', set_currency, name='currencies_set_currency'),
]
