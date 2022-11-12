from pathlib import Path

import ffmpy
import logging

from django_video_converter.settings import BASE_DIR

logger = logging.getLogger()


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

    # folder to save extracted images
    output_folder_for_compressed_videos = BASE_DIR / "compressed_folder"
    out_dir_path = BASE_DIR / output_folder_for_compressed_videos
    if not out_dir_path.is_dir():
        out_dir_path.mkdir()

    ffmpeg_output_parameters = (
            # "-s " + '854x480 ' + "-crf " + str(target_size)
            f"-c:v libx264 -preset veryslow -crf {target_size}"
    )
    output_file_path = out_dir_path / 'compressed10_processing.mp4'
    unique_name = output_file_path.name
    ff = ffmpy.FFmpeg(
        executable='ffmpeg',
        inputs={video_file: ""},
        outputs={output_file_path: ffmpeg_output_parameters},
    )
    try:
        ff.run()
    except ffmpy.FFRuntimeError as e:
        logger.error(e, exc_info=True)
        return None, None
    output_file_path = mark_ready(output_file_path)
    return unique_name, output_file_path

def mark_ready(file_path):
    file_name = file_path.name.replace('_processing', '')
    file_path.rename(Path(file_path.parent, f"{file_name}"))
    logger.info('File marked as ready')
    return file_path

unique_name, file_path = compress_video_file('/home/kisel/Рабочий стол/тест.mp4', 6)
