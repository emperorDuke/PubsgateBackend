# Generated by Django 4.0.3 on 2022-08-05 19:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Cores', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subjectdiscipline',
            options={'ordering': ('name',), 'verbose_name': 'subject_discipline', 'verbose_name_plural': 'subject_disciplines'},
        ),
    ]
