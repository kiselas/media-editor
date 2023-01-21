from django_media_editor.constants import MAX_VIDEO_TO_GIF_DURATION, AVAILABLE_QUANTIZE_ALGORITHMS
from PIL import Image, ImageSequence


def validate_video_to_gif_data(start_time, file_duration, end_time, quantize_algorithm):
    duration = end_time - start_time
    if duration > MAX_VIDEO_TO_GIF_DURATION:
        raise AttributeError('Duration cant be bigger than MAX_VIDEO_TO_GIF_DURATION')
    if file_duration < end_time:
        raise AttributeError(f'End time ({end_time}) cant be bigger than video duration ({file_duration})')
    if start_time < 0:
        raise AttributeError(f'Variable start ({start_time}) cant be less than 0')
    if start_time > file_duration:
        raise AttributeError(f'Start cant ({start_time}) be bigger than video duration ({file_duration})')
    if start_time >= end_time:
        raise AttributeError(f'Start time ({start_time}) cant be bigger than end time ({end_time})')
    if quantize_algorithm not in AVAILABLE_QUANTIZE_ALGORITHMS:
        raise AttributeError('Unkown quantize algorithm')


def compress_gif(image_path):
    # open the gif
    gif = Image.open(image_path)
    width, height = gif.size
    if width > 1920:
        scale = 0.2
    elif width > 1280:
        scale = 0.5
    elif width > 854:
        scale = 0.7
    else:
        return True

    new_width, new_height = int(width * scale), int(height * scale)

    def thumbnails(img_frames):
        for frame in img_frames:
            thumbnail = frame.copy()
            thumbnail.thumbnail((new_width, new_height), Image.ANTIALIAS)
            yield thumbnail

    # resize the gif
    im = Image.open(image_path)
    frames = ImageSequence.Iterator(im)

    # save the compressed gif to the output path
    frames = thumbnails(frames)
    om = next(frames)  # Handle first frame separately
    om.info = im.info  # Copy sequence info
    om.save(image_path, save_all=True, append_images=list(frames))
    return True

