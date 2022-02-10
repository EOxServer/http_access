from django.urls import path

from . import views

app_name = "http_access"
urlpatterns = [
    path("storage/<str:storage_name>/<path:path>", views.return_file, name="file"),
    path("local/<path:path>", views.return_file, name="file-local"),
]
