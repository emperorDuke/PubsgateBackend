# Generated by Django 4.0.3 on 2022-07-31 16:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Journals', '0006_editorrecruitmentapplication'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recruitmentapplication',
            options={'ordering': ['-created_at'], 'verbose_name': 'recruitment application', 'verbose_name_plural': 'recruitment applications'},
        ),
        migrations.AddField(
            model_name='recruitmentapplication',
            name='role',
            field=models.PositiveIntegerField(choices=[(1, 'editor'), (2, 'reviewer')], default=1, verbose_name='role'),
        ),
        migrations.AlterField(
            model_name='recruitmentapplication',
            name='journal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recruitment_applications', to='Journals.journal'),
        ),
        migrations.AlterModelTable(
            name='recruitmentapplication',
            table='recruitment_applications',
        ),
    ]
