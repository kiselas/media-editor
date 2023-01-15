from django.urls import path

from . import views

urlpatterns = [
    path('', views.convert_video, name='convert_video'),
]