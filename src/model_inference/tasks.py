from core import celery_app
from model_inference.inference_runners.dlc_inference_runner import DLCInferenceRunner
from model_inference.models import InferredKeypoints
from model_training.models import TrainedNeuralNetwork
from video_manager.models import InferenceVideo
from django.contrib.auth.models import User


@celery_app.task
def dlc_inferrence(user_id: int, trained_network_id: int, video_id: int):
    net = TrainedNeuralNetwork.objects.get(pk=trained_network_id)
    video = InferenceVideo.objects.get(pk=video_id)
    user = User.objects.get(pk=user_id)

    DLCInferenceRunner(user, net, video).run_inference()
    

