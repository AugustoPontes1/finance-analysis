from django.urls import path

from backend.apps.values_extraction.views import DocumentExctractionAPIView


urlpatterns = [
    path('upload_file/v1/', DocumentExctractionAPIView.as_view({"post": "upload_file"})),
    path('get_file/v1/', DocumentExctractionAPIView.as_view({"get": "get_file"})),
    path('select_file_params/v1/', DocumentExctractionAPIView.as_view({"post": "select_file_params"})),
    path('remove_file/v1/', DocumentExctractionAPIView.as_view({"delete": "remove_file"})),
    path('update_file/v1/', DocumentExctractionAPIView.as_view({"put": "update_file"})),
]
