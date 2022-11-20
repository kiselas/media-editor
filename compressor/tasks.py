import logging

import ffmpy
from django.conf import settings

from compressor.utils import get_crf_for_compression
from django_celery.celery import app
from ws_app.consumers import send_video_ready_msg, get_channel_video_group_name


class InvalidCRFSize(Exception):
    """Raised when the input size invalid"""
    pass


logger = logging.getLogger(__name__)
BASE_DIR = settings.BASE_DIR


@app.task
def compress_video_file(video_file_path, file_identifier, target_size):
    logger.info('Start compressing video')
    target_size = get_crf_for_compression(target_size)
    file_name = f'{file_identifier}.mp4'

    # folder to save extracted images
    output_folder_for_compressed_videos = BASE_DIR / "media" / "compressed_folder"
    out_dir_path = BASE_DIR / output_folder_for_compressed_videos
    logger.info(f'output_folder_for_compressed_videos {output_folder_for_compressed_videos}')
    logger.info(f'out_dir_path {out_dir_path}')
    logger.info(f'video_file_path {video_file_path}')
    if not out_dir_path.is_dir():
        out_dir_path.mkdir()

    ffmpeg_output_parameters = (
        # "-s " + '854x480 ' + "-crf " + str(target_size)
        f"-c:v libx264 -preset veryslow -crf {target_size}"
    )

    ff = ffmpy.FFmpeg(
        executable='ffmpeg',
        inputs={BASE_DIR / "media" / video_file_path: "-y -hide_banner -nostats"},
        outputs={out_dir_path / file_name: ffmpeg_output_parameters},
    )
    try:
        ff.run()
        group_name = get_channel_video_group_name(file_identifier)
        send_video_ready_msg(group_name, path_to_file=str(out_dir_path / file_name).replace('/code', ''))
        logger.info('Video compression is successful')
    except ffmpy.FFRuntimeError as e:
        logger.info('Video compression error')
        logger.error(e, exc_info=True)
        return False
