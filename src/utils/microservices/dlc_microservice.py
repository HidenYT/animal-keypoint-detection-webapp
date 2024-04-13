from utils.microservices.microservice import DefaultMicroservice
from django.conf import settings


class DLCMicroservice(DefaultMicroservice):
    MICROSERVICE_URL = settings.DLC_MICROSERVICE_URL

DLC_MICROSERVICE = DLCMicroservice()