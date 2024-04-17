from datetime import datetime
from django.db import models
from model_training.models import SLEAPNeuralNetwork, DLCNeuralNetwork
from video_manager.models import InferenceVideo
from django.contrib.auth.models import User


class InferredKeypoints(models.Model):
    keypoints = models.JSONField(null=True, blank=True)
    results_id = models.IntegerField()

    started_inference_at = models.DateTimeField(default=datetime.now)
    finished_inference_at = models.DateTimeField(null=True, blank=True)

    sleap_neural_network = models.ForeignKey(SLEAPNeuralNetwork, 
                                             on_delete=models.DO_NOTHING, 
                                             related_name='inferred_keypoints_set', 
                                             null=True)
    dlc_neural_network = models.ForeignKey(DLCNeuralNetwork, 
                                           on_delete=models.DO_NOTHING, 
                                           related_name='inferred_keypoints_set', 
                                           null=True)

    inference_video = models.ForeignKey(InferenceVideo, on_delete=models.DO_NOTHING, related_name='inferred_keypoints_set')
    
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