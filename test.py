import imageio
import os
from pygifsicle import optimize

def video_to_gif(input_video_file, output_gif_file, start, duration):
    clip = os.path.abspath(input_video_file)
    output_file = os.path.abspath(output_gif_file)

    reader = imageio.get_reader(clip)

    fps = reader.get_meta_data()['fps']/1.2 # Меньше кадров - быстрее обработкка
    print(fps)
    print(reader.get_meta_data()['duration'])
    writer = imageio.get_writer(output_file, fps=fps, palettesize=256)
    for frames in range(int(start*fps), int(start*fps) + int(duration*fps)):
        image = reader.get_data(frames)
        writer.append_data(image)
        print(f'Procesing....{frames}')

    writer.close()
    optimize(output_gif_file)

video_to_gif("/home/kisel/Рабочий стол/test.mp4", "/home/kisel/Рабочий стол/output_not_optimized.gif", 0, 2)