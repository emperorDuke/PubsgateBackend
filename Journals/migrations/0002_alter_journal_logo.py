# Generated by Django 4.0.3 on 2022-07-17 15:13

import Journals.models.journals
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Journals', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journal',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to=Journals.models.journals.Journal.upload_to, verbose_name='logo'),
        ),
    ]
