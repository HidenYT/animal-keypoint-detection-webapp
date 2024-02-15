from abc import ABC, abstractmethod
from django.contrib.auth.models import User
from model_training.models import TrainedNeuralNetwork
from video_manager.models import InferenceVideo


class InferenceRunner(ABC):
    def __init__(self, user: User, trained_net: TrainedNeuralNetwork, video: InferenceVideo) -> None:
        super().__init__()
        self._user = user
        self._trained_net = trained_net
        self._video = video

    @abstractmethod
    def run_inference(self):
        pass