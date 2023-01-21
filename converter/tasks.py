
import logging

import ffmpy
from PIL import Image
from django.conf import settings
from django.core.cache import cache

from django_celery.celery import app
from django_media_editor.constants import FileStatus, FULL_PATH_TO_PROCESSED_FILES, CONVERT_FORMAT_PARAMETERS, \
    FILE_LIFETIME
from django_media_editor.tasks import delete_file
from ws_app.consumers import send_video_ready_msg, get_channel_video_group_name, send_error_msg

BASE_DIR = settings.BASE_DIR
logger = logging.getLogger(__name__)


@app.task
def convert_video_file(video_file_path, file_identifier, file_format, convert_format):
    logger.info(f'Start converting video from {file_format} to {convert_format}')
    file_name = f'{file_identifier}{convert_format}'

    if not FULL_PATH_TO_PROCESSED_FILES.is_dir():
        FULL_PATH_TO_PROCESSED_FILES.mkdir()

    path_to_file = FULL_PATH_TO_PROCESSED_FILES / file_name

    ffmpeg_output_parameters = \
        CONVERT_FORMAT_PARAMETERS.get(file_format, {}).get(convert_format, '-q 1 -c copy')

    ffmpeg_input_parameters = "-y -hide_banner -nostats -loglevel warning -threads 6"

    ff = ffmpy.FFmpeg(
        executable='ffmpeg',
        inputs={BASE_DIR / "media" / video_file_path: ffmpeg_input_parameters},
        outputs={path_to_file: ffmpeg_output_parameters},
    )
    try:
        ff.run()
        logger.info(f'Set cache for {file_identifier} to {FileStatus.READY},{convert_format}')
        cache.set(file_identifier, f'{FileStatus.READY},{convert_format}')
        group_name = get_channel_video_group_name(file_identifier)

        # ссылка для скачивания не должна включать базовую папку проекта
        logger.info('Try to send ws message')
        send_video_ready_msg(group_name,
                             path_to_file=str(path_to_file).replace('/code', ''))
        delete_file.apply_async((str(path_to_file), file_identifier), countdown=FILE_LIFETIME)

        print('Video convertation is successful')
    except ffmpy.FFRuntimeError as e:
        group_name = get_channel_video_group_name(file_identifier)
        cache.set(file_identifier, f'{FileStatus.ERROR},{convert_format}')
        send_error_msg(group_name)
        logger.info('Video convertation error', exc_info=True)
        return False


@app.task
def convert_image_file(path_to_original_file, file_identifier, file_format, convert_format):
    logger.info(f'Start converting image from {file_format} to {convert_format}')
    file_name = f'{file_identifier}{convert_format}'
    path_to_original_file = BASE_DIR / "media" / path_to_original_file

    if not FULL_PATH_TO_PROCESSED_FILES.is_dir():
        FULL_PATH_TO_PROCESSED_FILES.mkdir()

    path_to_processed_file = FULL_PATH_TO_PROCESSED_FILES / file_name

    try:
        img = Image.open(path_to_original_file)
        if file_format == '.png':
            img = img.convert('RGB')

        new_image = path_to_processed_file
        img.save(f'{new_image}')

        logger.info(f'Set cache for {file_identifier} to {FileStatus.READY},{convert_format}')
        cache.set(file_identifier, f'{FileStatus.READY},{convert_format}')
        group_name = get_channel_video_group_name(file_identifier)

        # ссылка для скачивания не должна включать базовую папку проекта
        logger.info('Try to send ws message')
        send_video_ready_msg(group_name,
                             path_to_file=str(path_to_processed_file).replace('/code', ''))
        delete_file.apply_async((str(path_to_processed_file), file_identifier), countdown=FILE_LIFETIME)

        print('File convertation is successful')
    except Exception as e:
        group_name = get_channel_video_group_name(file_identifier)
        cache.set(file_identifier, f'{FileStatus.ERROR},{convert_format}')
        send_error_msg(group_name)
        logger.info('Image convertation error', exc_info=True)
        return False