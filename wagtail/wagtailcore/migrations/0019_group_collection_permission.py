# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('wagtailcore', '0018_collection_initial_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupCollectionPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('collection', models.ForeignKey(verbose_name='collection', to='wagtailcore.Collection', related_name='group_permissions')),
                ('group', models.ForeignKey(verbose_name='group', to='auth.Group', related_name='collection_permissions')),
                ('permission', models.ForeignKey(verbose_name='permission', to='auth.Permission')),
            ],
            options={
                'verbose_name': 'group collection permission',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='groupcollectionpermission',
            unique_together=set([('group', 'collection', 'permission')]),
        ),
    ]
