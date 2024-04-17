from datetime import datetime
from typing import Literal, Type
from requests import Response

from model_inference.models import InferredKeypoints
from model_training.models import DLCNeuralNetwork, NeuralNetworkType, SLEAPNeuralNetwork

def process_video_analysis_results_response(response: Response, neural_network_type_name: str):
    if response.status_code != 200: 
        print(f"{neural_network_type_name} inference results error: {response.json()}")
        return
    for result in response.json():
        if result["keypoints"] is None: continue
        if neural_network_type_name == NeuralNetworkType.SLEAP:
            kps = InferredKeypoints.objects.get(
                results_id=result["id"], 
                sleap_neural_network__isnull=False
            )
        elif neural_network_type_name == NeuralNetworkType.DLC:
            kps = InferredKeypoints.objects.get(
                results_id=result["id"], 
                dlc_neural_network__isnull=False
            )
        kps.keypoints = result["keypoints"]
        kps.finished_inference_at = datetime.now()
        kps.save()

def process_finished_training_at_response(response: Response, neural_network_type: Type[SLEAPNeuralNetwork] | Type[DLCNeuralNetwork]):
    if response.status_code != 200: 
        print(f"{neural_network_type} finished training at getting error: {response.json()}")
        return
    for result in response.json():
        if result["finished_training_at"] is None: continue
        net = neural_network_type.objects.get(model_uid=result['uid'])
        net.finished_training_at = result["finished_training_at"]
        net.save()