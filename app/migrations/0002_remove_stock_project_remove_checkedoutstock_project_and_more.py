# Generated by Django 5.0.3 on 2024-06-20 22:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stock',
            name='project',
        ),
        migrations.RemoveField(
            model_name='checkedoutstock',
            name='project',
        ),
        migrations.AlterField(
            model_name='stock',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='app.location', verbose_name='Location/Project'),
        ),
        migrations.DeleteModel(
            name='Project',
        ),
    ]