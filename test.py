from pathlib import Path

import ffmpy
import logging

from io import StringIO
from PIL import Image
from PIL.Image import Resampling

logger = logging.getLogger()


def convert_video_file(video_file_path, file_identifier, file_format, convert_format):
    logger.info(f'Start converting video from {file_format} to {convert_format}')
    file_name = f'{file_identifier}{convert_format}'

    FULL_PATH_TO_COMPRESSED_FILES = Path('/home/kisel/Рабочий стол/')
    if not FULL_PATH_TO_COMPRESSED_FILES.is_dir():
        FULL_PATH_TO_COMPRESSED_FILES.mkdir()

    path_to_file = FULL_PATH_TO_COMPRESSED_FILES / file_name

    convert_format_parameters = {
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
    ffmpeg_output_parameters = \
        convert_format_parameters.get(file_format, {}).get(convert_format, '-q 1 -c copy')
    print(ffmpeg_output_parameters)
    ffmpeg_input_parameters = "-y -hide_banner -nostats -loglevel warning -threads 6"

    ff = ffmpy.FFmpeg(
        executable='ffmpeg',
        inputs={video_file_path: ffmpeg_input_parameters},
        outputs={path_to_file: ffmpeg_output_parameters},
    )
    try:
        ff.run() # сжатие файла

        # cache.set(file_identifier, FileStatus.READY)
        # group_name = get_channel_video_group_name(file_identifier)

        # ссылка для скачивания не должна включать базовую папку проекта
        # send_video_ready_msg(group_name,
        #                      path_to_file=str(path_to_file).replace('/code', ''))
        # удаляем через 90 секунд
        # delete_file.apply_async((str(path_to_file), file_identifier), countdown=FILE_LIFETIME)

        print('Video compression is successful')
    except ffmpy.FFRuntimeError as e:
        # group_name = get_channel_video_group_name(file_identifier)
        # cache.set(file_identifier, FileStatus.ERROR)
        # send_error_msg(group_name)
        logger.info('Video compression error', exc_info=True)
        return False

# compress_video_file('/home/kisel/Рабочий стол/тест.mp4', 6)

# convert_video_file('/home/kisel/Рабочий стол/тест.flv', 'test_flv_to_webm', '.flv', '.webm')


def compress_image(path_to_file, target_size):
    target_size = target_size/100
    foo = Image.open(path_to_file)  # My image is a 200x374 jpeg that is 102kb large
    new_size = (int(foo.size[0] * target_size), int(foo.size[1] * target_size))  # (400 * 0.5, 800 * 0.5)
    print(new_size)

    # downsize the image with an ANTIALIAS filter (gives the highest quality)
    foo = foo.resize(new_size, Resampling.LANCZOS)

    foo.save('/home/kisel/Рабочий стол/image_scaled.jpg', quality=95)

    foo.save('/home/kisel/Рабочий стол/image_scaled_opt.jpg', optimize=True, quality=95)


compress_image('/home/kisel/Рабочий стол/test_img_4k.jpg', 90)