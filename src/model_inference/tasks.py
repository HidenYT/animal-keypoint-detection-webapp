from celery import Celery
from core.celery import app as celery
from model_inference.models import InferredKeypoints
from model_inference.utils import process_video_analysis_results_response
from model_training.models import NeuralNetworkType
from requests.exceptions import ConnectionError
from utils.microservices.dlc_microservice import DLC_MICROSERVICE
from utils.microservices.sleap_microservice import SLEAP_MICROSERVICE

@celery.task
def get_uncompleted_analysis_results():
    uncompleted = (InferredKeypoints.objects
                   .filter(keypoints__isnull=True)
                   )
    sleap_ids = []
    dlc_ids = []
    for kps in uncompleted:
        if kps.sleap_neural_network:
            sleap_ids.append(kps.results_id)
        else:
            dlc_ids.append(kps.results_id)
    if sleap_ids:
        try:
            sleap_response = SLEAP_MICROSERVICE.send_inference_results_request(sleap_ids)
            process_video_analysis_results_response(sleap_response, NeuralNetworkType.SLEAP)
        except ConnectionError as e:
            print(f"Didn't manage to connect to a microservice due to the error: {e}")
    if dlc_ids:
        try:
            dlc_response = DLC_MICROSERVICE.send_inference_results_request(dlc_ids)
            process_video_analysis_results_response(dlc_response, NeuralNetworkType.DLC)
        except ConnectionError as e:
            print(f"Didn't manage to connect to a microservice due to the error: {e}")

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(10, get_uncompleted_analysis_results, name="Get uncompleted analysis results")