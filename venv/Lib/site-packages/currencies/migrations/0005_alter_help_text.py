# -*- coding: utf-8 -*-
# Created by Aleksandr Pasevin on 2019-07-05 14:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('currencies', '0004_code_primary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currency',
            name='factor',
            field=models.DecimalField(decimal_places=10, default=1.0,
                                      help_text='Specifies the currency rate ratio to the base currency.',
                                      max_digits=30, verbose_name='factor'),
        ),
        migrations.AlterField(
            model_name='currency',
            name='is_base',
            field=models.BooleanField(default=False,
                                      help_text='Make this the base currency against which rate factors are calculated.',
                                      verbose_name='base'),
        ),
    ]
