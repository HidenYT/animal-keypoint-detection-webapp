from django import forms


class RunTrainedNetworkForm(forms.Form):
    trained_network = forms.ChoiceField(label="Обученная нейросеть")
    video = forms.ChoiceField(label="Видео")