# Generated by Django 2.2.10 on 2020-04-22 09:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('points', '0015_profilecategory_collection_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profilecategory',
            old_name='collection_type',
            new_name='permission_type',
        ),
    ]
