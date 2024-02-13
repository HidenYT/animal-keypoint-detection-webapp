from abc import ABC
from typing import Any, Callable, Union
from model_training.tasks import start_dlc_network_training
from celery import Task
from train_datasets_manager.models import TrainDataset


class TrainingTaskRunner(ABC):
    '''Обёртка для удобного запуска задачи celery по обучению нейросети.
    
    Принимает данные, необходимые для всех дальнейших настроек обучения: 
    имя пользователя, датасет и словарь настроек. 
    
    Поле `task` должно содержать задачу celery, которая принимает параметры:
    имя пользователя, путь к датасету, id датасета, словарь настроек. '''
    task: Union[Task, Callable[[str, str, int, dict[str, Any]], Any]]

    def __init__(self, username: str, dataset: TrainDataset, config: dict[str, Any]) -> None:
        self._username = username
        self._ds = dataset
        self._config = config
    
    def start_training(self):
        '''Запускает задачу celery, передавая в неё имя пользователя, путь к датасету, id датасета, словарь настроек.'''
        self.task.delay(self._username, self._ds.file.path, self._ds.pk, self._config)

class DeepLabCutTrainingTaskRunner(TrainingTaskRunner):
    task = start_dlc_network_training