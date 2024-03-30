from utils.microservices.microservice import Microservice
from django.conf import settings


class SLEAPMicroservice(Microservice):
    MICROSERVICE_URL = settings.SLEAP_MICROSERVICE_URL