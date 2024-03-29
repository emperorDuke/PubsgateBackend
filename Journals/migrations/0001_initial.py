# Generated by Django 4.0.3 on 2022-09-18 13:31

import Journals.models.journals
from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Editor',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('affiliation', models.CharField(blank=True, max_length=300, null=True, verbose_name='affiliation')),
                ('phone_number', models.CharField(blank=True, max_length=255, null=True, verbose_name='phone number')),
                ('specialisation', models.CharField(blank=True, max_length=255, null=True, verbose_name='specialisation')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='started at')),
            ],
            options={
                'verbose_name': 'editor',
                'verbose_name_plural': 'editors',
                'db_table': 'editors',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='EditorialMember',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('role', models.IntegerField(blank=True, choices=[(1, 'Editor in chief'), (2, 'Line editor'), (3, 'Copy editor'), (4, 'Section editor')], default=4, verbose_name='role')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('access_login', models.CharField(max_length=255, verbose_name='access_login')),
            ],
            options={
                'verbose_name': 'editorial member',
                'verbose_name_plural': 'editorial members',
                'db_table': 'journal_editorial_members',
            },
        ),
        migrations.CreateModel(
            name='EditorJournalActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(verbose_name='last_login')),
                ('started_at', models.DateTimeField(auto_now_add=True, verbose_name='started_at')),
            ],
            options={
                'verbose_name': 'editor journal activity',
                'verbose_name_plural': 'editor journal activities',
                'db_table': 'EditorJournalActivies',
                'ordering': ['-last_login'],
            },
        ),
        migrations.CreateModel(
            name='Journal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='name')),
                ('slug', models.SlugField(max_length=255, unique=True, verbose_name='slug')),
                ('access_options', models.IntegerField(choices=[(1, 'open-access'), (2, 'partial-access')], default=1, verbose_name='access_model')),
                ('issn', models.CharField(max_length=255, verbose_name='ISSN')),
                ('publication_start_date', models.DateField(default=django.utils.timezone.now, verbose_name='publication_start_date')),
                ('publication_frequency', models.IntegerField(choices=[(1, 'annually'), (2, 'bi-annually'), (3, 'tri-annually'), (4, 'quarterly')], default=2, verbose_name='publication_frequency')),
                ('iso_abbreviation', models.CharField(default=None, max_length=255, null=True, verbose_name='ISO_abbreviation')),
                ('logo', models.ImageField(blank=True, null=True, upload_to=Journals.models.journals.Journal.upload_to, verbose_name='logo')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'journal',
                'verbose_name_plural': 'journals',
                'db_table': 'journals',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='JournalBanner',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('file', models.ImageField(upload_to=Journals.models.journals.JournalBanner.upload_to, verbose_name='file')),
                ('section', models.IntegerField(choices=[(1, 'main'), (2, 'middle'), (3, 'bottom')], default=1, verbose_name='section')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
            ],
            options={
                'verbose_name': 'journal_banner',
                'verbose_name_plural': 'journal_banners',
                'db_table': 'journal_banners',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='JournalInformation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('content', models.JSONField(blank=True, null=True, verbose_name='content')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
            ],
            options={
                'verbose_name': 'journal information',
                'verbose_name_plural': 'journal informations',
                'db_table': 'journal_informations',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='JournalPermission',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('code_name', models.CharField(max_length=255, verbose_name='code_name')),
                ('label', models.CharField(max_length=255, verbose_name='label')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
            ],
            options={
                'verbose_name': 'journal permission',
                'verbose_name_plural': 'journal permissions',
                'db_table': 'journal_permissions',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='JournalReportQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=255, verbose_name='question')),
                ('hint', models.CharField(max_length=255, verbose_name='hint')),
                ('has_long_answer', models.BooleanField(default=False, verbose_name='has_long_answer')),
                ('options', models.JSONField(blank=True, null=True, verbose_name='options')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
            ],
            options={
                'verbose_name': 'journal report question',
                'verbose_name_plural': 'journal report questions',
                'db_table': 'journal_report_questions',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='JournalSubjectArea',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
            ],
            options={
                'verbose_name': 'journal subject',
                'verbose_name_plural': 'journal subjects',
                'db_table': 'journal_subjects',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='JournalViewLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('ip_address', models.GenericIPAddressField(verbose_name='ip_address')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
            ],
            options={
                'verbose_name': 'journal view log',
                'verbose_name_plural': 'journal view logs',
                'db_table': 'journal_view_logs',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='JournalVolume',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('is_active', models.BooleanField(default=False, verbose_name='is_active')),
                ('added_at', models.DateTimeField(auto_now_add=True, verbose_name='added_at')),
            ],
            options={
                'verbose_name': 'journal_volume',
                'verbose_name_plural': 'journal_volumes',
                'db_table': 'journal_volumes',
                'ordering': ['-added_at'],
            },
        ),
        migrations.CreateModel(
            name='JournalVolumeIssue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('is_special', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False, verbose_name='is_active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
            ],
            options={
                'verbose_name': 'journal_volume_issue',
                'verbose_name_plural': 'journal_volume_issues',
                'db_table': 'journal_volume_issues',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='RecruitmentApplication',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('role', models.PositiveIntegerField(choices=[(1, 'editor'), (2, 'reviewer')], default=1, verbose_name='role')),
                ('status', models.IntegerField(choices=[(1, 'processing'), (2, 'accept'), (3, 'rejected'), (4, 'completed')], default=1, verbose_name='recruitment_status')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
            ],
            options={
                'verbose_name': 'recruitment application',
                'verbose_name_plural': 'recruitment applications',
                'db_table': 'recruitment_applications',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Reviewer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('is_anonymous', models.BooleanField(default=False)),
                ('affiliation', models.CharField(max_length=255, verbose_name='affiliation')),
                ('started_at', models.DateTimeField(auto_now_add=True, verbose_name='started_at')),
                ('journals', models.ManyToManyField(related_name='reviewers', to='Journals.journal')),
            ],
            options={
                'verbose_name': 'reviewer',
                'verbose_name_plural': 'reviewers',
                'db_table': 'reviewers',
                'ordering': ['-started_at'],
            },
        ),
    ]
