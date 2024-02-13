import csv
from typing import Iterable
import py7zr
import yaml
from yaml import SafeDumper
from model_training.training_config_adapters.dlc_training_config_adapter import DeepLabCutTrainingConfigAdapter
from .dataset_preparator import DatasetPreparator
import os
from django.conf import settings
from secrets import token_urlsafe


class DLCDatasetPreparator(DatasetPreparator[str]):
    
    def __init__(self, adapter: DeepLabCutTrainingConfigAdapter) -> None:
        self.adapter = adapter

    
    def _convert_labels_to_dlc_format(self, labels_file_path: str) -> tuple[str, set[str]]:
        '''Создаёт файл `labeled-data/dummy/CollectedData_{username}.csv` из файла
        `labeled-data/dummy/labels.csv` в формате, необходимом для `CollectedData_{username}.csv`.
        
        Возвращает путь к файлу `labeled-data/dummy/CollectedData_{username}.csv`, а также список частей тела из файла разметки.'''
        username = self.adapter.username
        # Выбираем данные из файла разметки
        with open(labels_file_path, "r") as f:
            reader = iter(csv.reader(f))
            bodyparts = next(reader)[1:]
            next(reader)
            coords: dict[str, list[str]] = {}
            for row in reader:
                coords[row[0]] = [val for val in row[1:]]

        # Создаём файл разметки по формату DLC
        filename = f'CollectedData_{username}.csv'
        labels_folder = os.path.dirname(labels_file_path)
        result_path = os.path.join(labels_folder, filename)
        with open(result_path, "w") as f:
            l = (len(bodyparts))
            f.write("scorer" + (f",{username}")*l + os.linesep)
            f.write("bodyparts," + ",".join(bodyparts) + os.linesep)
            f.write("coords" + ",x,y"*(l//2) + os.linesep)
            for k, v in coords.items():
                f.write(f"labeled-data/dummy/{k}," + ",".join(v) + os.linesep)
        return result_path, set(bodyparts)


    def _fill_bodyparts(self, config_path: str, bodyparts: Iterable[str]):
        '''Изменяет файл `config.yaml`, добавляя поля в `bodyparts` части тела из разметки и удаляя 
        данные из поля `skeleton`.'''
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
            data["bodyparts"] = list(bodyparts)
            data["skeleton"] = None
            data["identity"] = None
            SafeDumper.add_representer(
                type(None),
                lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:null', '')
            )
        with open(config_path, "w") as f:
            f.write(yaml.safe_dump(data, default_flow_style=False))


    def prepare_dataset(self) -> str:
        # Импорт из функции, так как загрузка библиотеки занимает много времени
        import deeplabcut

        username = self.adapter.username
        base_folder = settings.DLC_PROJECTS_DIR_PATH
        dummy_video = settings.DUMMY_VIDEO_PATH

        # Создаём проект
        user_projects_folder = os.path.join(base_folder, username)
        os.makedirs(user_projects_folder, exist_ok=True)
        proj_config = deeplabcut.create_new_project(token_urlsafe(6), username, [dummy_video], working_directory=user_projects_folder)
        project_path = os.path.dirname(proj_config)

        # Распаковка датасета в папку разметки проекта
        labels_folder_path = os.path.join(project_path, 'labeled-data', 'dummy')
        os.makedirs(labels_folder_path, exist_ok=True)
        with py7zr.SevenZipFile(self.adapter.dataset_path) as f:
            f.extractall(labels_folder_path)

        # Изменение файла разметки под формат DLC
        labels_file = os.path.join(labels_folder_path, 'labels.csv')
        labels_file, bodyparts = self._convert_labels_to_dlc_format(labels_file)
        deeplabcut.convertcsv2h5(proj_config, scorer=username, userfeedback=False)

        # Заполняем config.yaml скелетом 
        self._fill_bodyparts(proj_config, bodyparts)

        deeplabcut.create_training_dataset(proj_config, net_type=self.adapter.net_type)
        return proj_config