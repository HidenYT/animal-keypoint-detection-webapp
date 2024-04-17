from datetime import datetime
from requests import Response

from model_inference.models import InferredKeypoints
from model_training.models import NeuralNetworkType

def process_video_analysis_results_response(response: Response, neural_network_type_name: str):
    if response.status_code != 200: 
        print(f"{neural_network_type_name} inference results error: {response.json()}")
    else:
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
    