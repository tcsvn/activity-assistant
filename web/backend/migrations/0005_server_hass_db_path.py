# Generated by Django 3.1.2 on 2020-10-27 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_auto_20201026_2358'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='hass_db_path',
            field=models.CharField(max_length=100, null=True),
        ),
    ]