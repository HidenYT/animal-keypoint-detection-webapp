from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from sklearn import neural_network
from model_inference.forms import RunTrainedNetworkForm
from model_inference.inference_task_runners import DLCInferenceTaskRunner
from model_inference.models import InferredKeypoints
from model_training.models import NeuralNetworkType, TrainedNeuralNetwork
from video_manager.models import InferenceVideo


@login_required
def start_dlc_network_inference_view(request: HttpRequest):
    form = RunTrainedNetworkForm(request.POST or None)
    form.fields["trained_network"].choices = [
        (net.id, net.name) for net in TrainedNeuralNetwork.objects.filter(user=request.user, neural_network_type__name=NeuralNetworkType.DeepLabCut)
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
def detail_inference_results_view(request: HttpRequest, id: int):
    kps = get_object_or_404(InferredKeypoints, user=request.user, pk=id)
    return render(request, "model_inference/detail.html", {"kps": kps})

@login_required
def list_inference_results_view(request: HttpRequest):
    results = request.user.inferred_keypoints_set.all()
    return render(request, "model_inference/list.html", {"results": results})