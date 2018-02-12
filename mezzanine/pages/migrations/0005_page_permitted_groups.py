# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('pages', '0004_auto_20170411_0504'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='permitted_groups',
            field=models.ManyToManyField(blank=True, help_text='Limit viewing permission to these groups.', to='auth.Group', verbose_name='Permitted groups'),
        ),
    ]
