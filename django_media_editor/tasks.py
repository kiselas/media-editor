import logging
import pathlib

from django.core.cache import cache

from django_celery.celery import app
from django_media_editor.constants import FileStatus

logger = logging.getLogger(__name__)


@app.task
def delete_file(path_to_file, file_identifier):
    compress_file_to_remove = pathlib.Path(path_to_file)
    temp_file_to_remove = pathlib.Path(path_to_file.replace("/processed_files/", "/temp/"))
    try:
        logger.debug(f"Deleting compressed file with path: {path_to_file}")
        compress_file_to_remove.unlink()
        cache.set(file_identifier, f"{FileStatus.DELETED},undefined")
    except Exception:
        logger.error(f"Error deleting file with path {temp_file_to_remove}", exc_info=True)
        cache.set(file_identifier, f"{FileStatus.ERROR},undefined")

    try:
        logger.debug(f"Deleting temp file with path: {temp_file_to_remove}")
        temp_file_to_remove.unlink()
    except Exception:
        logger.error(f"Error deleting temp file with path {temp_file_to_remove}", exc_info=True)
