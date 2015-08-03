# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def add_documents_to_default_collection(apps, schema_editor):
    Collection = apps.get_model('wagtailcore.Collection')
    Document = apps.get_model('wagtaildocs.Document')
    default_collection, _created = Collection.objects.get_or_create(name='Default')
    Document.objects.update(collection=default_collection)


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0018_collection_initial_data'),
        ('wagtaildocs', '0003_add_verbose_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='collection',
            field=models.ForeignKey(verbose_name='collection', related_name='+', to='wagtailcore.Collection', null=True),
            preserve_default=False,
        ),
        migrations.RunPython(add_documents_to_default_collection),
        migrations.AlterField(
            model_name='document',
            name='collection',
            field=models.ForeignKey(verbose_name='collection', related_name='+', to='wagtailcore.Collection', null=False),
            preserve_default=True,
        ),
    ]
