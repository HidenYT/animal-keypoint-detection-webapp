from django import forms

from model_training.models import DLCNeuralNetwork, SLEAPNeuralNetwork

EXCLUDE_FIELDS = [
    'user', 
    'started_training_at', 
    'finished_training_at', 
    'train_dataset', 
    'neural_network_type', 
    'model_uid'
]

class DeeplabcutNetworkTrainingForm(forms.ModelForm):
    dataset = forms.ChoiceField()

    class Meta:
        model = DLCNeuralNetwork
        exclude = EXCLUDE_FIELDS


class SLEAPNetworkTrainingForm(forms.ModelForm):
    backbone_model = forms.ChoiceField(
        choices=SLEAPNeuralNetwork.BACKBONE_MODELS, 
        widget=forms.Select(attrs={"onchange": "onBackboneModelChanged();"}))
    dataset = forms.ChoiceField()

    class Meta:
        model = SLEAPNeuralNetwork
        exclude = EXCLUDE_FIELDS
