from datetime import datetime
from requests import Response

from model_inference.models import InferredKeypoints

def process_video_analysis_results_response(response: Response, neural_network_type_name: str):
    if response.status_code != 200: 
        print(f"{neural_network_type_name} inference results error: {response.json()}")
    else:
        for result in response.json():
            if result["keypoints"] is None: continue
            kps = InferredKeypoints.objects.get(
                results_id=result["id"], 
                trained_neural_network__neural_network_type__name=neural_network_type_name
            )
            kps.keypoints = result["keypoints"]
            kps.finished_inference_at = datetime.now()
            kps.save()
    