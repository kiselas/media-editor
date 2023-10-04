
import logging
import time

import ffmpy
import imageio as imageio
from django.conf import settings
from django.core.cache import cache
from PIL import Image
from pygifsicle import optimize

from converter.utils import compress_gif, validate_video_to_gif_data
from django_celery.celery import app
from django_media_editor.constants import (
    CONVERT_FORMAT_PARAMETERS,
    FILE_LIFETIME,
    FULL_PATH_TO_PROCESSED_FILES,
    FileStatus,
)
from django_media_editor.tasks import delete_file
from ws_app.consumers import get_channel_video_group_name, send_error_msg, send_video_ready_msg

BASE_DIR = settings.BASE_DIR
logger = logging.getLogger(__name__)


@app.task
def convert_video_file(video_file_path, file_identifier, file_format, convert_format):
    logger.info(f"Start converting video from {file_format} to {convert_format}")
    file_name = f"{file_identifier}{convert_format}"

    if not FULL_PATH_TO_PROCESSED_FILES.is_dir():
        FULL_PATH_TO_PROCESSED_FILES.mkdir()

    path_to_file = FULL_PATH_TO_PROCESSED_FILES / file_name

    ffmpeg_output_parameters = \
        CONVERT_FORMAT_PARAMETERS.get(file_format, {}).get(convert_format, "-q 1 -c copy")

    ffmpeg_input_parameters = "-y -hide_banner -nostats -loglevel warning -threads 6"

    ff = ffmpy.FFmpeg(
        executable="ffmpeg",
        inputs={BASE_DIR / "media" / video_file_path: ffmpeg_input_parameters},
        outputs={path_to_file: ffmpeg_output_parameters},
    )
    try:
        ff.run()
        logger.info(f"Set cache for {file_identifier} to {FileStatus.READY},{convert_format}")
        cache.set(file_identifier, f"{FileStatus.READY},{convert_format}")
        group_name = get_channel_video_group_name(file_identifier)

        # ссылка для скачивания не должна включать базовую папку проекта
        logger.info("Try to send ws message")
        send_video_ready_msg(group_name,
                             path_to_file=str(path_to_file).replace("/code", ""))
        delete_file.apply_async((str(path_to_file), file_identifier), countdown=FILE_LIFETIME)

        logger.info("Video convertation is successful")
    except ffmpy.FFRuntimeError:
        group_name = get_channel_video_group_name(file_identifier)
        cache.set(file_identifier, f"{FileStatus.ERROR},{convert_format}")
        send_error_msg(group_name)
        logger.info("Video convertation error", exc_info=True)
        return False


@app.task
def convert_image_file(path_to_original_file, file_identifier, file_format, convert_format):
    logger.info(f"Start converting image from {file_format} to {convert_format}")
    file_name = f"{file_identifier}{convert_format}"
    path_to_original_file = BASE_DIR / "media" / path_to_original_file

    if not FULL_PATH_TO_PROCESSED_FILES.is_dir():
        FULL_PATH_TO_PROCESSED_FILES.mkdir()

    path_to_processed_file = FULL_PATH_TO_PROCESSED_FILES / file_name

    try:
        img = Image.open(path_to_original_file)
        if file_format == ".png":
            img = img.convert("RGB")

        new_image = path_to_processed_file
        img.save(f"{new_image}")

        logger.info(f"Set cache for {file_identifier} to {FileStatus.READY},{convert_format}")
        cache.set(file_identifier, f"{FileStatus.READY},{convert_format}")
        group_name = get_channel_video_group_name(file_identifier)

        # ссылка для скачивания не должна включать базовую папку проекта
        logger.info("Try to send ws message")
        send_video_ready_msg(group_name,
                             path_to_file=str(path_to_processed_file).replace("/code", ""))
        delete_file.apply_async((str(path_to_processed_file), file_identifier), countdown=FILE_LIFETIME)

        logger.info("File convertation is successful")
    except Exception: # noqa BLE001
        group_name = get_channel_video_group_name(file_identifier)
        cache.set(file_identifier, f"{FileStatus.ERROR},{convert_format}")
        send_error_msg(group_name)
        logger.info("Image convertation error", exc_info=True)
        return False


@app.task
def convert_video_to_gif(path_to_original_file, file_identifier, file_format, start_time, end_time, quantize_algorithm):
    logger.info("[video_to_gif] STAGE 0: Start task video to gif convertation")
    start_run_script = time.time()
    video_filename = f"{file_identifier}{file_format}"
    gif_file_name = f"{file_identifier}.gif"
    start_time = int(start_time)
    end_time = int(end_time)
    quantize_algorithm = int(quantize_algorithm)

    if not FULL_PATH_TO_PROCESSED_FILES.is_dir():
        FULL_PATH_TO_PROCESSED_FILES.mkdir()

    path_to_original_file = BASE_DIR / "media" / path_to_original_file
    path_to_processed_video_file = FULL_PATH_TO_PROCESSED_FILES / video_filename
    path_to_processed_gif_file = FULL_PATH_TO_PROCESSED_FILES / gif_file_name
    try:
        reader = imageio.get_reader(path_to_original_file)
        file_duration = reader.get_meta_data()["duration"]
        validate_video_to_gif_data(start_time=start_time,
                                   file_duration=file_duration,
                                   end_time=end_time,
                                   quantize_algorithm=quantize_algorithm)

        logger.info("[video_to_gif] STAGE 1: Convert video to gif")
        reader = imageio.get_reader(path_to_original_file)
        fps = reader.get_meta_data()["fps"]

        writer = imageio.get_writer(path_to_processed_gif_file, fps=fps, quantizer=quantize_algorithm, palettesize=256)
        for frames in range(int(start_time*fps), int(end_time*fps)):
            image = reader.get_data(frames)
            writer.append_data(image)
        writer.close()

        compress_gif(path_to_processed_gif_file)
        optimize(path_to_processed_gif_file)

        file_format = ".gif"
        logger.info(f"Set cache for {file_identifier} to {FileStatus.READY},{file_format}")
        cache.set(file_identifier, f"{FileStatus.READY},{file_format}")
        group_name = get_channel_video_group_name(file_identifier)

        # ссылка для скачивания не должна включать базовую папку проекта
        logger.info("Try to send ws message")
        send_video_ready_msg(group_name,
                             path_to_file=str(path_to_processed_gif_file).replace("/code", ""))
        delete_file.apply_async((str(path_to_processed_gif_file), file_identifier), countdown=FILE_LIFETIME)
        delete_file.apply_async((str(path_to_processed_video_file), file_identifier), countdown=FILE_LIFETIME)

        logger.info("[video_to_gif] STAGE 2: File convertation is successful")
        logger.info(f"[video_to_gif] STATISTICS: Execution time: {round(time.time() - start_run_script, 1)} seconds")

    except Exception:  # noqa BLE001
        group_name = get_channel_video_group_name(file_identifier)
        cache.set(file_identifier, f"{FileStatus.ERROR},{file_format}")
        send_error_msg(group_name)
        logger.info("Video to gif convertation error", exc_info=True)
        return False
