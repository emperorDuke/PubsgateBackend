# Generated by Django 4.0.3 on 2022-09-18 13:31

import Contents.models
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Cores', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Manuscript',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('word_count', models.PositiveIntegerField(verbose_name='word_count')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'manuscript',
                'verbose_name_plural': 'manuscripts',
                'db_table': 'manuscripts',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ManuscriptSection',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('content', models.JSONField(verbose_name='content')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('manuscript', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='Contents.manuscript')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Cores.articletypesection')),
            ],
            options={
                'verbose_name': 'manuscript_section',
                'verbose_name_plural': 'manuscript_sections',
                'db_table': 'manuscript_sections',
                'ordering': ('created_at',),
            },
        ),
        migrations.CreateModel(
            name='ManuscriptReference',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('authors', models.JSONField(verbose_name='author')),
                ('year', models.CharField(max_length=255, verbose_name='year')),
                ('issue', models.CharField(blank=True, max_length=200, null=True, verbose_name='issue')),
                ('DOI', models.CharField(blank=True, max_length=255, null=True, verbose_name='DOI')),
                ('volume', models.CharField(blank=True, max_length=100, null=True, verbose_name='volume')),
                ('publisher', models.CharField(blank=True, max_length=255, null=True, verbose_name='publisher')),
                ('page_start', models.PositiveIntegerField(blank=True, null=True, verbose_name='page_start')),
                ('page_end', models.PositiveIntegerField(blank=True, null=True, verbose_name='page_end')),
                ('manuscript', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='references', to='Contents.manuscript')),
            ],
            options={
                'verbose_name': 'manuscript_reference',
                'verbose_name_plural': 'manuscript_references',
                'db_table': 'manuscript_references',
            },
        ),
        migrations.CreateModel(
            name='ManuscriptKeywordTag',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('tag', models.CharField(max_length=255, verbose_name='tag')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('manuscript', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='keyword_tags', to='Contents.manuscript')),
            ],
            options={
                'verbose_name': 'manuscript_keyword',
                'verbose_name_plural': 'manuscript_keywords',
                'db_table': 'manuscript_keyword_tags',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='ManuscriptFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.PositiveIntegerField(blank=True, default=1, verbose_name='version')),
                ('label_no', models.PositiveIntegerField(verbose_name='label_number')),
                ('label_on_manuscript', models.CharField(max_length=255, verbose_name='label_on_manuscript')),
                ('file_type', models.IntegerField(choices=[(1, 'table'), (2, 'figure')], default=2, verbose_name='file_type')),
                ('doc', models.FileField(blank=True, max_length=255, null=True, upload_to=Contents.models.ManuscriptFile.file_path, verbose_name='file')),
                ('image', models.ImageField(blank=True, max_length=255, null=True, upload_to=Contents.models.ManuscriptFile.file_path, verbose_name='image')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('manuscript', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='Contents.manuscript')),
            ],
            options={
                'verbose_name': 'manuscript_file',
                'verbose_name_plural': 'manuscript_files',
                'db_table': 'manuscript_files',
                'ordering': ['file_type', 'label_no'],
            },
        ),
        migrations.CreateModel(
            name='ManuscriptAuthor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255, verbose_name='first_name')),
                ('last_name', models.CharField(max_length=255, verbose_name='last_name')),
                ('email', models.EmailField(max_length=254, verbose_name='email')),
                ('affiliation', models.CharField(max_length=255, verbose_name='affiliation')),
                ('rank', models.PositiveBigIntegerField(default=1, verbose_name='rank')),
                ('is_corresponding', models.BooleanField(blank=True, default=False, verbose_name='is_corresponding')),
                ('manuscript', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authors', to='Contents.manuscript')),
            ],
            options={
                'verbose_name': 'manuscript_author',
                'verbose_name_plural': 'manuscript_authors',
                'db_table': 'manuscript_authors',
                'ordering': ('rank',),
            },
        ),
    ]
