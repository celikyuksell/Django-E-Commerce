# -*- coding: utf-8 -*-
# Created by Aleksandr Pasevin on 2019-07-05 17:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('currencies', '0005_alter_help_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currency',
            name='name',
            field=models.CharField(max_length=55, verbose_name='name', db_index=True)
        ),
    ]
