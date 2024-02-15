from datetime import datetime
from django.db import models
from train_datasets_manager.models import TrainDataset
from django.contrib.auth.models import User


class NeuralNetworkType(models.Model):
    DeepLabCut = "DeepLabCut"
    SLEAP = "SLEAP"
    DeepPoseKit = "DeepPoseKit"
    AlphaTracher = "AlphaTracker"

    NETWORKS = [
        DeepLabCut,
        SLEAP,
        DeepPoseKit,
        AlphaTracher,
    ]

    name = models.CharField(max_length=100)


class TrainedNeuralNetwork(models.Model):
    name = models.CharField(max_length=200)
    
    file_path = models.CharField(max_length=500)

    started_training_at = models.DateTimeField(default=datetime.now)
    finished_training_at = models.DateTimeField(null=True, blank=True)

    train_dataset = models.ForeignKey(TrainDataset, on_delete=models.DO_NOTHING, related_name='trained_neural_networks')

    neural_network_type = models.ForeignKey(NeuralNetworkType, on_delete=models.DO_NOTHING, related_name='trained_neural_networks')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trained_neural_networks')