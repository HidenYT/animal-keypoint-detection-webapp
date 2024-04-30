from datetime import datetime
import os
from amqp import NotFound
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django_sendfile import sendfile
from django.urls import reverse

from model_inference.models import InferredKeypoints
from model_training.models import NeuralNetwork
from utils.list_sort import get_sorted_objects

from .forms import DatasetEditForm, DatasetUploadForm
from .models import TrainDataset

def get_dataset(request: HttpRequest, id: int) -> TrainDataset:
    return get_object_or_404(TrainDataset, pk=id, user=request.user)

@login_required
def list_train_datasets_view(request: HttpRequest):
    datasets = TrainDataset.objects.filter(user=request.user)
    order_datasets_by = request.GET.get("order-datasets-by", "-created_at")
    if order_datasets_by not in TrainDataset.ORDER_BY_OPTIONS:
        order_datasets_by = '-created_at'
    datasets = get_sorted_objects(order_datasets_by, list(datasets))
    ctx = {
        "datasets": datasets,
    }
    return render(request, 'train_datasets_manager/list.html', ctx)

@login_required
def upload_train_dataset_view(request: HttpRequest):
    form = DatasetUploadForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            dataset = TrainDataset()
            dataset.name = form.cleaned_data['name']
            dataset.description = form.cleaned_data['description']
            dataset.user = request.user
            dataset.file = request.FILES['file']
            dataset.save()
            return redirect(reverse('train_datasets_manager:list_train_datasets'))
    return render(request, 'train_datasets_manager/upload.html', {"form": form})

@login_required
def edit_train_dataset_view(request: HttpRequest, id: int):
    dataset = get_dataset(request, id)
    form = DatasetEditForm(request.POST or None, request.FILES or None, instance=dataset)
    if request.method == 'POST':
        if form.is_valid():
            dataset.name = form.cleaned_data['name']
            dataset.description = form.cleaned_data['description']
            if request.FILES:
                dataset.file = request.FILES['file']
            dataset.updated_at = datetime.now()
            dataset.save()
            return redirect(reverse('train_datasets_manager:list_train_datasets'))
    return render(request, 'train_datasets_manager/edit.html', {"form": form, "dataset": dataset})

@login_required
def delete_train_dataset_view(request: HttpRequest, id: int):
    dataset = get_dataset(request, id)
    if request.method == 'POST':
        dataset.delete()
        return redirect(reverse("train_datasets_manager:list_train_datasets"))
    order_networks_by = request.GET.get("order-nets-by", "-started_training_at")
    if order_networks_by not in NeuralNetwork.ORDER_BY_OPTIONS:
        order_networks_by = '-started_training_at'
    order_results_by = request.GET.get("order-results-by", "-started_inference_at")
    if order_results_by not in InferredKeypoints.ORDER_BY_OPTIONS:
        order_results_by = '-started_inference_at'
    networks = get_sorted_objects(order_networks_by, 
                                   list(dataset.sleap_neural_networks.all()) + 
                                   list(dataset.dlc_neural_networks.all())
                                   )
    analysis_results = get_sorted_objects(order_results_by,
            [res for net in networks for res in net.inferred_keypoints_set.all()]                   
    )
    ctx = {
        "dataset": dataset,
        "networks": networks,
        'analysis_results': analysis_results,
    }
    return render(request, "train_datasets_manager/delete.html", ctx)

@login_required
def train_dataset_data_view(request: HttpRequest, id: int):
    dataset = get_dataset(request, id)
    _, ext = os.path.splitext(dataset.file.path)
    return sendfile(request, 
                    dataset.file.path, 
                    attachment=True, 
                    attachment_filename=f'Train dataset {dataset.name}{ext}',
                    )