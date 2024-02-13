from abc import ABC, abstractmethod
from typing import TypeVar
from typing import Generic

T = TypeVar('T')

class DatasetPreparator(ABC, Generic[T]):
    '''Интерфейс классов, осуществляющих подготовку данных перед обучением нейросети.'''
    
    @abstractmethod
    def prepare_dataset(self) -> T:
        '''Подготавливает данные для дальнейшего использования нейросети (запуск обучения, настройки, ...).'''
        pass