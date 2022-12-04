from pathlib import Path

from django_video_converter.settings import BASE_DIR

PATH_TO_COMPRESSED_FILES = "media/compressed_folder/"
FULL_PATH_TO_COMPRESSED_FILES: Path = BASE_DIR / "media/compressed_folder/"
AVAILABLE_VIDEO_FORMATS = ['.avi', '.mkv', '.mov', '.mkv', '.mp4']
MAX_VIDEO_SIZE = 400 * 1024 * 1024 # 400 мегабайт

class FileStatus:
    IN_PROCESS = "1"
    READY = "2"
    DELETED = "3"
    ERROR = "4"
