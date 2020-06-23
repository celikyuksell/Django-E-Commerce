# -*- coding: utf-8 -*-

from django.db import models


class CurrencyQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_active=True)

    def default(self):
        return self.get(is_default=True)

    def base(self):
        return self.get(is_base=True)


class CurrencyManager(models.Manager):

    def get_queryset(self):
        return CurrencyQuerySet(self.model, using=self._db).active()

    def default(self):
        return self.get_queryset().default()

    def base(self):
        return self.get_queryset().base()
