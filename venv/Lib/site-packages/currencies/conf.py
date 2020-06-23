# -*- coding: utf-8 -*-

from django.conf import settings

SESSION_PREFIX = getattr(settings, 'CURRENCY_SESSION_PREFIX', 'session')
SESSION_KEY = '%s.currency_code' % SESSION_PREFIX
