# Generated by Django 2.2.10 on 2020-07-29 08:05

from django.db import migrations, models
import django.db.models.deletion


def add_theme_to_pc(apps, schema_editor):

    ProfileCategory = apps.get_model('points', 'ProfileCategory')

    for pc in ProfileCategory.objects.all():
        pc.theme = pc.category.theme
        pc.save()

class Migration(migrations.Migration):

    dependencies = [
        ('points', '0032_auto_20200730_1120'),
    ]

    operations = [
        migrations.AddField(
            model_name='profilecategory',
            name='theme',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='points.Theme'),
        ),
        migrations.RunPython(add_theme_to_pc),
        migrations.RemoveField(
            model_name='category',
            name='theme',
        ),
    ]
