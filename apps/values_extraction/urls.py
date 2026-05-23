from django.urls import path

from apps.values_extraction.views import DocumentExctractionAPIView


urlpatterns = [
    path('upload_file/v1/', DocumentExctractionAPIView.upload_file),
    path('get_file/v1/', DocumentExctractionAPIView.get_file),
    path('select_file_params/v1/', DocumentExctractionAPIView.select_file_params),
    path('remove_file/v1/', DocumentExctractionAPIView.remove_file),
    path('update_file/v1/', DocumentExctractionAPIView.update_file),
]
