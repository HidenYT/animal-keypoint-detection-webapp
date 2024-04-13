from uuid import UUID
from django.http import HttpRequest, HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from model_training.models import NeuralNetworkType, TrainedNeuralNetwork
from train_datasets_manager.models import TrainDataset
from utils.microservices.dlc_microservice import DLC_MICROSERVICE
from utils.microservices.microservice import Microservice
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
                nn = TrainedNeuralNetwork.objects.create(
                    name=form.cleaned_data["trained_network_name"],
                    file_path = response.json()["model_uid"],
                    train_dataset = ds,
                    neural_network_type = NeuralNetworkType.objects.get(name=NeuralNetworkType.DeepLabCut),
                    user = request.user
                )
                return redirect(reverse("network_training:detail_trained_network", kwargs={"id": nn.pk}))
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
                nn = TrainedNeuralNetwork.objects.create(
                    name=form.cleaned_data["trained_network_name"],
                    file_path = response.json()["model_uid"],
                    train_dataset = ds,
                    neural_network_type = NeuralNetworkType.objects.get(name=NeuralNetworkType.SLEAP),
                    user = request.user
                )
                return redirect(reverse("network_training:detail_trained_network", kwargs={"id": nn.pk}))
            return redirect(reverse("network_training:list_trained_networks"))
    ctx = {
        "form": form,
    }
    return render(request, "model_training/start_sleap_model_training.html", ctx)

@login_required
def get_model_training_stats(request: HttpRequest, model_id: int):
    model = get_object_or_404(TrainedNeuralNetwork, pk=model_id, user=request.user)
    model_uid = UUID(model.file_path)
    microservice: Microservice = None
    if model.neural_network_type.name == NeuralNetworkType.SLEAP:
        microservice = SLEAP_MICROSERVICE
    elif model.neural_network_type.name == NeuralNetworkType.DeepLabCut:
        microservice = DLC_MICROSERVICE
    else:
        return HttpResponseNotFound(f"Can't use neural network with type {model.neural_network_type.name}")
    response = microservice.send_learning_stats_request(model_uid)
    return JsonResponse(response.json())

@login_required
def detail_trained_network_view(request: HttpRequest, id: int):
    net = get_object_or_404(TrainedNeuralNetwork, pk=id, user=request.user)
    info = {
        "started_training_at": net.started_training_at,
        "finished_training_at": net.finished_training_at,
    }
    if net.neural_network_type.name == NeuralNetworkType.SLEAP:
        info = SLEAP_MICROSERVICE.send_model_info_request(UUID(net.file_path)).json()
        return render(request, "model_training/sleap_detail.html", {"info": info, "net": net})
    elif net.neural_network_type.name == NeuralNetworkType.DeepLabCut:
        info = DLC_MICROSERVICE.send_model_info_request(UUID(net.file_path)).json()
        return render(request, "model_training/detail.html", {"info": info, "net": net})

@login_required
def list_trained_networks_view(request: HttpRequest):
    networks = TrainedNeuralNetwork.objects.filter(user=request.user).order_by("-started_training_at")
    return render(request, "model_training/list.html", {"networks": networks})