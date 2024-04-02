from utils.microservices.microservice import DefaultMicroservice
from django.conf import settings


class SLEAPMicroservice(DefaultMicroservice):
    MICROSERVICE_URL = settings.SLEAP_MICROSERVICE_URL

SLEAP_MICROSERVICE = SLEAPMicroservice()