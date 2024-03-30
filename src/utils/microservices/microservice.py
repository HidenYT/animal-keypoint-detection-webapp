from abc import ABC, abstractmethod
import os
from typing import Any
import base64
from uuid import UUID
import requests
from urllib.parse import urljoin


class Microservice(ABC):
    @abstractmethod
    def send_train_network_request(self, dataset_path: str, training_config: dict[str, Any]) -> int:
        pass

    @abstractmethod
    def send_learning_stats_request(self, model_uid: UUID) -> int:
        pass

    @abstractmethod
    def send_video_inference_request(self, video_path: str, model_uid: UUID) -> int:
        pass

    @abstractmethod
    def send_inference_results_request(self, results_id: int) -> int:
        pass


class DefaultMicroservice(Microservice):

    MICROSERVICE_URL: str
    
    def send_train_network_request(self, dataset_path: str, training_config: dict[str, Any]) -> int:
        with open(dataset_path, "rb") as f:
            dataset_base64 = base64.b64encode(f.read()).decode()
        json = {
            "training_dataset": dataset_base64,
            "training_config": training_config,
        }
        response = requests.request(
            method="POST",
            url=urljoin(self.MICROSERVICE_URL, "api/train-network"),
            json=json,
        )
        return response.status_code
    
    def send_learning_stats_request(self, model_uid: UUID) -> int:
        response = requests.request(
            method="GET",
            url=urljoin(self.MICROSERVICE_URL, "api/learning-stats"),
            json={
                "model_uid": str(model_uid)
            },
        )
        return response.status_code
    
    def send_video_inference_request(self, video_path: str, model_uid: UUID) -> int:
        with open(video_path, "rb") as f:
            video_base64 = base64.b64encode(f.read()).decode()
        json = {
            "video_base64": video_base64,
            "file_name": os.path.basename(video_path),
            "model_uid": str(model_uid),
        }
        response = requests.request(
            method="POST",
            url=urljoin(self.MICROSERVICE_URL, "api/video-inference"),
            json=json,
        )
        return response.status_code
    
    def send_inference_results_request(self, results_id: int) -> int:
        response = requests.request(
            method="GET",
            url=urljoin(self.MICROSERVICE_URL, "api/inference-results"),
            json={
                "results_id": results_id,
            },
        )
        return response.status_code