# Generated by Django 3.1.2 on 2020-10-28 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0009_remove_person_predicted_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='hass_name',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='person',
            name='name',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
    ]