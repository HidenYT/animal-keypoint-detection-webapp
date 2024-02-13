from typing import Any


class BaseTrainingConfigAdapter:
    '''Базовый адаптер конфигурации для обучения нейросети. 
    
    Содержит базовые поля, необходимые для настройки и запуска обучения нейросетей.'''
    def __init__(self, username: str, dataset_path: str, dataset_id: int, data: dict[str, Any]):
        self._dataset_id = dataset_id
        self._username = username
        self._data = data
        self._dataset_path = dataset_path
    
    @property
    def dataset_id(self) -> int:
        return self._dataset_id

    @property
    def username(self) -> str:
        return self._username

    @property
    def trained_network_name(self) -> str:
        return self._data['trained_network_name']
    
    @property
    def dataset_path(self) -> str:
        return self._dataset_path