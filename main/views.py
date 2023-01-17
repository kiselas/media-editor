from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

from compressor.utils import get_path_to_file
from django_media_editor.constants import FileStatus, FULL_PATH_TO_PROCESSED_FILES


def index(request):
    context = {'latest_question_list': 'hello'}
    return render(request, 'index.html', context)


def get_compressed_file(request, file_id):
    path_to_file = ""
    file_status = FileStatus.ERROR
    id_and_status = cache.get(file_id)
    if id_and_status:
        file_status, file_format = id_and_status.split(',')
        if file_status == FileStatus.READY:
            path_to_file = get_path_to_file(file_id, file_format, FULL_PATH_TO_PROCESSED_FILES)

    return render(request, 'get_compressed_file.html', {"file_id": file_id,
                                                        "file_status": file_status,
                                                        "path_to_file": path_to_file})


def get_sitemap(request, **kwargs):
    t = loader.get_template('sitemap.xml')
    response = HttpResponse(t.render(), content_type="application/xml")
    response['Content-Disposition'] = 'attachment; filename=sitemap.xml'
    return response
