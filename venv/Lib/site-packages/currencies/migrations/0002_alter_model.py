# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('currencies', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currency',
            name='code',
            field=models.CharField(unique=True, max_length=3, verbose_name='code', db_index=True),
        ),
        migrations.AlterField(
            model_name='currency',
            name='name',
            field=models.CharField(max_length=35, verbose_name='name', db_index=True),
        ),
        migrations.AlterField(
            model_name='currency',
            name='symbol',
            field=models.CharField(db_index=True, max_length=4, verbose_name='symbol', blank=True),
        ),
    ]
