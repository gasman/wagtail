# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import VERSION as DJANGO_VERSION
from django.db import migrations


def initial_data(apps, schema_editor):
    Collection = apps.get_model('wagtailcollections.Collection')

    default_collection = Collection.objects.create(
        name="Default",
    )


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcollections', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(initial_data),
    ]
