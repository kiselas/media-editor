from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
from .utils import compress_video_file

import logging
logger = logging.getLogger(__name__)


def compress_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            url_for_waiting = compress_video_file(request.FILES['file'], 2)
            return HttpResponseRedirect(f'{url_for_waiting}')
        logger.debug("This logs a debug message.")
        logger.info("This logs an info message.")
        logger.warn("This logs a warning message.")
        logger.error("This logs an error message.")
    else:
        form = UploadFileForm()
    return render(request, 'compressor.html', {'form': form})


def get_templatecompressed_file(request, video_id):
    from django.core.cache import cache
    cache.set('foo', 'bar')
    return render(request, 'get_compressed_file.html', {'video_id': video_id})
