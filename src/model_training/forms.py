from django import forms

def gt0(value: float):
    if value <= 0:
        raise forms.ValidationError(
            ("%(value)s is not greater than 0"),
            params={"value": value},
        )

class BaseNetworkTrainingForm(forms.Form):
    dataset = forms.ChoiceField()
    trained_network_name = forms.CharField()

class DeeplabcutNetworkTrainingForm(BaseNetworkTrainingForm):
    DLC_NET_TYPES = [
        ("resnet_50", "ResNet 50"),
        ("resnet_101", "ResNet 101"),
        ("resnet_152", "ResNet 152"),
        ("mobilenet_v2_1.0", "MobileNet v2-1.0"),
        ("mobilenet_v2_0.75", "MobileNet v2-0.75"),
        ("mobilenet_v2_0.5", "MobileNet v2-0.5"),
        ("mobilenet_v2_0.35", "MobileNet v2-0.35"),
    ]

    test_fraction = forms.FloatField(max_value=1, min_value=0)
    num_epochs = forms.IntegerField(min_value=1)
    backbone_model = forms.ChoiceField(choices=DLC_NET_TYPES)


class SLEAPNetworkTrainingForm(BaseNetworkTrainingForm):
    
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

    test_fraction = forms.FloatField(max_value=1, min_value=0)
    num_epochs = forms.IntegerField(min_value=1)
    learning_rate = forms.FloatField(validators=[gt0])
    backbone_model = forms.ChoiceField(choices=BACKBONE_MODELS, widget=forms.Select(attrs={"onchange": "onBackboneModelChanged();"}))
    pretrained_encoder = forms.ChoiceField(required=False, choices=PRETRAINED_ENCODERS)
    heads_sigma = forms.FloatField(validators=[gt0])
    heads_output_stride = forms.IntegerField(min_value=1)