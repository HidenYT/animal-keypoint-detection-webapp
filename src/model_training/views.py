from uuid import UUID
from django.http import HttpRequest, HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from model_training.models import NeuralNetworkType, SLEAPNeuralNetwork, DLCNeuralNetwork
from train_datasets_manager.models import TrainDataset
from utils.microservices.dlc_microservice import DLC_MICROSERVICE
from utils.microservices.sleap_microservice import SLEAP_MICROSERVICE
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
            response = DLC_MICROSERVICE.send_train_network_request(ds.file.path, form.cleaned_data)
            if response.status_code == 200:
                nn = DLCNeuralNetwork.objects.create(
                    name=form.cleaned_data["name"],
                    model_uid = response.json()["model_uid"],

                    test_fraction = form.cleaned_data["test_fraction"],
                    backbone_model = form.cleaned_data["backbone_model"],
                    num_epochs = form.cleaned_data["num_epochs"],

                    train_dataset = ds,
                    user = request.user,
                )
                return redirect(reverse("network_training:detail_trained_network", kwargs={"id": nn.pk, "neural_network_type": "DLC"}))
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
            response = SLEAP_MICROSERVICE.send_train_network_request(ds.file.path, form.cleaned_data)
            if response.status_code == 200:
                nn = SLEAPNeuralNetwork.objects.create(
                    name=form.cleaned_data["name"],
                    model_uid = response.json()["model_uid"],

                    test_fraction = form.cleaned_data["test_fraction"],
                    num_epochs = form.cleaned_data["num_epochs"],
                    learning_rate = form.cleaned_data["learning_rate"],
                    backbone_model = form.cleaned_data["backbone_model"],
                    pretrained_encoder = form.cleaned_data["pretrained_encoder"],
                    heads_sigma = form.cleaned_data["heads_sigma"],
                    heads_output_stride = form.cleaned_data["heads_output_stride"],

                    train_dataset = ds,
                    user = request.user,
                )
                return redirect(reverse("network_training:detail_trained_network", kwargs={"id": nn.pk, "neural_network_type": "SLEAP"}))
            return redirect(reverse("network_training:list_trained_networks"))
    ctx = {
        "form": form,
    }
    return render(request, "model_training/start_sleap_model_training.html", ctx)

@login_required
def get_model_training_stats(request: HttpRequest, neural_network_type: str, model_id: int):
    if neural_network_type == NeuralNetworkType.SLEAP:
        model = get_object_or_404(SLEAPNeuralNetwork, pk=model_id, user=request.user)
        microservice = SLEAP_MICROSERVICE
    elif neural_network_type == NeuralNetworkType.DLC:
        model = get_object_or_404(DLCNeuralNetwork, pk=model_id, user=request.user)
        microservice = DLC_MICROSERVICE
    else:
        return HttpResponseNotFound(f"No neural network type {neural_network_type}")
    model_uid = UUID(model.model_uid)
    response = microservice.send_learning_stats_request(model_uid)
    return JsonResponse(response.json())

@login_required
def detail_trained_network_view(request: HttpRequest, neural_network_type: str, id: int):
    nn_cls = None
    if neural_network_type == NeuralNetworkType.SLEAP:
        nn_cls = SLEAPNeuralNetwork
    elif neural_network_type == NeuralNetworkType.DLC:
        nn_cls = DLCNeuralNetwork
    else:
        return HttpResponseNotFound(f"No neural network type {neural_network_type}")
    net = get_object_or_404(nn_cls, pk=id, user=request.user)
    if neural_network_type == NeuralNetworkType.SLEAP:
        return render(request, "model_training/sleap_detail.html", {"net": net})
    elif neural_network_type == NeuralNetworkType.DLC:
        return render(request, "model_training/detail.html", {"net": net})

@login_required
def list_trained_networks_view(request: HttpRequest):
    sleap_networks = list(SLEAPNeuralNetwork.objects.filter(user=request.user).values())
    for net in sleap_networks:
        net["neural_network_type"] = "SLEAP"
    dlc_networks = list(DLCNeuralNetwork.objects.filter(user=request.user).values())
    for net in dlc_networks:
        net["neural_network_type"] = "DLC"
    networks = sorted(sleap_networks + dlc_networks, key=lambda x: x["started_training_at"], reverse=True)
    return render(request, "model_training/list.html", {"networks": networks})