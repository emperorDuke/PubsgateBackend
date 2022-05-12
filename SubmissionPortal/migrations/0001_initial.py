# Generated by Django 4.0.3 on 2022-05-11 17:41

import SubmissionPortal.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Cores', '0001_initial'),
        ('Contents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthorSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('article_type', models.IntegerField(choices=[(1, 'research article'), (2, 'review article')], verbose_name='article_type')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('manuscript', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='author_submission', to='Contents.manuscript')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'submission',
                'verbose_name_plural': 'submissions',
                'db_table': 'author_submissions',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SubmissionStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stage', models.IntegerField(choices=[(1, 'out for review'), (2, 'is with editor'), (3, 'accepted'), (4, 'published')], default=2, verbose_name='stage')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author_submission', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='status', to='SubmissionPortal.authorsubmission')),
            ],
            options={
                'verbose_name': 'submission_status',
                'verbose_name_plural': 'submission_status',
                'db_table': 'author_submission_statuses',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='SubmissionFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.PositiveIntegerField(blank=True, default=1, verbose_name='version')),
                ('file_type', models.PositiveIntegerField(choices=[(1, 'Cover letter'), (2, 'Manuscript'), (3, 'Supplementary data')], verbose_name='file type')),
                ('file', models.FileField(max_length=255, upload_to=SubmissionPortal.models.SubmissionFile.file_path, verbose_name='file')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author_submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='SubmissionPortal.authorsubmission')),
            ],
            options={
                'verbose_name': 'submission_file',
                'verbose_name_plural': 'submission_files',
                'db_table': 'author_submission_files',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SubmissionConditionAgreement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statement', models.TextField(blank=True, null=True, verbose_name='statement')),
                ('documented_at', models.DateTimeField(auto_now_add=True, verbose_name='documented_at')),
                ('response', models.IntegerField(choices=[(1, 'YES'), (2, 'NO')], default=2, verbose_name='response')),
                ('author_submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agreements', to='SubmissionPortal.authorsubmission')),
                ('term', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Cores.termofservice')),
            ],
            options={
                'verbose_name': 'submission_condition_agreements',
                'db_table': 'author_submission_condition_agreements',
                'ordering': ['documented_at'],
            },
        ),
        migrations.CreateModel(
            name='ArticleProcessingCharge',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='amount')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(choices=[(1, 'successful'), (2, 'pending'), (3, 'failed')], default=2, verbose_name='payment status')),
                ('author_submission', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='APC', to='SubmissionPortal.authorsubmission')),
            ],
            options={
                'verbose_name': 'article_processing_charge',
                'verbose_name_plural': 'article_processing_charges',
                'db_table': 'article_processing_charges',
                'ordering': ['-created_at'],
            },
        ),
    ]
