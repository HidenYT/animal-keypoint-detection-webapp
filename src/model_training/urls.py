from django.urls import path
from .views import start_dlc_network_training, detail_trained_network_view, list_trained_networks_view


app_name = "network_training"

urlpatterns = [
    path("start-dlc-training", start_dlc_network_training, name="start_dlc_network_training"),
    path("<int:id>", detail_trained_network_view, name="detail_trained_network"),
    path("", list_trained_networks_view, name="list_trained_networks"),
]