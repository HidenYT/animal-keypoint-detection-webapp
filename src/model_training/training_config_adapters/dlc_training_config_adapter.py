from typing import Any
from model_training.training_config_adapters.training_config_adapter import BaseTrainingConfigAdapter


class DeepLabCutTrainingConfigAdapter(BaseTrainingConfigAdapter):

    @property
    def net_type(self) -> str:
        return self._data['network_type']
    
    @property
    def maxiters(self) -> int:
        return self._data['max_iters']