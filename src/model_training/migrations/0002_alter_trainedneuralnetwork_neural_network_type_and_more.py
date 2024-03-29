# Generated by Django 4.0.1 on 2024-02-12 16:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('train_datasets_manager', '0004_alter_skeleon_train_dataset_and_more'),
        ('model_training', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainedneuralnetwork',
            name='neural_network_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='trained_neural_networks', to='model_training.neuralnetworktype'),
        ),
        migrations.AlterField(
            model_name='trainedneuralnetwork',
            name='train_dataset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='trained_neural_networks', to='train_datasets_manager.traindataset'),
        ),
    ]
