# Generated by Django 2.2.10 on 2020-04-11 09:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0071_rename_profilehighlight_sequence'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProfileData',
        ),
    ]