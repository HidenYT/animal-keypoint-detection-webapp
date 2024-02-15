from typing import Any, Callable, Union
from celery import Task
from model_inference.tasks import dlc_inferrence


class InferenceTaskRunner:
    '''Обёртка для удобного запуска задачи celery по запуску нейросети на видео.
    
    Принимает данные, необходимые для всех дальнейших запуска нейросети: 
    id пользователя, id обученной нейросети и id видео. 
    
    Поле `task` должно содержать задачу celery, которая принимает параметры:
    id пользователя, id обученной нейросети и id видео. '''
    task: Union[Task, Callable[[int, int, int], Any]]

    def __init__(self, user_id: int, trained_network_id: int, video_id: int) -> None:
        self._user_id = user_id
        self._trained_network_id = trained_network_id
        self._video_id = video_id

    def start_inference(self):
        '''Запускает задачу celery, id пользователя, id обученной нейросети и id видео.'''
        self.task.delay(self._user_id, self._trained_network_id, self._video_id)

class DLCInferenceTaskRunner(InferenceTaskRunner):
    task = dlc_inferrence