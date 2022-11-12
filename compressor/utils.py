import logging

import ffmpy
from django.conf import settings
import uuid


logger = logging.getLogger(__name__)
BASE_DIR = settings.BASE_DIR


def compress_video_file(video_file, target_size):
    if target_size == 1:
        target_size = 25 # 20%
    elif target_size == 2:
        target_size = 30 # 40%
    elif target_size == 3:
        target_size = 35 # 70%
    elif target_size == 4:
        target_size = 40 # 80%
    elif target_size == 5:
        target_size = 45 # 85%
    elif target_size == 6:
        target_size = 50 # 88%
    else:
        logger.error('Incorrect target size for video')
        target_size = 35
    file_identifier = f"{uuid.uuid4()}.mp4"

    # folder to save extracted images
    output_folder_for_compressed_videos = BASE_DIR / "media" / "compressed_folder"
    out_dir_path = BASE_DIR / output_folder_for_compressed_videos
    if not out_dir_path.is_dir():
        out_dir_path.mkdir()

    ffmpeg_output_parameters = (
            # "-s " + '854x480 ' + "-crf " + str(target_size)
            f"-c:v libx264 -preset veryslow -crf {target_size}"
    )

    ff = ffmpy.FFmpeg(
        executable='ffmpeg',
        inputs={video_file.temporary_file_path(): "-y -hide_banner -nostats -loglevel panic"},
        outputs={out_dir_path / file_identifier: ffmpeg_output_parameters},
    )
    try:
        ff.run()
    except ffmpy.FFRuntimeError as e:
        logger.error(e, exc_info=True)
        return False

    return file_identifier


