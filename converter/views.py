import logging
import uuid

from django.core.cache import cache
from django.core.files.storage import default_storage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from compressor.forms import ConvertVideoForm
from converter.tasks import convert_video_file
from compressor.utils import get_file_format, get_path_to_file
from django_media_editor.constants import AVAILABLE_VIDEO_FORMATS, FileStatus, MAX_VIDEO_SIZE, \
    FULL_PATH_TO_PROCESSED_FILES

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

                convert_video_file.delay(file_path, file_identifier, file_format, convert_format)
                cache.set(file_identifier, f'{FileStatus.IN_PROCESS},{convert_format}')
                return HttpResponseRedirect(f'/download/{file_identifier}')
            else:
                logger.error(f'Incorrect size or format of video '
                             f'(Size: {file_from_request.size}, format: {file_format})')
                return HttpResponseRedirect('error')
    else:
        form = ConvertVideoForm()
    return render(request, 'convert_video.html', {'form': form})
