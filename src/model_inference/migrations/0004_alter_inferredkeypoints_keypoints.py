# Generated by Django 4.0.1 on 2024-02-15 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model_inference', '0003_inferredkeypoints_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inferredkeypoints',
            name='keypoints',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
