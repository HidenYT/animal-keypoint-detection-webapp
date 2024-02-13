from django import forms


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

    network_type = forms.ChoiceField(choices=DLC_NET_TYPES)
    max_iters = forms.IntegerField(min_value=0)