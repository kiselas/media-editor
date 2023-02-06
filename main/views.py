from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

from compressor.utils import get_path_to_file
from django_media_editor.constants import FileStatus, FULL_PATH_TO_PROCESSED_FILES


def index(request):
    context = {'title': 'Media-editor - сжать фото и видео онлайн',
               'description':
                   '''Это онлайн-сервис для сжатия и конвертации фото (PNG. JPEG) и видео (MP4, AVI, MKV, MOV) файлов.
                        Вы можете выбрать степень сжатия фото и видео, а так же поменять формат файла.
                        Бесплатный и быстрый инструмент поможет вам уменьшить размер файлов всего в пару кликов.''',
               'keywords': 'Сжатие, фото, видео, gif, изменение размера, изменение формата, конвертировать'}
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
                                                        "path_to_file": path_to_file,
                                                        "title": "Файл обрабатывается, ожидайте",
                                                        "description": "",
                                                        "keywords": ""})


def get_sitemap(request, **kwargs):
    t = loader.get_template('sitemap.xml')
    response = HttpResponse(t.render(), content_type="application/xml")
    response['Content-Disposition'] = 'attachment; filename=sitemap.xml'
    return response


def get_robots(request, **kwargs):
    t = loader.get_template('robots.txt')
    response = HttpResponse(t.render(), content_type="text/plain")
    response['Content-Disposition'] = 'attachment; filename=robots.txt'
    return response
