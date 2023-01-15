import uuid

from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.files.storage import default_storage

from ws_app.consumers import send_video_ready_msg
from django_media_editor.constants import FULL_PATH_TO_PROCESSED_FILES, FileStatus, \
    AVAILABLE_VIDEO_FORMATS, AVAILABLE_IMAGE_FORMATS, MAX_VIDEO_SIZE, MAX_IMAGE_SIZE
from .forms import CompressVideoForm, UploadImageForm

import logging

from .tasks import compress_video_file, compress_image_file
from .utils import get_path_to_file, get_file_format

logger = logging.getLogger(__name__)


def compress_video(request):
    if request.method == 'POST':
        form = CompressVideoForm(request.POST, request.FILES)
        if form.is_valid():
            file_from_request = request.FILES['file']
            file_format = get_file_format(file_from_request)
            if file_format in AVAILABLE_VIDEO_FORMATS and file_from_request.size < MAX_VIDEO_SIZE:
                file_identifier = str(uuid.uuid4())
                file_path = default_storage.save(f'./temp/{file_identifier}{file_format}', file_from_request)
                target_size = form.cleaned_data['compression_ratio']

                compress_video_file.delay(file_path, file_identifier, target_size, file_format)
                cache.set(file_identifier, f'{FileStatus.IN_PROCESS},{file_format}')
                return HttpResponseRedirect(f'/download/{file_identifier}')
            else:
                logger.error(f'Incorrect size or format of video '
                             f'(Size: {file_from_request.size}, format: {file_format})')
                return HttpResponseRedirect('error')
    else:
        form = CompressVideoForm()
    return render(request, 'compress_video.html', {'form': form})


def compress_image(request):
    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            file_from_request = request.FILES['file']
            file_format = get_file_format(file_from_request)
            if file_format in AVAILABLE_IMAGE_FORMATS and file_from_request.size < MAX_IMAGE_SIZE:
                file_identifier = str(uuid.uuid4())
                file_path = default_storage.save(f'./temp/{file_identifier}{file_format}', file_from_request)
                target_size = form.cleaned_data['compression_ratio']

                compress_image_file.delay(file_path, file_identifier, target_size, file_format)
                cache.set(file_identifier, f'{FileStatus.IN_PROCESS},{file_format}')
                return HttpResponseRedirect(f'/download/{file_identifier}')
            else:
                logger.error(f'Incorrect size or format of file '
                             f'(Size: {file_from_request.size}, format: {file_format})')
                return HttpResponseRedirect('error')
    else:
        form = UploadImageForm()
    return render(request, 'compress_image.html', {'form': form})

