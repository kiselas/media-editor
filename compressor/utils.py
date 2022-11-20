import logging

from django.conf import settings

from .exceptions import InvalidCRFSize

logger = logging.getLogger(__name__)
BASE_DIR = settings.BASE_DIR


def get_crf_for_compression(target_size):
    if isinstance(target_size, int):
        if target_size == 1:
            target_size = 25  # 20%
        elif target_size == 2:
            target_size = 30  # 40%
        elif target_size == 3:
            target_size = 35  # 70%
        elif target_size == 4:
            target_size = 40  # 80%
        elif target_size == 5:
            target_size = 45  # 85%
        elif target_size == 6:
            target_size = 50  # 88%
        else:
            logger.error('Incorrect target size for video')
            target_size = 35
        return target_size
    raise InvalidCRFSize
