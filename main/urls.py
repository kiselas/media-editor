from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('download/<str:file_id>', views.get_compressed_file, name='compress_file_unique_url'),
    path('sitemap.xml', views.get_sitemap, name='sitemap'),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain"), ),
]