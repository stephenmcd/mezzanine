# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=10, verbose_name='Type', choices=[('user', 'User'), ('list', 'List'), ('search', 'Search')])),
                ('value', models.CharField(max_length=140, verbose_name='Value')),
                ('interested', models.BooleanField(default=True, verbose_name='Interested')),
            ],
            options={
                'ordering': ('-id',),
                'verbose_name': 'Twitter query',
                'verbose_name_plural': 'Twitter queries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('remote_id', models.CharField(max_length=50, verbose_name='Twitter ID')),
                ('created_at', models.DateTimeField(null=True, verbose_name='Date/time')),
                ('text', models.TextField(null=True, verbose_name='Message')),
                ('profile_image_url', models.URLField(null=True, verbose_name='Profile image URL')),
                ('user_name', models.CharField(max_length=100, null=True, verbose_name='User name')),
                ('full_name', models.CharField(max_length=100, null=True, verbose_name='Full name')),
                ('retweeter_profile_image_url', models.URLField(null=True, verbose_name='Profile image URL (Retweeted by)')),
                ('retweeter_user_name', models.CharField(max_length=100, null=True, verbose_name='User name (Retweeted by)')),
                ('retweeter_full_name', models.CharField(max_length=100, null=True, verbose_name='Full name (Retweeted by)')),
                ('query', models.ForeignKey(related_name='tweets', to='twitter.Query')),
            ],
            options={
                'ordering': ('-created_at',),
                'verbose_name': 'Tweet',
                'verbose_name_plural': 'Tweets',
            },
            bases=(models.Model,),
        ),
    ]
