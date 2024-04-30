from django.urls import path
from .views import (
    start_dlc_network_inference_view, 
    detail_inference_results_view, 
    list_inference_results_view,
    start_sleap_network_inference_view,
    download_inference_results_view,
    run_labeled_video_generation_view,
    download_labeled_video_view,
    delete_analysis_results_view,
)


app_name="network_inference"

urlpatterns = [
    path("run-dlc-network", start_dlc_network_inference_view, name="start_dlc_network_inference"),
    path("run-sleap-network", start_sleap_network_inference_view, name="start_sleap_network_inference"),
    path("<int:id>", detail_inference_results_view, name="detail_inference_results"),
    path("", list_inference_results_view, name="list_inference_results"),
    path("<int:id>/download", download_inference_results_view, name="download_inference_results"),
    path("<int:id>/generate-labeled-video", run_labeled_video_generation_view, name="run_labeled_video_generation"),
    path("<int:id>/download-labeled-video", download_labeled_video_view, name="download_labeled_video"),
    path("<int:id>/delete", delete_analysis_results_view, name="delete_analysis_results"),
]