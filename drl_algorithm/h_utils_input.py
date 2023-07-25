import os
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, concatenate_videoclips

def get_file_details(file):
    file_params = input_file.split(".")
    file_name = file_params[0]
    extension = file_params[1]
    file_size = os.path.getsize(file) / (1024*1024)
    return file, file_name, extension, file_size

def increase_file_size(input_file, output_size):
    input_file, input_file_name, extension, input_size = get_file_details(input_file)
    output_file = f"{input_file_name}_{output_size}.{extension}"
    while (output_size >= input_size):
        match extension:
            case 'mp3':
                increase_audio_size(input_file, output_file, extension)
            case 'wav':
                increase_audio_size(input_file, output_file, extension)
            case 'mp4':
                increase_video_size(input_file, output_file)
            case _:
                increase_text_size(input_file, output_file)
        input_file, input_file_name, extension, input_size = get_file_details(output_file)
    return output_file


def increase_audio_size(input_file, output_file, extension):
    audio = AudioSegment.from_file(input_file)
    doubled_audio = audio + audio
    doubled_audio.export(output_file, format=extension)

def increase_video_size(input_file, output_file):
    clip = VideoFileClip(input_file)
    doubled_clip = concatenate_videoclips([clip, clip])
    doubled_clip.write_videofile(output_file)

def increase_text_size(input_file, output_file):
    with open(input_file, 'r') as file:
        text = file.read()
    doubled_text = text * 2
    with open(output_file, 'w') as file:
        file.write(doubled_text)

if __name__ == '__main__':
    params = [
        # ["app1_input.mp4", 200],
        # ["app1_input.mp4", 400],
        # ["app2_audio.mp3", 1],
        ["app2_subtitle.txt", 1],
        ["app3_audio.wav", 1],
    ]

    for param in params:
        input_file = param[0]
        output_size = param[1]
        output_file = increase_file_size(input_file, output_size)
        print(f"Completed: {output_file}")