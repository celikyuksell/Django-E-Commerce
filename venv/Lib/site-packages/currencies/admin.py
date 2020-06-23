# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Currency


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "is_base", "is_default", "code", "symbol", "factor")
    list_filter = ("is_active", )
    search_fields = ("name", "code")

admin.site.register(Currency, CurrencyAdmin)
