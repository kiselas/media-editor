import logging
from pathlib import Path

from django.conf import settings

from .exceptions import InvalidCRFSize

logger = logging.getLogger(__name__)
BASE_DIR = settings.BASE_DIR


def get_crf_for_compression(target_size):
    if isinstance(target_size, str):
        if target_size == '0':
            target_size = 25  # 20%
            logger.info('Selected 25 target size')
        elif target_size == '1':
            target_size = 30  # 40%
            logger.info('Selected 30 target size')
        elif target_size == '2':
            target_size = 35  # 70%
            logger.info('Selected 35 target size')
        elif target_size == '3':
            target_size = 40  # 80%
            logger.info('Selected 40 target size')
        elif target_size == '4':
            target_size = 45  # 85%
            logger.info('Selected 45 target size')
        elif target_size == '5':
            target_size = 50  # 88%
            logger.info('Selected 50 target size')
        else:
            logger.error(f'Incorrect target size for video {target_size}')
            target_size = 30
    else:
        logger.error(f'Incorrect target size type {target_size} - {type(target_size)} for video ')
        target_size = 30
    return target_size


def check_video_is_ready(file_identifier: str, path_to_dir) -> bool:
    output_folder_for_compressed_videos = BASE_DIR / path_to_dir / f'{file_identifier}.mp4'
    return output_folder_for_compressed_videos.exists()


def get_path_to_file(file_identifier: str, path_to_dir) -> str:
    output_folder_for_compressed_videos = BASE_DIR / path_to_dir / f'{file_identifier}.mp4'
    return output_folder_for_compressed_videos


def mark_ready(file_path):
    file_name = file_path.name.replace('_processing', '')
    new_file_path = file_path.rename(Path(file_path.parent, f"{file_name}"))
    logger.info('File marked as ready')
    return new_file_path


def get_file_format(file_from_request):
    try:
        file_type = file_from_request.name.rsplit('.', 1)[-1]
        return f'.{file_type}'
    except ValueError:
        logger.error("File doesn't have type")


