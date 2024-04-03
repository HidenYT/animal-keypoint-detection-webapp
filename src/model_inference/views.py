from datetime import datetime
import json
from uuid import UUID
from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from model_inference.forms import RunTrainedNetworkForm
from model_inference.inference_task_runners import DLCInferenceTaskRunner
from model_inference.models import InferredKeypoints
from model_training.models import NeuralNetworkType, TrainedNeuralNetwork
from utils.check_token import check_token
from utils.microservices.sleap_microservice import SLEAP_MICROSERVICE
from video_manager.models import InferenceVideo


@login_required
def start_dlc_network_inference_view(request: HttpRequest):
    form = RunTrainedNetworkForm(request.POST or None)
    form.fields["trained_network"].choices = [
        (net.id, net.name) 
        for net in 
        TrainedNeuralNetwork.objects.filter(
            user=request.user, 
            neural_network_type__name=NeuralNetworkType.DeepLabCut
        )
    ]
    form.fields["video"].choices = [
        (video.id, video.name) for video in request.user.inference_videos.all()
    ]
    if request.method == "POST":
        if form.is_valid():
            get_object_or_404(TrainedNeuralNetwork, 
                              user=request.user, 
                              pk=form.cleaned_data['trained_network'], 
                              neural_network_type__name=NeuralNetworkType.DeepLabCut)
            get_object_or_404(InferenceVideo, 
                              user=request.user, 
                              pk=form.cleaned_data['video'])
            runner = DLCInferenceTaskRunner(request.user.pk, 
                                            form.cleaned_data['trained_network'], 
                                            form.cleaned_data['video'])
            runner.start_inference()
    return render(request, "model_inference/run_network.html", {"form": form})

@login_required
def start_sleap_network_inference_view(request: HttpRequest):
    form = RunTrainedNetworkForm(request.POST or None)
    form.fields["trained_network"].choices = [
        (net.id, net.name) 
        for net in 
        TrainedNeuralNetwork.objects.filter(
            user=request.user, 
            neural_network_type__name=NeuralNetworkType.SLEAP
        )
    ]
    form.fields["video"].choices = [
        (video.id, video.name) for video in request.user.inference_videos.all()
    ]
    if request.method == "POST":
        if form.is_valid():
            net = get_object_or_404(TrainedNeuralNetwork, 
                              user=request.user, 
                              pk=form.cleaned_data['trained_network'], 
                              neural_network_type__name=NeuralNetworkType.SLEAP)
            video = get_object_or_404(InferenceVideo, 
                              user=request.user, 
                              pk=form.cleaned_data['video'])
            response = SLEAP_MICROSERVICE.send_video_inference_request(
                video.file.path,
                UUID(net.file_path)
            )
            if response.status_code == 200:
                response = response.json()
                kps = InferredKeypoints.objects.create(
                    results_id=response["results_id"],
                    trained_neural_network=net,
                    user=request.user,
                    inference_video=video,
                )
                return redirect('network_inference:detail_inference_results', id=kps.pk)
            raise Exception("Response didn't return 200 status code: %s" % response.content.decode())
    return render(request, "model_inference/run_network.html", {"form": form})

@login_required
def detail_inference_results_view(request: HttpRequest, id: int):
    kps = get_object_or_404(InferredKeypoints, user=request.user, pk=id)
    return render(request, "model_inference/detail.html", {"kps": kps})

@login_required
def list_inference_results_view(request: HttpRequest):
    results = request.user.inferred_keypoints_set.order_by("-started_inference_at").all()
    return render(request, "model_inference/list.html", {"results": results})

@check_token
@csrf_exempt
def inference_results_view(request: HttpRequest):
    try:
        results = json.loads(request.body)
        sender = results["sender"]
        for inferred_kps in results["results"]:
            id = inferred_kps["id"]
            kps = inferred_kps["keypoints"]
            obj = InferredKeypoints.objects.get(
                trained_neural_network__neural_network_type__name=sender, 
                results_id=id
            )
            obj.keypoints = kps
            obj.finished_inference_at = datetime.now()
            obj.save()
    except:
        return HttpResponseBadRequest("You must provide a valid json of the inferred keypoints.")
    return JsonResponse({"response": "success"})