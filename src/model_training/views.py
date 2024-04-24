from uuid import UUID
from django import forms
from django.http import HttpRequest, HttpResponseNotFound, HttpResponseServerError, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from requests import ConnectionError
from model_training.error_responses import JSONHttpErrorResponse
from model_training.models import NeuralNetwork, NeuralNetworkType, SLEAPNeuralNetwork, DLCNeuralNetwork
from train_datasets_manager.models import TrainDataset
from utils.microservices.dlc_microservice import DLC_MICROSERVICE
from utils.microservices.exceptions import RequestSendingError
from utils.microservices.microservice import Microservice
from utils.microservices.sleap_microservice import SLEAP_MICROSERVICE
from .forms import DeeplabcutNetworkTrainingForm, SLEAPNetworkTrainingForm


def base_network_training_view(request: HttpRequest, form_class: type[forms.ModelForm], microservice: Microservice, template: str):
    form = form_class(request.POST or None)
    user_datasets = request.user.train_datasets.all()
    form.fields['dataset'].choices = [(ds.pk, ds.name) for ds in user_datasets]
    if request.method == "POST":
        if form.is_valid():
            ds_id = form.cleaned_data["dataset"]
            ds = get_object_or_404(TrainDataset, pk=ds_id, user=request.user)
            try:
                response = microservice.send_train_network_request(ds.file.path, form.cleaned_data)
                if response.status_code == 200:
                    nn: NeuralNetwork = form.save(False)
                    nn.user = request.user
                    nn.train_dataset = ds
                    nn.model_uid = response.json()["model_uid"]
                    nn.save()
                    return redirect(nn.get_absolute_url())
                raise RequestSendingError(f"Response didn't return error code 200. Response: {response.text}")
            except ConnectionError:
                print(f"Can't connect to the {microservice.__class__.__name__} microservice")
            except Exception as e:
                print(e)
            form.add_error(None, "Something went wrong when sending request to train the model. Try again later.")
    ctx = {
        "form": form,
    }
    return render(request, template, ctx)

@login_required
def start_dlc_network_training(request: HttpRequest):
    return base_network_training_view(request, DeeplabcutNetworkTrainingForm, DLC_MICROSERVICE, "model_training/start_model_training.html")

@login_required
def start_sleap_network_training(request: HttpRequest):
    return base_network_training_view(request, SLEAPNetworkTrainingForm, SLEAP_MICROSERVICE, "model_training/start_sleap_model_training.html")

@login_required
def get_model_training_stats(request: HttpRequest, neural_network_type: str, model_id: int):
    if neural_network_type == NeuralNetworkType.SLEAP:
        model = get_object_or_404(SLEAPNeuralNetwork, pk=model_id, user=request.user)
        microservice = SLEAP_MICROSERVICE
    elif neural_network_type == NeuralNetworkType.DLC:
        model = get_object_or_404(DLCNeuralNetwork, pk=model_id, user=request.user)
        microservice = DLC_MICROSERVICE
    else:
        return JSONHttpErrorResponse(HttpResponseNotFound(f"No neural network type {neural_network_type}"))
    model_uid = UUID(model.model_uid)
    try:
        response = microservice.send_learning_stats_request(model_uid)
        return JsonResponse(response.json())
    except ConnectionError:
        print(f"Can't connect to the {microservice.__class__.__name__} microservice")
    except Exception as e:
        print(e)
    return JSONHttpErrorResponse(HttpResponseServerError(f"Something went wrong during the request. Try again later"))

@login_required
def detail_trained_network_view(request: HttpRequest, neural_network_type: str, id: int):
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
    sleap_networks = list(SLEAPNeuralNetwork.objects.filter(user=request.user))
    dlc_networks = list(DLCNeuralNetwork.objects.filter(user=request.user))
    networks = sorted(sleap_networks + dlc_networks, key=lambda x: x.started_training_at, reverse=True)
    return render(request, "model_training/list.html", {"networks": networks})

@login_required
def delete_trained_network_view(request: HttpRequest, neural_network_type: str, id: int):
    if neural_network_type == NeuralNetworkType.SLEAP:
        nn_cls = SLEAPNeuralNetwork
    elif neural_network_type == NeuralNetworkType.DLC:
        nn_cls = DLCNeuralNetwork
    else:
        return HttpResponseNotFound(f"No neural network type {neural_network_type}")
    network = get_object_or_404(nn_cls, pk=id, user=request.user)
    if request.method == "POST":
        network.delete()
        return redirect("network_training:list_trained_networks")
    return render(request, "model_training/delete.html", {"net": network})