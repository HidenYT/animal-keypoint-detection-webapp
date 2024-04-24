from django.urls import path
from .views import (
    delete_trained_network_view,
    start_dlc_network_training, 
    detail_trained_network_view, 
    list_trained_networks_view, 
    start_sleap_network_training,
    get_model_training_stats,
)

app_name = "network_training"

urlpatterns = [
    path("start-dlc-training", start_dlc_network_training, name="start_dlc_network_training"),
    path("start-sleap-training", start_sleap_network_training, name="start_sleap_network_training"),
    path("<str:neural_network_type>/<int:id>", detail_trained_network_view, name="detail_trained_network"),
    path("<str:neural_network_type>/<int:id>/delete", delete_trained_network_view, name="delete_trained_network"),
    path("", list_trained_networks_view, name="list_trained_networks"),
    path("training-stats/<str:neural_network_type>/<int:model_id>", get_model_training_stats, name="get_model_training_stats"),
]