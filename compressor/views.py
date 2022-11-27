import uuid

from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.files.storage import default_storage

from ws_app.consumers import send_video_ready_msg
from .constants import PATH_TO_COMPRESSED_VIDEO, FileStatus
from .forms import UploadFileForm

import logging

from .tasks import compress_video_file
from .utils import check_video_is_ready, get_path_to_file

logger = logging.getLogger(__name__)


def compress_video(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_identifier = str(uuid.uuid4())
            file_path = default_storage.save(f'./temp/{file_identifier}.mp4', request.FILES['file'])
            compression_ratio = form.cleaned_data['compression_ratio']
            compress_video_file.delay(file_path, file_identifier, compression_ratio)
            cache.set(file_identifier, FileStatus.IN_PROCESS)
            return HttpResponseRedirect(file_identifier)
    else:
        form = UploadFileForm()
    return render(request, 'compress_video.html', {'form': form})


def get_compressed_file(request, video_id):
    path_to_file = ""
    file_status = cache.get(video_id)
    if file_status == FileStatus.READY:
        path_to_file = str(get_path_to_file(video_id, PATH_TO_COMPRESSED_VIDEO)).replace('/code', '')
    return render(request, 'get_compressed_file.html', {"video_id": video_id,
                                                        "file_status": file_status,
                                                        "path_to_file": path_to_file})
