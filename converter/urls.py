from django.urls import path

from . import views

urlpatterns = [
    path('videos/', views.convert_video, name='convert_video'),
    path('images/', views.convert_image, name='convert_image'),
    path('convert_video_to_gif/', views.convert_video_to_gif_view, name='convert_video_to_gif'),
]