import logging

import ffmpy
import time
from django.conf import settings
from django.core.cache import cache

from compressor.constants import PATH_TO_COMPRESSED_VIDEO, FileStatus
from compressor.utils import get_crf_for_compression, mark_ready
from django_celery.celery import app
from ws_app.consumers import send_video_ready_msg, get_channel_video_group_name, send_error_msg


class InvalidCRFSize(Exception):
    """Raised when the input size invalid"""
    pass


logger = logging.getLogger(__name__)
BASE_DIR = settings.BASE_DIR
FFMPEG_COMPRESSION_PRESET = 'superfast' # slow, medium, fast, superfast


@app.task
def compress_video_file(video_file_path, file_identifier, target_size, file_format):
    logger.info(f'Start compressing video with preset {FFMPEG_COMPRESSION_PRESET}')
    target_size = get_crf_for_compression(target_size)
    file_name = f'{file_identifier}{file_format}'

    output_folder_for_compressed_videos = BASE_DIR / PATH_TO_COMPRESSED_VIDEO
    if not output_folder_for_compressed_videos.is_dir():
        output_folder_for_compressed_videos.mkdir()

    ffmpeg_output_parameters = (
        # "-s " + '854x480 ' + "-crf " + str(target_size)
        f"-c:v libx264 -preset {FFMPEG_COMPRESSION_PRESET} -crf {target_size}"
    )

    ff = ffmpy.FFmpeg(
        executable='ffmpeg',
        inputs={BASE_DIR / "media" / video_file_path: "-y -hide_banner -nostats -loglevel warning -threads 6"},
        outputs={output_folder_for_compressed_videos / file_name: ffmpeg_output_parameters},
    )
    try:
        ff.run()
        cache.set(file_identifier, FileStatus.READY)
        group_name = get_channel_video_group_name(file_identifier)
        send_video_ready_msg(group_name,
                             path_to_file=str(output_folder_for_compressed_videos / file_name).replace('/code', ''))
        logger.info('Video compression is successful')
    except ffmpy.FFRuntimeError as e:
        group_name = get_channel_video_group_name(file_identifier)
        cache.set(file_identifier, FileStatus.ERROR)
        send_error_msg(group_name,
                             path_to_file=str(output_folder_for_compressed_videos / file_name).replace('/code', ''))
        logger.info('Video compression error')
        logger.error(e, exc_info=True)
        return False
