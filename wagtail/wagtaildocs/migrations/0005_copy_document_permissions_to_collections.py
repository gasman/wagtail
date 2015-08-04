# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import VERSION as DJANGO_VERSION
from django.db import models, migrations


def get_document_permissions(apps):
    # return a queryset of all permissions relating to documents
    Permission = apps.get_model('auth.Permission')
    ContentType = apps.get_model('contenttypes.ContentType')

    document_content_type, _created = ContentType.objects.get_or_create(
        model='document',
        app_label='wagtaildocs',
        defaults={'name': 'document'} if DJANGO_VERSION < (1, 8) else {}
    )
    return Permission.objects.filter(content_type=document_content_type)


def copy_document_permissions_to_collections(apps, schema_editor):
    Collection = apps.get_model('wagtailcore.Collection')
    Group = apps.get_model('auth.Group')
    GroupCollectionPermission = apps.get_model('wagtailcore.GroupCollectionPermission')

    default_collection, _created = Collection.objects.get_or_create(name='Default')

    for permission in get_document_permissions(apps):
        for group in Group.objects.filter(permissions=permission):
            GroupCollectionPermission.objects.create(
                group=group,
                collection=default_collection,
                permission=permission
            )


def remove_document_permissions_from_collections(apps, schema_editor):
    GroupCollectionPermission = apps.get_model('wagtailcore.GroupCollectionPermission')
    document_permissions = get_document_permissions(apps)

    GroupCollectionPermission.objects.filter(permission__in=document_permissions).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0019_group_collection_permission'),
        ('wagtaildocs', '0004_document_collection'),
    ]

    operations = [
        migrations.RunPython(
            copy_document_permissions_to_collections,
            remove_document_permissions_from_collections),
    ]
