# Generated by Django 4.0.3 on 2022-05-17 23:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('PeerReviewPortal', '0001_initial'),
        ('Journals', '0001_initial'),
        ('SubmissionPortal', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='journalsubmission',
            name='author_submission',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='journal_submission', to='SubmissionPortal.authorsubmission'),
        ),
        migrations.AddField(
            model_name='journalsubmission',
            name='journal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='submissions', to='Journals.journal'),
        ),
        migrations.AddField(
            model_name='journalsubmission',
            name='reviewers',
            field=models.ManyToManyField(related_name='submissions', to='Journals.reviewer'),
        ),
        migrations.AddField(
            model_name='editorreport',
            name='editor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='Journals.editor'),
        ),
        migrations.AddField(
            model_name='editorreport',
            name='journal_submission',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='editors_reports', to='PeerReviewPortal.journalsubmission'),
        ),
        migrations.AddConstraint(
            model_name='reviewerreportsection',
            constraint=models.UniqueConstraint(fields=('report', 'section'), name='unique_report_section'),
        ),
        migrations.AddConstraint(
            model_name='reviewerreport',
            constraint=models.UniqueConstraint(fields=('reviewer', 'journal_submission'), name='unique_reviewer_report'),
        ),
        migrations.AddConstraint(
            model_name='editorreport',
            constraint=models.UniqueConstraint(fields=('detail', 'editor', 'journal_submission'), name='unique_editor_report'),
        ),
    ]
