# Generated by Django 2.2.5 on 2019-09-27 14:45

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0042_simplechildpage_simpleparentpage'),
    ]

    operations = [
        migrations.AddField(
            model_name='customdocument',
            name='fancy_description',
            field=wagtail.core.fields.RichTextField(blank=True),
        ),
        migrations.AddField(
            model_name='customdocument',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.contenttype'),
        ),
    ]
