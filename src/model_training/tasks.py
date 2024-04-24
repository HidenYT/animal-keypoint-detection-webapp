from celery import Celery
from core.celery import app as celery
from model_inference.utils import process_finished_training_at_response
from model_training.models import DLCNeuralNetwork, SLEAPNeuralNetwork
from utils.microservices.dlc_microservice import DLC_MICROSERVICE
from utils.microservices.sleap_microservice import SLEAP_MICROSERVICE

@celery.task
def get_neural_networks_training_finish_time():
    sleap_uncompleted = SLEAPNeuralNetwork.objects.filter(finished_training_at__isnull=True).values_list('model_uid', flat=True)
    dlc_uncompleted = DLCNeuralNetwork.objects.filter(finished_training_at__isnull=True).values_list('model_uid', flat=True)
    if sleap_uncompleted:
        try:
            sleap_response = SLEAP_MICROSERVICE.send_training_finished_at_request(sleap_uncompleted)
            process_finished_training_at_response(sleap_response, SLEAPNeuralNetwork)
        except ConnectionError as e:
            print(f"Didn't manage to connect to a microservice due to the error: {e}")
    if dlc_uncompleted:
        try:
            dlc_response = DLC_MICROSERVICE.send_training_finished_at_request(dlc_uncompleted)
            process_finished_training_at_response(dlc_response, DLCNeuralNetwork)
        except ConnectionError as e:
            print(f"Didn't manage to connect to a microservice due to the error: {e}")

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(10, get_neural_networks_training_finish_time, name="Get finished training at for neural networks")