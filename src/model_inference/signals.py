from django.dispatch import receiver
from django.db import models
from .models import LabeledVideo
import os


@receiver(models.signals.post_delete, sender=LabeledVideo)
def auto_delete_file_on_delete(sender, instance: LabeledVideo, **kwargs):
    if os.path.isfile(instance.file_path):
        try:
            os.remove(instance.file_path)
        except:
            print("didn't manage to remove a file")