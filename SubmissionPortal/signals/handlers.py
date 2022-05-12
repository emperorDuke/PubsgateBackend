import os
from pathlib import Path
from docx2pdf import convert

from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save

from ..models import SubmissionFile


@receiver(post_delete, sender=SubmissionFile)
def delete_file(sender, instance, *args, **kwargs):
    file_path = instance.file.path

    if os.path.isfile(file_path):
        os.remove(file_path)


@receiver(post_save, sender=SubmissionFile)
def covert_to_pdf(sender, instance, created, *args, **kwargs):
    file_path = instance.file.path
    file_name = instance.file.name
    ext = Path(file_path).suffix

    if created and (ext == "docx" or ext == "doc"):
        path = Path(file_path).resolve().parents[0]
        new_path = Path(path).touch("{0}_convert.pdf".format(file_name))
        convert(file_path, new_path)
