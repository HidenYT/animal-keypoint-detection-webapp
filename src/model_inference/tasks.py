from datetime import datetime
import os
from uuid import uuid4
from celery import Celery
import cv2 as cv
from core.celery import app as celery
from model_inference.models import InferredKeypoints
from model_inference.utils import process_video_analysis_results_response
from model_training.models import NeuralNetworkType
from requests.exceptions import ConnectionError
from utils.microservices.dlc_microservice import DLC_MICROSERVICE
from utils.microservices.sleap_microservice import SLEAP_MICROSERVICE
from django.conf import settings
from random import randint

@celery.task
def get_uncompleted_analysis_results():
    uncompleted = InferredKeypoints.objects.filter(keypoints__isnull=True)
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

@celery.task(bind=True)
def generate_labeled_video_from_analysis_results(self, results_id: int, file_path: str):
    results = InferredKeypoints.objects.get(pk=results_id, keypoints__isnull=False)
    all_keypoints: dict[str, dict[str, list[float | None]]] = results.keypoints # type: ignore
    colors = {k: [randint(0, 255) for _ in range(3)] for k in all_keypoints["0"]}
    cap = cv.VideoCapture(results.inference_video.file.path)
    fourcc = cv.VideoWriter.fourcc(*'mp4v')
    fps = cap.get(cv.CAP_PROP_FPS)
    frame_sz = int(cap.get(cv.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    writer = cv.VideoWriter(file_path, fourcc, fps, frame_sz)
    for frame_n, keypoints in all_keypoints.items():
        frame_n = int(frame_n)
        if frame_n%10 == 0: print(frame_n)
        cap.set(cv.CAP_PROP_POS_FRAMES, frame_n)
        writer.set(cv.CAP_PROP_POS_FRAMES, frame_n)
        res, image = cap.read()
        for kp_name, kp_coords in keypoints.items():
            if kp_coords[0] is None or kp_coords[1] is None: continue
            kp_coords = int(kp_coords[0]), int(kp_coords[1])
            color = colors[kp_name]
            cv.circle(image, kp_coords, 3, color, -1)
            text_size = cv.getTextSize(kp_name, cv.FONT_HERSHEY_SIMPLEX, 1/3, 1)[0]
            text_coords = kp_coords[0]-text_size[0]//2, kp_coords[1]-3-text_size[1]//2
            cv.putText(image, kp_name, text_coords, cv.FONT_HERSHEY_SIMPLEX, 1/3, color)
        writer.write(image)
    writer.release()
    cap.release()
    results.labeled_video.finished_production_at = datetime.now()
    results.labeled_video.save()


@celery.on_after_finalize.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(10, get_uncompleted_analysis_results, name="Get uncompleted analysis results")