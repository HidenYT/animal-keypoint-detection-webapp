# Generated by Django 5.0 on 2024-04-30 10:17

import django.core.validators
import train_datasets_manager.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('train_datasets_manager', '0005_remove_skeletonkeypoint_skeleton_delete_skeleon_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='traindataset',
            name='file',
            field=models.FileField(upload_to=train_datasets_manager.models.train_dataset_upload_path, validators=[django.core.validators.FileExtensionValidator(['7z'])]),
        ),
    ]
