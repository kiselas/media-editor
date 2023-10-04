from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("download/<str:file_id>", views.get_compressed_file, name="compress_file_unique_url"),
    path("sitemap.xml", views.get_sitemap, name="sitemap"),
    path("robots.txt", views.get_robots, name="robots"),
]
