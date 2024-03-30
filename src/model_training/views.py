from uuid import UUID
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from model_training.models import NeuralNetworkType, TrainedNeuralNetwork
from model_training.training_task_runners import DeepLabCutTrainingTaskRunner
from train_datasets_manager.models import TrainDataset
from utils.microservices.sleap_microservice import SLEAPMicroservice
from .forms import DeeplabcutNetworkTrainingForm, SLEAPNetworkTrainingForm


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
            return redirect(reverse("network_training:list_trained_networks"))

    ctx = {
        "form": form,
    }
    return render(request, "model_training/start_model_training.html", ctx)

@login_required
def start_sleap_network_training(request: HttpRequest):
    form = SLEAPNetworkTrainingForm(request.POST or None)
    user_datasets = request.user.train_datasets.all()
    form.fields['dataset'].choices = [(ds.pk, ds.name) for ds in user_datasets]
    if request.method == "POST":
        if form.is_valid():
            ds_id = form.cleaned_data["dataset"]
            ds = get_object_or_404(TrainDataset, pk=ds_id, user=request.user)
            response = SLEAPMicroservice().send_train_network_request(ds.file.path, form.cleaned_data)
            if response.status_code == 200:
                nn = TrainedNeuralNetwork()
                nn.name = form.cleaned_data["trained_network_name"]
                nn.file_path = response.json()["model_uid"]
                nn.train_dataset = ds
                nn.neural_network_type = NeuralNetworkType.objects.get(name="SLEAP")
                nn.user = request.user
                nn.save()
                return redirect(reverse("network_training:detail_trained_network", kwargs={"id": nn.pk}))
            return redirect(reverse("network_training:list_trained_networks"))
    ctx = {
        "form": form,
    }
    return render(request, "model_training/start_sleap_model_training.html", ctx)

@login_required
def get_model_training_stats(request: HttpRequest, model_id: int):
    model = get_object_or_404(TrainedNeuralNetwork, pk=model_id, user=request.user)
    response = SLEAPMicroservice().send_learning_stats_request(UUID(model.file_path))
    return JsonResponse(response.json())

@login_required
def detail_trained_network_view(request: HttpRequest, id: int):
    net = get_object_or_404(TrainedNeuralNetwork, pk=id, user=request.user)
    return render(request, "model_training/detail.html", {"net": net})

@login_required
def list_trained_networks_view(request: HttpRequest):
    networks = TrainedNeuralNetwork.objects.filter(user=request.user)
    return render(request, "model_training/list.html", {"networks": networks})