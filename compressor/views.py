import logging
import uuid

from django.core.cache import cache
from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect
from django.shortcuts import render

from django_media_editor.constants import (
    AVAILABLE_IMAGE_FORMATS,
    AVAILABLE_VIDEO_FORMATS,
    MAX_IMAGE_SIZE,
    MAX_VIDEO_SIZE,
    FileStatus,
)

from .forms import CompressVideoForm, UploadImageForm
from .tasks import compress_image_file, compress_video_file
from .utils import get_file_format

logger = logging.getLogger(__name__)


def compress_video(request):
    context = {"title": "Сжать видео MP4, AVI, MOV, MKV, VMW без потери качества. "
                        "Онлайн-инструмент для сжатия видео всех форматов | Media-Editor",
               "description": """Сжимайте видео MP4, AVI, MOV, MKV, VMW онлайн бесплатно, уменьшайте размер видео
               онлайн,
                               бесплатный компрессор видео.""",
               "keywords": "сжать видео, "
                           "сжать видео онлайн, "
                           "сжать качество видео, "
                           "сжать видео без потери качества, "
                           "сжать качество видео онлайн, "
                           "сжать видео онлайн бесплатно, "
                           "сжать видео для ватсап, "
                           "сжать большое видео онлайн, "
                           "сжать видео для почты",
               "display_metric": True,
               }
    if request.method == "POST":
        form = CompressVideoForm(request.POST, request.FILES)
        if form.is_valid():
            file_from_request = request.FILES["file"]
            file_format = get_file_format(file_from_request)
            if file_format in AVAILABLE_VIDEO_FORMATS and file_from_request.size < MAX_VIDEO_SIZE:
                file_identifier = str(uuid.uuid4())
                file_path = default_storage.save(f"./temp/{file_identifier}{file_format}", file_from_request)
                target_size = form.cleaned_data["compression_ratio"]
                cache.set(file_identifier, f"{FileStatus.IN_PROCESS},{file_format}")

                compress_video_file.delay(file_path, file_identifier, target_size, file_format)
                return HttpResponseRedirect(f"/download/{file_identifier}")
            else:
                logger.error(f"Incorrect size or format of video "
                             f"(Size: {file_from_request.size}, format: {file_format})")
                return HttpResponseRedirect("/download/error")
    else:
        form = CompressVideoForm()
    context["form"] = form
    return render(request, "compress_video.html", context)


def compress_image(request):
    context = {
        "title": "Сжать фото JPG, JPEG, PNG, WEBP без потери качества. "
                 "Онлайн-инструмент для сжатия картинок всех форматов",
        "description": """Сжимайте картинки JPG, JPEG, PNG, WEBP онлайн бесплатно, уменьшайте размер изображения онлайн,
                                   бесплатный компрессор фото.""",
        "keywords": """сжатая картинки онлайн,
                    сжать картинку онлайн,
                    сжать качество картинки,
                    уменьшение веса картинок,
                    сжать размер картинки,
                    уменьшение размера картинок,
                    сжать качество картинки онлайн,
                    сжать картинку онлайн без потери качества,
                    сжать картинку jpg онлайн,
                    сжать файл картинку,
                    сжать картинку пнг,
                    уменьшить размер картинки онлайн""",
        "display_metric": True,
    }

    if request.method == "POST":
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            file_from_request = request.FILES["file"]
            file_format = get_file_format(file_from_request)
            if file_format in AVAILABLE_IMAGE_FORMATS and file_from_request.size < MAX_IMAGE_SIZE:
                file_identifier = str(uuid.uuid4())
                file_path = default_storage.save(f"./temp/{file_identifier}{file_format}", file_from_request)
                target_size = form.cleaned_data["compression_ratio"]
                cache.set(file_identifier, f"{FileStatus.IN_PROCESS},{file_format}")

                compress_image_file.delay(file_path, file_identifier, target_size, file_format)
                return HttpResponseRedirect(f"/download/{file_identifier}")
            else:
                logger.error(f"Incorrect size or format of file "
                             f"(Size: {file_from_request.size}, format: {file_format})")
                return HttpResponseRedirect("/download/error")
    else:
        form = UploadImageForm()
    context["form"] = form
    return render(request, "compress_image.html", context)

