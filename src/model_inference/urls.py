from django.urls import path
from .views import start_dlc_network_inference_view, detail_inference_results_view, list_inference_results_view


app_name="network_inference"

urlpatterns = [
    path("run-dlc-network", start_dlc_network_inference_view, name="start_dlc_network_inference"),
    path("<int:id>", detail_inference_results_view, name="detail_inference_results"),
    path("", list_inference_results_view, name="list_inference_results"),
]