# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pages.Page')),
                ('content', mezzanine.core.fields.RichTextField(verbose_name='Content')),
                ('zip_import', models.FileField(help_text="Upload a zip file containing images, and they'll be imported into this gallery.", upload_to='galleries', verbose_name='Zip import', blank=True)),
            ],
            options={
                'ordering': ('_order',),
                'verbose_name': 'Gallery',
                'verbose_name_plural': 'Galleries',
            },
            bases=('pages.page', models.Model),
        ),
        migrations.CreateModel(
            name='GalleryImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_order', models.IntegerField(null=True, verbose_name='Order')),
                ('file', mezzanine.core.fields.FileField(max_length=200, verbose_name='File')),
                ('description', models.CharField(max_length=1000, verbose_name='Description', blank=True)),
                ('gallery', models.ForeignKey(related_name='images', to='galleries.Gallery')),
            ],
            options={
                'ordering': ('_order',),
                'verbose_name': 'Image',
                'verbose_name_plural': 'Images',
            },
            bases=(models.Model,),
        ),
    ]
