# Generated by Django 4.0.3 on 2022-08-06 12:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='name')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
            ],
            options={
                'verbose_name': 'article_type',
                'verbose_name_plural': 'article_types',
                'db_table': 'article_types',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='JournalDetailType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
            ],
            options={
                'verbose_name': 'journal detail type',
                'verbose_name_plural': 'journal detail types',
                'db_table': 'journal_detail_types',
                'ordering': ('created_at',),
            },
        ),
        migrations.CreateModel(
            name='SubjectDiscipline',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='discipline')),
                ('slug', models.CharField(max_length=255, unique=True, verbose_name='slug')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'subject_discipline',
                'verbose_name_plural': 'subject_disciplines',
                'db_table': 'subject_displicines',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='TermOfService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section', models.CharField(max_length=255, verbose_name='section')),
                ('question', models.CharField(max_length=255, verbose_name='question')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('group', models.CharField(blank=True, max_length=255, null=True, verbose_name='group')),
                ('discipline', models.ManyToManyField(related_name='terms', to='Cores.subjectdiscipline')),
            ],
            options={
                'verbose_name': 'term_of_service',
                'verbose_name_plural': 'terms_of_service',
                'db_table': 'terms_of_services',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='ArticleTypeSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('article_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='Cores.articletype')),
            ],
            options={
                'verbose_name': 'article_type_section',
                'verbose_name_plural': 'article_type_sections',
                'db_table': 'article_type_sections',
                'ordering': ('created_at',),
            },
        ),
        migrations.AddConstraint(
            model_name='articletypesection',
            constraint=models.UniqueConstraint(fields=('name', 'article_type'), name='unique_sections'),
        ),
    ]
