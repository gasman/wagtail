# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import VERSION as DJANGO_VERSION
from django.db import migrations


def initial_data(apps, schema_editor):
    Collection = apps.get_model('wagtailcore.Collection')

    # Create root page
    Collection.objects.create(
        name="Root",
        path='0001',
        depth=1,
        numchild=0,
    )


def noop(apps, schema_editor):
    # no action required to reverse initial_data
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0020_collection'),
    ]

    operations = [
        migrations.RunPython(initial_data, noop),
    ]
