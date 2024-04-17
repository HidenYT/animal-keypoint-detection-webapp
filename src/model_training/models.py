from datetime import datetime
from django.db import models
from train_datasets_manager.models import TrainDataset
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

from utils.validators import greater_0, less_1

class NeuralNetworkType:
    SLEAP = "SLEAP"
    DLC = "DLC"

    ALL_TYPES = [
        (SLEAP, SLEAP),
        (DLC, DLC),
    ]

class NeuralNetwork(models.Model):

    neural_network_type = models.CharField(choices=NeuralNetworkType.ALL_TYPES)
    name = models.CharField(max_length=200)
    model_uid = models.CharField(max_length=500)
    started_training_at = models.DateTimeField(default=datetime.now)
    finished_training_at = models.DateTimeField(null=True, blank=True)
    
    # Общие для всех параметры обучения
    test_fraction = models.FloatField(validators=[MinValueValidator(0), less_1])
    num_epochs = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        abstract = True

class SLEAPNeuralNetwork(NeuralNetwork):
    BACKBONE_MODELS = [
        ("unet", "UNet"), 
        ("leap", "LEAP"), 
        ("hourglass", "Hourglass"), 
        ("resnet", "ResNet"), 
        ("pretrained_encoder", "Pretrained encoder"),
    ]

    PRETRAINED_ENCODERS = [
        ('vgg16', 'vgg16'), ('vgg19', 'vgg19'), 
        ('resnet18', 'resnet18'), ('resnet34', 'resnet34'), ('resnet50', 'resnet50'), ('resnet101', 'resnet101'), ('resnet152', 'resnet152'), 
        ('resnext50', 'resnext50'), ('resnext101', 'resnext101'), 
        ('inceptionv3', 'inceptionv3'), ('inceptionresnetv2', 'inceptionresnetv2'), 
        ('densenet121', 'densenet121'), ('densenet169', 'densenet169'), ('densenet201', 'densenet201'), 
        ('seresnet18', 'seresnet18'), ('seresnet34', 'seresnet34'), ('seresnet50', 'seresnet50'), ('seresnet101', 'seresnet101'), ('seresnet152', 'seresnet152'), 
        ('seresnext50', 'seresnext50'), ('seresnext101', 'seresnext101'), ('senet154', 'senet154'), 
        ('mobilenet', 'mobilenet'), ('mobilenetv2', 'mobilenetv2'), 
        ('efficientnetb0', 'efficientnetb0'), ('efficientnetb1', 'efficientnetb1'), ('efficientnetb2', 'efficientnetb2'), ('efficientnetb3', 'efficientnetb3'), ('efficientnetb4', 'efficientnetb4'), ('efficientnetb5', 'efficientnetb5')
    ]
    neural_network_type = models.CharField(default=NeuralNetworkType.SLEAP)

    learning_rate = models.FloatField(validators=[greater_0])
    backbone_model = models.CharField(choices=BACKBONE_MODELS)
    pretrained_encoder = models.CharField(choices=PRETRAINED_ENCODERS, null=True, blank=True)
    heads_sigma = models.FloatField(validators=[greater_0])
    heads_output_stride = models.IntegerField(validators=[MinValueValidator(1)])

    train_dataset = models.ForeignKey(TrainDataset, on_delete=models.DO_NOTHING, related_name='sleap_neural_networks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sleap_neural_networks')

class DLCNeuralNetwork(NeuralNetwork):
    DLC_NET_TYPES = [
        ("resnet_50", "ResNet 50"),
        ("resnet_101", "ResNet 101"),
        ("resnet_152", "ResNet 152"),
        ("mobilenet_v2_1.0", "MobileNet v2-1.0"),
        ("mobilenet_v2_0.75", "MobileNet v2-0.75"),
        ("mobilenet_v2_0.5", "MobileNet v2-0.5"),
        ("mobilenet_v2_0.35", "MobileNet v2-0.35"),
    ]

    neural_network_type = models.CharField(default=NeuralNetworkType.DLC)

    backbone_model = models.CharField(choices=DLC_NET_TYPES)

    train_dataset = models.ForeignKey(TrainDataset, on_delete=models.DO_NOTHING, related_name='dlc_neural_networks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dlc_neural_networks')