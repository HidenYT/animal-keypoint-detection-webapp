from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from model_training.training_task_runners import DeepLabCutTrainingTaskRunner
from train_datasets_manager.models import TrainDataset
from .forms import DeeplabcutNetworkTrainingForm


@login_required
def start_dlc_network_training(request: HttpRequest):
    form = DeeplabcutNetworkTrainingForm(request.POST or None)
    user_datasets = request.user.train_datasets.all()
    form.fields['dataset'].choices = [(ds.pk, ds.name) for ds in user_datasets]
    if request.method == "POST":
        if form.is_valid():
            ds_id = form.cleaned_data["dataset"]
            ds = get_object_or_404(TrainDataset, pk=ds_id, user=request.user)
            trainer = DeepLabCutTrainingTaskRunner(request.user.username, ds, form.cleaned_data)
            trainer.start_training()

    ctx = {
        "form": form,
    }
    return render(request, "model_training/start_model_training.html", ctx)