from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('values_extraction/', include("apps.values_extraction.urls")),
    path("values_ai_extraction/", include("apps.values_ai_extraction.urls")),
]
