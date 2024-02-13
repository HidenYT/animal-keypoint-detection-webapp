from abc import ABC, abstractmethod

class NetworkTrainingRunner(ABC):
    '''Интерфейс классов, которые запускают процесс обучения нейросети.'''
    
    @abstractmethod
    def start_training(self):
        '''Функция, непосредственно запускающая процесс обучения нейросети'''
        pass