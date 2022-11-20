import uuid

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.files.storage import default_storage

from ws_app.consumers import send_video_ready_msg
from .forms import UploadFileForm

import logging

from .tasks import compress_video_file

logger = logging.getLogger(__name__)


def compress_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_identifier = str(uuid.uuid4())
            file_path = default_storage.save(f'./temp/{file_identifier}.mp4', request.FILES['file'])
            compress_video_file.delay(file_path, file_identifier, 3)
            return HttpResponseRedirect(file_identifier)
    else:
        form = UploadFileForm()
    return render(request, 'compressor.html', {'form': form})


def get_compressed_file(request, video_id):
    return render(request, 'get_compressed_file.html', {'video_id': video_id})
