# Generated by Django 4.0.1 on 2024-02-12 16:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('model_training', '0002_alter_trainedneuralnetwork_neural_network_type_and_more'),
        ('video_manager', '0004_alter_inferencevideo_description_and_more'),
        ('model_inference', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inferredkeypoints',
            name='inference_video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='inferred_keypoints_set', to='video_manager.inferencevideo'),
        ),
        migrations.AlterField(
            model_name='inferredkeypoints',
            name='trained_neural_network',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='inferred_keypoints_set', to='model_training.trainedneuralnetwork'),
        ),
    ]
