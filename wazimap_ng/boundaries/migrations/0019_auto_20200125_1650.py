# Generated by Django 2.2.8 on 2020-01-25 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boundaries', '0018_auto_20200125_1604'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='country',
            index=models.Index(fields=['code'], name='boundaries__code_1d7b13_idx'),
        ),
        migrations.AddIndex(
            model_name='district',
            index=models.Index(fields=['code'], name='boundaries__code_9f7e30_idx'),
        ),
        migrations.AddIndex(
            model_name='mainplace',
            index=models.Index(fields=['code'], name='boundaries__code_2d305e_idx'),
        ),
        migrations.AddIndex(
            model_name='municipality',
            index=models.Index(fields=['code'], name='boundaries__code_ca68d6_idx'),
        ),
        migrations.AddIndex(
            model_name='province',
            index=models.Index(fields=['code'], name='boundaries__code_0f299b_idx'),
        ),
        migrations.AddIndex(
            model_name='subplace',
            index=models.Index(fields=['code'], name='boundaries__code_7f6234_idx'),
        ),
        migrations.AddIndex(
            model_name='ward',
            index=models.Index(fields=['code'], name='boundaries__code_2cb22e_idx'),
        ),
    ]
