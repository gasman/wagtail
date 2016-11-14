# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2016-11-14 20:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0016_deprecate_rendition_filter_relation'),
        ('modeladmintest', '0003_publisher'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='cover_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='wagtailimages.Image'),
        ),
    ]
