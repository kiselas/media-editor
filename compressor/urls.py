from django.urls import path

from . import views

urlpatterns = [
    path('', views.compress_video, name='compress_video'),
    path('<str:video_id>', views.get_compressed_file, name='compress_file_unique_url'),
]