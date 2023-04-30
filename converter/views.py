import logging
import uuid

from django.core.cache import cache
from django.core.files.storage import default_storage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from compressor.forms import ConvertVideoForm, ConvertImageForm, ConvertVideoToGifForm
from converter.tasks import convert_video_file, convert_image_file, convert_video_to_gif
from compressor.utils import get_file_format, get_path_to_file
from django_media_editor.constants import AVAILABLE_VIDEO_FORMATS, FileStatus, MAX_VIDEO_SIZE, \
    FULL_PATH_TO_PROCESSED_FILES, AVAILABLE_IMAGE_FORMATS, MAX_IMAGE_SIZE

logger = logging.getLogger(__name__)


def convert_video(request):
    context = {
        "title": "Конвертировать видео MP4, AVI, MOV, MKV, VMW в другой формат."
                 "Онлайн-инструмент для конвертации видео любого типа | Media-Editor",
        "description":
            """Конвертируйте видео в MP4, AVI, MOV, MKV, VMW онлайн бесплатно, поменяйте формат видео онлайн, 
                                       бесплатно сменить формат у видео.""",
        "keywords": 'конвертировать видео, '
                    'конвертировать видео онлайн, '
                    'конвертируем видео в mp4, '
                    'конвертировать видео бесплатно, '
                    'конвертировать видео онлайн бесплатно, '
                    'конвертировать видео +в mp4 онлайн, '
                    'изменять видео формат, '
                    'изменить формат видео онлайн, '
                    'изменить формат видео онлайн +в mp4'}
    if request.method == 'POST':
        form = ConvertVideoForm(request.POST, request.FILES)
        if form.is_valid():
            file_from_request = request.FILES['file']
            file_format = get_file_format(file_from_request)
            if file_format in AVAILABLE_VIDEO_FORMATS and file_from_request.size < MAX_VIDEO_SIZE:
                file_identifier = str(uuid.uuid4())
                # default storage сохраняет файлы в папку media, в подпапку temp
                file_path = default_storage.save(f'./temp/{file_identifier}{file_format}', file_from_request)
                convert_format = form.data['convert_format']
                cache.set(file_identifier, f'{FileStatus.IN_PROCESS},{convert_format}')

                convert_video_file.delay(file_path, file_identifier, file_format, convert_format)
                return HttpResponseRedirect(f'/download/{file_identifier}')
            else:
                logger.error(f'Incorrect size or format of file '
                             f'(Size: {file_from_request.size}, format: {file_format})')
                return HttpResponseRedirect('/download/error')
    else:
        form = ConvertVideoForm()
    context['form'] = form
    return render(request, 'convert_video.html', context)


def convert_image(request):
    context = {
        "title": "Конвертировать фото JPG, JPEG, PNG, WEBP в другой формат."
                 "Онлайн-инструмент для конвертации картинок любого типа | Media-Editor",
        "description":
            """Конвертируйте картинки в JPG, JPEG, PNG, WEBP онлайн бесплатно, поменяйте формат изображения онлайн, 
                                       бесплатно сменить формат у фото.""",
        "keywords": 'изменить формат картинки, '
                    'изменить формат картинки онлайн, '
                    'конвертировать картинку, '
                    'конвертировать картинку онлайн, '
                    'конвертировать картинку онлайн бесплатно, '
                    'конвертировать картинку в jpg онлайн, '
                    'конвертировать картинку в jpg,'}
    if request.method == 'POST':
        form = ConvertImageForm(request.POST, request.FILES)
        if form.is_valid():
            file_from_request = request.FILES['file']
            file_format = get_file_format(file_from_request)
            if file_format in AVAILABLE_IMAGE_FORMATS and file_from_request.size < MAX_IMAGE_SIZE:
                file_identifier = str(uuid.uuid4())
                # default storage сохраняет файлы в папку media, в подпапку temp
                file_path = default_storage.save(f'./temp/{file_identifier}{file_format}', file_from_request)
                convert_format = form.data['convert_format']

                cache.set(file_identifier, f'{FileStatus.IN_PROCESS},{convert_format}')
                convert_image_file.delay(file_path, file_identifier, file_format, convert_format)

                return HttpResponseRedirect(f'/download/{file_identifier}')
            else:
                logger.error(f'Incorrect size or format of file '
                             f'(Size: {file_from_request.size}, format: {file_format})')
                return HttpResponseRedirect('/download/error')
    else:
        form = ConvertImageForm()
    context['form'] = form
    return render(request, 'convert_image.html', context)


def convert_video_to_gif_view(request):
    context = {
        "title": "Конвертируйте видео в GIF. Онлайн-инструмент для конвертации видео в гиф | Media-Editor",
        "description": """Сделайте GIF-анимацию из видео онлайн бесплатно, конвертируйте видеофайл в gif.""",
        "keywords": 'видео в gif, '
                    'сделать gif из видео, '
                    'создать gif +из видео, '
                    'сделать gif онлайн из видео, '
                    'видео в gif онлайн, '
                    'конвертировать видео в gif,'
                    'перевести gif в видео'}
    if request.method == 'POST':
        form = ConvertVideoToGifForm(request.POST, request.FILES)
        if form.is_valid():
            file_from_request = request.FILES['file']
            file_format = get_file_format(file_from_request)
            if file_format in AVAILABLE_VIDEO_FORMATS and file_from_request.size < MAX_VIDEO_SIZE:
                file_identifier = str(uuid.uuid4())
                file_path = default_storage.save(f'./temp/{file_identifier}{file_format}', file_from_request)
                start_time = form.cleaned_data['start_time']
                end_time = form.cleaned_data['end_time']
                quantize_algorithm = form.cleaned_data['quantize_algorithm']
                cache.set(file_identifier, f'{FileStatus.IN_PROCESS},.gif')

                convert_video_to_gif.delay(file_path, file_identifier, file_format, start_time, end_time, quantize_algorithm)

                return HttpResponseRedirect(f'/download/{file_identifier}')
            else:
                logger.error(f'Incorrect size or format of video '
                             f'(Size: {file_from_request.size}, format: {file_format})')
                return HttpResponseRedirect('/download/error')
    else:
        form = ConvertVideoToGifForm()
    context['form'] = form
    return render(request, 'convert_video_to_gif.html', context)
