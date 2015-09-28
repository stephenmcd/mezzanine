# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0004_auto_20150517_0510'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='use_captcha',
            field=models.BooleanField(default=True, help_text='Prevent form submit (and email processing) if captcha not OK', verbose_name='Require captcha'),
        ),
    ]
