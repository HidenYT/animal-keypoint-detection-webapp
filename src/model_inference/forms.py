from django import forms


class RunTrainedNetworkForm(forms.Form):
    trained_network = forms.ChoiceField()
    video = forms.ChoiceField()