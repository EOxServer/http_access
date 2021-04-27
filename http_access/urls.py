from django.urls import path

from . import views

app_name = "http_access"
urlpatterns = [
    path("<str:storage_name>/<path:path>", views.return_file, name="file"),
]
