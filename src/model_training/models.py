from abc import ABC, abstractmethod
from datetime import datetime
from django.db import models
from django.urls import reverse
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
    '''Помимо перечисленных полей каждая нейронная сеть также должна обладать полямиЖ
- train_dataset = models.ForeignKey(TrainDataset, on_delete=models.DO_NOTHING)
- user = models.ForeignKey(User, on_delete=models.CASCADE)'''

    ORDER_BY_OPTIONS = [
        'neural_network_type',
        'name',
        'started_training_at',
        'finished_training_at',
        'test_fraction',
        'num_epochs'
    ]
    ORDER_BY_OPTIONS += [f"-{opt}" for opt in ORDER_BY_OPTIONS]

    neural_network_type = models.CharField(choices=NeuralNetworkType.ALL_TYPES)
    name = models.CharField(max_length=200, verbose_name="Название")
    model_uid = models.CharField(max_length=500)
    started_training_at = models.DateTimeField(default=datetime.now)
    finished_training_at = models.DateTimeField(null=True, blank=True)
    
    # Общие для всех параметры обучения
    test_fraction = models.FloatField(validators=[MinValueValidator(0), less_1], verbose_name="Доля тестовых данных")
    num_epochs = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Количество эпох")

    train_dataset: models.ForeignKey
    user: models.ForeignKey

    class Meta:
        abstract = True
    
    def get_absolute_url(self) -> str:
        raise NotImplementedError("Abstract method")

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
        ('efficientnetb0', 'efficientnetb0'), ('efficientnetb1', 'efficientnetb1'), ('efficientnetb2', 'efficientnetb2'), ('efficientnetb3', 'efficientnetb3'), ('efficientnetb4', 'efficientnetb4'), ('efficientnetb5', 'efficientnetb5'),
        ('efficientnetb6', 'efficientnetb6'), ('efficientnetb7', 'efficientnetb7')
    ]
    neural_network_type = models.CharField(default=NeuralNetworkType.SLEAP)

    learning_rate = models.FloatField(validators=[greater_0])
    backbone_model = models.CharField(choices=BACKBONE_MODELS, verbose_name="Архитектура нейросети")
    pretrained_encoder = models.CharField(choices=PRETRAINED_ENCODERS, null=True, blank=True, verbose_name="Архитектура предобученной нейросети")
    heads_sigma = models.FloatField(validators=[greater_0], verbose_name="Размах нормального распределения вокруг ключевой точки")
    heads_output_stride = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Шаг в выходном слое")

    train_dataset = models.ForeignKey(TrainDataset, on_delete=models.CASCADE, related_name='sleap_neural_networks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sleap_neural_networks')

    def get_absolute_url(self) -> str:
        return reverse("network_training:detail_trained_network", kwargs={"id": self.pk, "neural_network_type": NeuralNetworkType.SLEAP})

class DLCNeuralNetwork(NeuralNetwork):
    DLC_NET_TYPES = [
        ("resnet_50", "ResNet 50"),
        ("resnet_101", "ResNet 101"),
        ("resnet_152", "ResNet 152"),
        ("mobilenet_v2_1.0", "MobileNet v2-1.0"),
        ("mobilenet_v2_0.75", "MobileNet v2-0.75"),
        ("mobilenet_v2_0.5", "MobileNet v2-0.5"),
        ("mobilenet_v2_0.35", "MobileNet v2-0.35"),
        ("efficientnet-b0", "EfficientNet b0"),
        ("efficientnet-b1", "EfficientNet b1"),
        ("efficientnet-b2", "EfficientNet b2"),
        ("efficientnet-b3", "EfficientNet b3"),
        ("efficientnet-b4", "EfficientNet b4"),
        ("efficientnet-b5", "EfficientNet b5"),
        ("efficientnet-b6", "EfficientNet b6"),
    ]

    neural_network_type = models.CharField(default=NeuralNetworkType.DLC)

    backbone_model = models.CharField(choices=DLC_NET_TYPES, verbose_name="Архитектура нейросети")

    train_dataset = models.ForeignKey(TrainDataset, on_delete=models.CASCADE, related_name='dlc_neural_networks', verbose_name="Датасет")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dlc_neural_networks')

    def get_absolute_url(self) -> str:
        return reverse("network_training:detail_trained_network", kwargs={"id": self.pk, "neural_network_type": NeuralNetworkType.DLC})