from datetime import datetime
import os
import glob
import shutil
from typing import Any, Optional
from django.contrib.auth.models import User
import pandas as pd
from model_inference.inference_runners.inference_runner import InferenceRunner
from django.conf import settings
from secrets import token_urlsafe
from model_inference.models import InferredKeypoints

from model_training.models import TrainedNeuralNetwork
from video_manager.models import InferenceVideo


class DLCInferenceRunner(InferenceRunner):
    def __init__(self, user: User, trained_net: TrainedNeuralNetwork, video: InferenceVideo) -> None:
        super().__init__(user, trained_net, video)
        self._dest_folder = self._create_dest_folder()
    
    def _create_dest_folder(self) -> str:
        """Создаёт папку для выгрузки результатов DeepLabCut и возвращает путь до неё."""
        # Путь назначения для результатов: папка DLC результатов/имя пользователя/дата и время/токен/
        user_folder = os.path.join(settings.DLC_INFERENCE_DIR_PATH, self._user.username)
        datetime_now = datetime.now().strftime("%d.%m.%Y_%H-%M-%S.%f")
        inference_folder_name = f"{datetime_now}-{token_urlsafe(6)}"
        inference_folder_path = os.path.join(user_folder, inference_folder_name)
        os.makedirs(inference_folder_path, exist_ok=False)
        return inference_folder_path
    
    def _clear_dest_folder(self):
        shutil.rmtree(self._dest_folder)
    
    def _find_results_file(self) -> str:
        path = os.path.join(self._dest_folder, "*.csv")
        results = glob.glob(path)
        return results[0]
    
    def _generate_json_for_results(self, results_file: Optional[str] = None) -> dict[str, Any]:
        results_file = results_file or self._find_results_file()
        df = pd.read_csv(results_file, header=[0, 1, 2])
        # Нулевой уроень не нужен
        df.columns = df.columns.droplevel(0)
        # Удаляем столбец likelihood
        df = df.drop("likelihood", axis=1, level=1)
        df = df.drop("bodyparts", axis=1, level=0)
        D = df.T.groupby(level=0).apply(lambda df: df.xs(df.name).to_dict()).to_dict()
        return D

    def _create_inferred_keypoints_initial_object(self) -> InferredKeypoints:
        kps = InferredKeypoints()
        kps.keypoints = None
        kps.started_inference_at = datetime.now()
        kps.trained_neural_network = self._trained_net
        kps.inference_video = self._video
        kps.user = self._user
        kps.save()
        return kps

    def _save_inferred_keypoints_final_object(self, kps: InferredKeypoints, labels: dict[str, Any]) -> None:
        kps.keypoints = labels
        kps.finished_inference_at = datetime.now()
        kps.save()

    def run_inference(self):
        import deeplabcut
        # self._generate_json_for_results(r"D:\Documents\Programming\Diploma\backend\src\uploads\inference_videos\buharev2009@gmail.com\15.02.2024_13-54-31.660855-37daa367-5c8e-4fd1-80f_NlUXRN3DLC_resnet50_cKEo2Jz9Feb13shuffle1_10.csv")

        kps = self._create_inferred_keypoints_initial_object()
        deeplabcut.analyze_videos(self._trained_net.file_path, 
                                  self._video.file.path, 
                                  save_as_csv=True,
                                  destfolder=self._dest_folder)
        result_file = self._find_results_file()
        labels = self._generate_json_for_results(result_file)
        self._save_inferred_keypoints_final_object(kps, labels)
        self._clear_dest_folder()

        
        

        
        