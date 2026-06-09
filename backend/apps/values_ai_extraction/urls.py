from django.urls import path
from backend.apps.values_ai_extraction.views import AIExtractionAPIView

urlpatterns = [
    path("analyze_document/<int:pk>/v1/", AIExtractionAPIView.as_view({"post": "analyze_document"})),
]
