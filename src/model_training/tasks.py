import datetime
from typing import Any
from core import celery_app
from model_training.models import NeuralNetworkType, TrainedNeuralNetwork
from model_training.network_training_runners.dlc_training_runner import DLCTrainingRunner
from model_training.training_config_adapters.dlc_training_config_adapter import BaseTrainingConfigAdapter, DeepLabCutTrainingConfigAdapter
from train_datasets_manager.models import TrainDataset
from .dataset_preparation.dlc_dataset_preparator import DLCDatasetPreparator


def create_trained_network_object(adapter: BaseTrainingConfigAdapter, 
                                  nn_path: str, 
                                  nn_type: str) -> TrainedNeuralNetwork:
    '''Функция создаёт, сохраняет в БД и возвращает `TrainedNeuralNetwork`.
    
    - `adapter` - адаптер настроек обучения.
    - `nn_path` - путь к нейросети, используемый для её дальнейшего запуска на реальных данных.
    - `nn_type` - тип нейросети, взятый из `NeuralNetworkType`'''
    ds = TrainDataset.objects.get(pk=adapter.dataset_id)
    nn = TrainedNeuralNetwork()
    nn.name = adapter.trained_network_name
    nn.file_path = nn_path
    nn.started_training_at = datetime.datetime.now()
    nn.train_dataset = ds
    nn.neural_network_type = NeuralNetworkType.objects.get(name=nn_type)
    nn.save()
    return nn
    

@celery_app.task
def start_dlc_network_training(username: str, dataset_path: str, dataset_id: int, config: dict[str, Any]):
    adapter = DeepLabCutTrainingConfigAdapter(username, dataset_path, dataset_id, config)
    project_path = DLCDatasetPreparator(adapter).prepare_dataset()
    nn = create_trained_network_object(adapter, project_path, NeuralNetworkType.DeepLabCut)
    DLCTrainingRunner(project_path, adapter).start_training()
    nn.finished_training_at = datetime.datetime.now()
    nn.save()

