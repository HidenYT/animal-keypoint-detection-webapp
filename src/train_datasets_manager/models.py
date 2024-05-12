from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from utils.file_uploads import default_upload_path
from django.conf import settings
from django.core.validators import FileExtensionValidator

def train_dataset_upload_path(instance: "TrainDataset", filename: str) -> str:
    return default_upload_path(settings.TRAIN_DATASET_UPLOAD_DIR, instance.user, filename)

class TrainDataset(models.Model):
    ORDER_BY_OPTIONS = [
        'name',
        'created_at',
        'updated_at'
    ]
    ORDER_BY_OPTIONS += [f"-{opt}" for opt in ORDER_BY_OPTIONS]
    
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")

    file = models.FileField(upload_to=train_dataset_upload_path, 
                            validators=[FileExtensionValidator(['7z'])],
                            verbose_name="Файл")

    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(default=datetime.now)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='train_datasets')
