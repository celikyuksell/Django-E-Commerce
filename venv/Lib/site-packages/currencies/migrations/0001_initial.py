# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=3, verbose_name='code')),
                ('name', models.CharField(max_length=35, verbose_name='name')),
                ('symbol', models.CharField(max_length=4, verbose_name='symbol', blank=True)),
                ('factor', models.DecimalField(default=1.0, help_text='Specifies the difference of the currency to default one.', verbose_name='factor', max_digits=30, decimal_places=10)),
                ('is_active', models.BooleanField(default=True, help_text='The currency will be available.', verbose_name='active')),
                ('is_base', models.BooleanField(default=False, help_text='Make this the base currency against which rates are calculated.', verbose_name='base')),
                ('is_default', models.BooleanField(default=False, help_text='Make this the default user currency.', verbose_name='default')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'currency',
                'verbose_name_plural': 'currencies',
            },
            bases=(models.Model,),
        ),
    ]
