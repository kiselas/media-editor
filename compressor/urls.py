from django.urls import path

from . import views

urlpatterns = [
    path("videos/", views.compress_video, name="compress_video"),
    path("images/", views.compress_image, name="compress_image"),
]
