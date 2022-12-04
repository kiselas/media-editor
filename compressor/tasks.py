import logging
import pathlib

import ffmpy
import time
from django.conf import settings
from django.core.cache import cache

from compressor.constants import FileStatus, FULL_PATH_TO_COMPRESSED_FILES
from compressor.utils import get_crf_for_compression
from django_celery.celery import app
from ws_app.consumers import send_video_ready_msg, get_channel_video_group_name, send_error_msg


class InvalidCRFSize(Exception):
    """Raised when the input size invalid"""
    pass


logger = logging.getLogger(__name__)
BASE_DIR = settings.BASE_DIR
FFMPEG_COMPRESSION_PRESET = 'superfast'  # slow, medium, fast, superfast
FILE_LIFETIME = 60 * 15 # время жизни файла 15 минут

@app.task
def compress_video_file(video_file_path, file_identifier, target_size, file_format):
    logger.info(f'Start compressing video with preset {FFMPEG_COMPRESSION_PRESET}')
    target_size = get_crf_for_compression(target_size)
    file_name = f'{file_identifier}{file_format}'

    if not FULL_PATH_TO_COMPRESSED_FILES.is_dir():
        FULL_PATH_TO_COMPRESSED_FILES.mkdir()

    path_to_file = FULL_PATH_TO_COMPRESSED_FILES / file_name
    ffmpeg_output_parameters = (
        # "-s " + '854x480 ' + "-crf " + str(target_size)
        f"-c:v libx264 -preset {FFMPEG_COMPRESSION_PRESET} -crf {target_size}"
    )

    ff = ffmpy.FFmpeg(
        executable='ffmpeg',
        inputs={BASE_DIR / "media" / video_file_path: "-y -hide_banner -nostats -loglevel warning -threads 6"},
        outputs={path_to_file: ffmpeg_output_parameters},
    )
    try:
        ff.run() # сжатие файла

        cache.set(file_identifier, FileStatus.READY)
        group_name = get_channel_video_group_name(file_identifier)

        # ссылка для скачивания не должна включать базовую папку проекта
        send_video_ready_msg(group_name,
                             path_to_file=str(path_to_file).replace('/code', ''))
        # удаляем через 90 секунд
        delete_file.apply_async((str(path_to_file), file_identifier), countdown=FILE_LIFETIME)

        logger.info('Video compression is successful')
    except ffmpy.FFRuntimeError as e:
        group_name = get_channel_video_group_name(file_identifier)
        cache.set(file_identifier, FileStatus.ERROR)
        send_error_msg(group_name)
        logger.info('Video compression error', exc_info=True)
        return False


@app.task
def delete_file(path_to_file, file_identifier):
    compress_file_to_remove = pathlib.Path(path_to_file)
    temp_file_to_remove = pathlib.Path(path_to_file.replace('/compressed_folder/', '/temp/'))
    try:
        logger.debug(f'Deleting compressed file with path: {path_to_file}')
        compress_file_to_remove.unlink()
        cache.set(file_identifier, FileStatus.DELETED)
    except Exception as e:
        logger.error(f'Error deleting file with path {temp_file_to_remove}', exc_info=True)
        cache.set(file_identifier, FileStatus.ERROR)

    try:
        logger.debug(f'Deleting temp file with path: {temp_file_to_remove}')
        temp_file_to_remove.unlink()
    except Exception as e:
        logger.error(f'Error deleting temp file with path {temp_file_to_remove}', exc_info=True)
