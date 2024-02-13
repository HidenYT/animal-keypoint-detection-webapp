from model_training.network_training_runners.network_training_runner import NetworkTrainingRunner
from model_training.training_config_adapters.dlc_training_config_adapter import DeepLabCutTrainingConfigAdapter


class DLCTrainingRunner(NetworkTrainingRunner):
    def __init__(self, project_config_path: str, adapter: DeepLabCutTrainingConfigAdapter) -> None:
        self._project_config_path = project_config_path
        self._adapter = adapter

    def start_training(self):
        # Импорт из функции, так как загрузка библиотеки занимает много времени
        import deeplabcut

        deeplabcut.train_network(self._project_config_path, maxiters=self._adapter.maxiters)