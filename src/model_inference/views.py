import json
from typing import Iterable
from uuid import UUID
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from model_inference.forms import RunTrainedNetworkForm
from model_inference.models import InferredKeypoints
from model_inference.tasks import generate_labeled_video_from_analysis_results
from model_training.models import DLCNeuralNetwork, NeuralNetwork, NeuralNetworkType, SLEAPNeuralNetwork
from utils.microservices.dlc_microservice import DLC_MICROSERVICE
from utils.microservices.exceptions import RequestSendingError
from utils.microservices.microservice import Microservice
from utils.microservices.sleap_microservice import SLEAP_MICROSERVICE
from video_manager.models import InferenceVideo
from requests import ConnectionError


def video_analysis_view(request: HttpRequest, network_class: type[NeuralNetwork], microservice: Microservice):
    form = RunTrainedNetworkForm(request.POST or None)
    form.fields["trained_network"].choices = [
        (net.pk, net.name) 
        for net in 
        network_class.objects.filter(user=request.user)
    ]
    form.fields["video"].choices = [
        (video.pk, video.name) for video in request.user.inference_videos.all()
    ]
    if request.method == "POST":
        if form.is_valid():
            model = get_object_or_404(
                network_class, 
                user=request.user, 
                pk=form.cleaned_data['trained_network']
            )
            video = get_object_or_404(
                InferenceVideo, 
                user=request.user, 
                pk=form.cleaned_data['video']
            )
            try:
                response = microservice.send_video_inference_request(
                    video.file.path,
                    UUID(model.model_uid),
                )
                if response.status_code == 200:
                    response = response.json()
                    kps = InferredKeypoints.objects.create(
                        results_id=response["results_id"],
                        dlc_neural_network=model,
                        user=request.user,
                        inference_video=video,
                    )
                    return redirect('network_inference:detail_inference_results', id=kps.pk)
                raise RequestSendingError(f"Response didn't return error code 200. Response: {response.text}")
            except ConnectionError:
                print(f"Can't connect to the {microservice.__class__.__name__} microservice")
            except Exception as e:
                print(e)
            form.add_error(None, "Something went wrong when sending request to analyze video. Try again later.")
    return render(request, "model_inference/run_network.html", {"form": form})

@login_required
def start_dlc_network_inference_view(request: HttpRequest):
    return video_analysis_view(request, DLCNeuralNetwork, DLC_MICROSERVICE)

@login_required
def start_sleap_network_inference_view(request: HttpRequest):
    return video_analysis_view(request, SLEAPNeuralNetwork, SLEAP_MICROSERVICE)

@login_required
def detail_inference_results_view(request: HttpRequest, id: int):
    kps = get_object_or_404(InferredKeypoints, user=request.user, pk=id)
    net_type = None
    net = None
    if kps.sleap_neural_network: 
        net_type = NeuralNetworkType.SLEAP
        net = kps.sleap_neural_network
    elif kps.dlc_neural_network: 
        net_type = NeuralNetworkType.DLC
        net = kps.dlc_neural_network
    return render(request, "model_inference/detail.html", {"kps": kps, "neural_network_type": net_type, "net": net})

@login_required
def download_inference_results_view(request: HttpRequest, id: int):
    results = get_object_or_404(InferredKeypoints, pk=id, user=request.user, keypoints__isnull=False)
    response = HttpResponse(json.dumps(results.keypoints), content_type="application/json")
    response['Content-Disposition'] = 'attachment; filename=' + f"Inference results {id}.json"
    return response

@login_required
def list_inference_results_view(request: HttpRequest):
    results: Iterable[InferredKeypoints] = request.user.inferred_keypoints_set.order_by("-started_inference_at").all()
    return render(request, "model_inference/list.html", {"results": results})

@login_required
def run_labeled_video_generation_view(request: HttpRequest, id: int):
    get_object_or_404(InferredKeypoints, pk=id, user=request.user, keypoints__isnull=False)
    generate_labeled_video_from_analysis_results.delay(id)
    return redirect("network_inference:detail_inference_results", id=id)