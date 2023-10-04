import logging

import ffmpy
from django.conf import settings
from django.core.cache import cache
from PIL import Image
from PIL.Image import Resampling

from compressor.utils import get_crf_for_compression
from django_celery.celery import app
from django_media_editor.constants import (
    FFMPEG_COMPRESSION_PRESET,
    FILE_LIFETIME,
    FULL_PATH_TO_PROCESSED_FILES,
    FileStatus,
)
from django_media_editor.tasks import delete_file
from ws_app.consumers import get_channel_video_group_name, send_error_msg, send_video_ready_msg


class InvalidCRFSize(Exception):
    """Raised when the input size invalid"""


BASE_DIR = settings.BASE_DIR
logger = logging.getLogger(__name__)


@app.task
def compress_video_file(video_file_path, file_identifier, target_size, file_format):
    logger.info(f"Start compressing video with preset {FFMPEG_COMPRESSION_PRESET}")
    target_size = get_crf_for_compression(target_size)
    file_name = f"{file_identifier}{file_format}"

    if not FULL_PATH_TO_PROCESSED_FILES.is_dir():
        FULL_PATH_TO_PROCESSED_FILES.mkdir()

    path_to_file = FULL_PATH_TO_PROCESSED_FILES / file_name
    ffmpeg_input_parameters = "-y -hide_banner -nostats -loglevel warning -threads 6"
    ffmpeg_output_parameters = (
        # "-s " + '854x480 ' + "-crf " + str(target_size)
        f"-c:v libx264 -preset {FFMPEG_COMPRESSION_PRESET} -crf {target_size}"
    )

    ff = ffmpy.FFmpeg(
        executable="ffmpeg",
        inputs={BASE_DIR / "media" / video_file_path: ffmpeg_input_parameters},
        outputs={path_to_file: ffmpeg_output_parameters},
    )
    try:
        ff.run()

        cache.set(file_identifier, f"{FileStatus.READY},{file_format}")
        group_name = get_channel_video_group_name(file_identifier)

        # ссылка для скачивания не должна включать базовую папку проекта
        send_video_ready_msg(group_name,
                             path_to_file=str(path_to_file).replace("/code", ""))
        delete_file.apply_async((str(path_to_file), file_identifier), countdown=FILE_LIFETIME)

        logger.info("Video compression is successful")
    except ffmpy.FFRuntimeError:
        group_name = get_channel_video_group_name(file_identifier)
        cache.set(file_identifier, f"{FileStatus.ERROR},{file_format}")
        send_error_msg(group_name)
        logger.info("Video compression error", exc_info=True)
        return False


@app.task
def compress_image_file(file_path, file_identifier, target_size, file_format):
    logger.info(f"Start compressing image with target_size {target_size}")
    target_size = (100 - int(target_size)) / 100
    file_name = f"{file_identifier}{file_format}"
    path_to_file = FULL_PATH_TO_PROCESSED_FILES / file_name
    if not FULL_PATH_TO_PROCESSED_FILES.is_dir():
        FULL_PATH_TO_PROCESSED_FILES.mkdir()
    try:
        foo = Image.open(BASE_DIR / "media" / file_path)
        new_size = (int(foo.size[0] * target_size), int(foo.size[1] * target_size))  # (400 * 0.5, 800 * 0.5)

        # downsize the image with an LANCZOS filter (gives the highest quality)
        foo = foo.resize(new_size, Resampling.LANCZOS)

        foo.save(f"{path_to_file}", optimize=True, quality=95)

        cache.set(file_identifier, f"{FileStatus.READY},{file_format}")
        group_name = get_channel_video_group_name(file_identifier)
        send_video_ready_msg(group_name, path_to_file=str(path_to_file).replace("/code", ""))
        delete_file.apply_async((str(path_to_file), file_identifier), countdown=FILE_LIFETIME)

        logger.info("Image compression is successful!")
    except Exception:
        group_name = get_channel_video_group_name(file_identifier)
        cache.set(file_identifier, f"{FileStatus.ERROR}.{file_format}")
        send_error_msg(group_name)
        logger.exception("Image compression error", exc_info=True)
