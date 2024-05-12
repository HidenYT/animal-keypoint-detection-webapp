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
    dataset = forms.ChoiceField(label="Датасет")

    class Meta:
        model = DLCNeuralNetwork
        exclude = EXCLUDE_FIELDS


class SLEAPNetworkTrainingForm(forms.ModelForm):
    backbone_model = forms.ChoiceField(
        choices=SLEAPNeuralNetwork.BACKBONE_MODELS, 
        widget=forms.Select(attrs={"onchange": "onBackboneModelChanged();"}),
        label="Архитектура нейросети")
    dataset = forms.ChoiceField(label="Датасет")

    def clean_pretrained_encoder(self):
        if self.cleaned_data['backbone_model'] != 'pretrained_encoder': return
        if self.cleaned_data['pretrained_encoder'] is None:
            raise forms.ValidationError("You should specify a Pretrained encoder model if you choose 'Pretrained encoder' as a backbone")
        return self.cleaned_data['pretrained_encoder']

    class Meta:
        model = SLEAPNeuralNetwork
        exclude = EXCLUDE_FIELDS
        
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["learning_rate"].initial = 1e-4
        self.fields["heads_sigma"].initial = 2.5
        self.fields["heads_output_stride"].initial = 1
