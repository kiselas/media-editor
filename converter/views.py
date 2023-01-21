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
    return render(request, 'convert_video.html', {'form': form})


def convert_image(request):
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
    return render(request, 'convert_image.html', {'form': form})


def convert_video_to_gif_view(request):
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
    return render(request, 'convert_video_to_gif.html', {'form': form})
