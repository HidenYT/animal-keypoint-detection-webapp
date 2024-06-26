from datetime import datetime
from django.conf import settings
from django.db import models
from django.urls import reverse
from model_training.models import SLEAPNeuralNetwork, DLCNeuralNetwork
from utils.file_uploads import default_upload_path
from video_manager.models import InferenceVideo
from django.contrib.auth.models import User

def labeled_video_random_path(instance: "InferredKeypoints") -> str:
    return default_upload_path(settings.LABELED_VIDEOS_DIR_PATH, instance.user, instance.inference_video.file.name)

class InferredKeypoints(models.Model):
    ORDER_BY_OPTIONS = [
        "started_inference_at",
        "finished_inference_at",
    ]
    ORDER_BY_OPTIONS += [f"-{opt}" for opt in ORDER_BY_OPTIONS]

    keypoints = models.JSONField(null=True, blank=True)
    results_id = models.IntegerField()

    started_inference_at = models.DateTimeField(default=datetime.now)
    finished_inference_at = models.DateTimeField(null=True, blank=True)

    sleap_neural_network = models.ForeignKey(SLEAPNeuralNetwork, 
                                             on_delete=models.CASCADE, 
                                             related_name='inferred_keypoints_set', 
                                             null=True)
    dlc_neural_network = models.ForeignKey(DLCNeuralNetwork, 
                                           on_delete=models.CASCADE, 
                                           related_name='inferred_keypoints_set', 
                                           null=True)

    inference_video = models.ForeignKey(InferenceVideo, on_delete=models.CASCADE, related_name='inferred_keypoints_set')
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inferred_keypoints_set')

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=
                (
                    models.Q(sleap_neural_network__isnull=True) |
                    models.Q(dlc_neural_network__isnull=True)
                ) & (
                    models.Q(sleap_neural_network__isnull=False) |
                    models.Q(dlc_neural_network__isnull=False)
                ) 
                ,
                name="only_one_neural_network"
            )
        ]
    
    def get_absolute_url(self):
        return reverse("network_inference:detail_inference_results", kwargs={"id": self.pk})

class LabeledVideo(models.Model):
    analysis_results = models.OneToOneField(InferredKeypoints, on_delete=models.CASCADE, related_name="labeled_video")
    started_production_at = models.DateTimeField(default=datetime.now)
    finished_production_at = models.DateTimeField(null=True, blank=True)
    file_path = models.CharField()
