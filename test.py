from PIL import Image

def image_converter(image, new_format):
  # Import the required library

  img = Image.open(image)

  # Split the image name and its extension
  name, extension = image.split('.')
  extension = extension.lower()

  if extension == 'png':
    img = img.convert('RGB')

  # Create new image name with the new format
  new_image = f'{name}.{new_format}'

  # Save the new image
  img.save(f'{new_image}')

  return f'Image converted to {new_format} successfully'


image_converter('/home/kisel/Рабочий стол/test.png', 'jpg')


def convert_image_file(path_to_original_file, file_identifier, file_format, convert_format):
  logger.info(f'Start converting video from {file_format} to {convert_format}')
  file_name = f'{file_identifier}{convert_format}'
  path_to_original_file = BASE_DIR / "media" / path_to_original_file

  if not FULL_PATH_TO_PROCESSED_FILES.is_dir():
    FULL_PATH_TO_PROCESSED_FILES.mkdir()

  path_to_processed_file = FULL_PATH_TO_PROCESSED_FILES / file_name

  try:
    img = Image.open(path_to_original_file)
    if extension == '.png':
      img = img.convert('RGB')

    new_image = path_to_processed_file
    img.save(f'{new_image}')
      
    logger.info(f'Set cache for {file_identifier} to {FileStatus.READY},{convert_format}')
    cache.set(file_identifier, f'{FileStatus.READY},{convert_format}')
    group_name = get_channel_video_group_name(file_identifier)

    # ссылка для скачивания не должна включать базовую папку проекта
    logger.info('Try to send ws message')
    send_video_ready_msg(group_name,
                         path_to_file=str(path_to_processed_file).replace('/code', ''))
    delete_file.apply_async((str(path_to_processed_file), file_identifier), countdown=FILE_LIFETIME)

    print('File convertation is successful')
  except Exception as e:
    group_name = get_channel_video_group_name(file_identifier)
    cache.set(file_identifier, f'{FileStatus.ERROR},{convert_format}')
    send_error_msg(group_name)
    logger.info('File convertation error', exc_info=True)
    return False


