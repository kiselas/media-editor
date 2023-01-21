from pathlib import Path

from django_media_editor.settings import BASE_DIR

PATH_TO_PROCESSED_FILES = "media/processed_files/"
FULL_PATH_TO_PROCESSED_FILES: Path = BASE_DIR / PATH_TO_PROCESSED_FILES
AVAILABLE_VIDEO_FORMATS = ['.avi', '.mkv', '.mov', '.mkv', '.mp4']
AVAILABLE_IMAGE_FORMATS = ['.jpg', '.png', '.jpeg', '.webp']
VIDEO_QUANTIZE_CHOICES = (
    (0, "Median"),
    (1, "Maximum coverage"),
    (2, "Fast octree"),
)
AVAILABLE_QUANTIZE_ALGORITHMS = [0, 1, 2]

MAX_VIDEO_SIZE = 400 * 1024 * 1024 # 400 мегабайт
MAX_VIDEO_TO_GIF_SIZE = 100 * 1024 * 1024 # 400 мегабайт
MAX_IMAGE_SIZE = 100 * 1024 * 1024 # 100 мегабайт

FFMPEG_COMPRESSION_PRESET = 'superfast'  # slow, medium, fast, superfast
FILE_LIFETIME = 60 * 15  # время жизни файла 15 минут
MAX_VIDEO_TO_GIF_DURATION = 10


class FileStatus:
    IN_PROCESS = "1"
    READY = "2"
    DELETED = "3"
    ERROR = "4"


VIDEO_CONVERTER_CHOICES = (
    (".avi", ".avi"),
    (".mkv", ".mkv"),
    (".mov", ".mov"),
    (".mkv", ".mkv"),
    (".mp4", ".mp4"),
)

IMAGE_CONVERTER_CHOICES = (
    (".jpg", ".jpg"),
    (".png", ".png"),
    (".webp", ".webp"),
)


CONVERT_FORMAT_PARAMETERS = {
        '.webm': {
            '.mp4': '-map 0 -c:v libx264 -c:a aac',
            '.mkv': '-map 0 -c:v libx264 -c:a aac',
            '.mov': '-map 0 -c:v libx264 -c:a aac',
            '.flv': '-map 0 -c:v libx264 -c:a aac',
        },
        '.mp4': {
            '.webm': '-c:v libvpx-vp9',
            '.flv': '-map 0 -c:v libx264 -c:a aac',
        },
        '.mkv': {
            '.webm': '-c:v libvpx-vp9',
            '.flv': '-map 0 -c:v libx264 -c:a aac',
        },
        '.mov': {
            '.webm': '-c:v libvpx-vp9',
            '.flv': '-map 0 -c:v libx264 -c:a aac',
        },
        '.flv': {
            '.mp4': '-c:v libx264 -c:a aac',
            '.mkv': '-c:v libx264 -c:a aac',
            '.mov': '-c:v libx264 -c:a aac',
            '.webm': '-c:v libvpx-vp9'
        },
    }
