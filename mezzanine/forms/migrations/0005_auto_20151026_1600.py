# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0004_auto_20150517_0510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='field',
            name='placeholder_text',
            field=models.CharField(max_length=100, verbose_name='Placeholder Text', blank=True),
        ),
    ]
