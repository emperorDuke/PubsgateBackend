# Generated by Django 4.0.3 on 2022-09-18 13:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('SubmissionPortal', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='authorsubmission',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='articleprocessingcharge',
            name='author_submission',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='APC', to='SubmissionPortal.authorsubmission'),
        ),
    ]
