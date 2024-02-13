from django.urls import path
from .views import start_dlc_network_training


app_name = "network_training"

urlpatterns = [
    path("start-dlc-training", start_dlc_network_training, name="start_dlc_network_training"),
]