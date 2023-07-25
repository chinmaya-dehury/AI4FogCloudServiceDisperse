import os
import time
import json
import requests
from pydub import AudioSegment



###################################################################### CONSTANTS
INPUT_FOLDER = "input/input2"
INPUT_AUDIO_FILE_NAME = "movie_audio.mp3"
INPUT_SUBTITLE_FILE_NAME = "movie_subtitle.txt"
INPUT_AUDIO_PATH = f"{INPUT_FOLDER}/{INPUT_AUDIO_FILE_NAME}"
INPUT_SUBTITLE_PATH = f"{INPUT_FOLDER}/{INPUT_SUBTITLE_FILE_NAME}"
INPUT_AUDIO_CHUNKS_PATH = f"{INPUT_FOLDER}/audio_chunks/{INPUT_AUDIO_FILE_NAME}"
INPUT_SUBTITLE_CHUNKS_PATH = f"{INPUT_FOLDER}/subtitle_chunks/{INPUT_SUBTITLE_FILE_NAME}"


OUTPUT_FOLDER = "output/output2"
OUTPUT_SUBTITLE_FILE_NAME = "video.srt"
OUTPUT_SUBTITLE_PATH = f"{OUTPUT_FOLDER}/{OUTPUT_SUBTITLE_FILE_NAME}"

FOG_API_ENDPOINT = "http://172.17.142.22:30001/api/sync"
CLOUD_API_ENDPOINT = "http://172.17.90.194:81/api/sync"


###################################################################### AUDIO SLICING
def get_audio_slices():
	audio = AudioSegment.from_mp3(INPUT_AUDIO_PATH)
	audio_slices = audio[::15000]
	return audio_slices

def get_count_of_audio_slices():
	audio_slices = get_audio_slices()
	length = len(list(audio_slices))
	return length

def split_audios():
	audio_slices = get_audio_slices()

	for index, chunk in enumerate(audio_slices):
		# write audio slice
		audio_slice_path = f"{INPUT_AUDIO_CHUNKS_PATH}_{index}.mp3"	
		with open(audio_slice_path, "wb") as f:
			chunk.export(f, format="mp3")
		


###################################################################### SUBTITLE SLICING
def readsubtitles(filepath):
	with open(filepath, 'r') as f:
		lines = f.readlines()
	return lines

def split_subtitles(slice_counter):
	subtitle_slices = split_subtitles_helper(readsubtitles(INPUT_SUBTITLE_PATH), slice_counter)

	for index in range(slice_counter):
		# write subtitle slice
		subtitle_slice_path = f"{INPUT_SUBTITLE_CHUNKS_PATH}_{index}.txt"
		with open(subtitle_slice_path, "w") as f:
			for subtitle in list(subtitle_slices[index]):
				f.write(subtitle)

def split_subtitles_helper(a, n):
    k, m = divmod(len(a), n)
    return [a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n)]


###################################################################### SYNC PART
def sendto(audio_path, subtitle_path, api_endpoint):
	files = {
		'audio': open(audio_path, 'rb'),
		'subtitle': open(subtitle_path, 'rb'),
	}
	response = requests.post(url = api_endpoint, files=files)
	return response.content


###################################################################### OUTPUT MERGING
def get_as_list(jsonfile):
	jsonfile = jsonfile.decode('utf8')
	myjson = json.loads(jsonfile)
	return myjson['fragments']

def change_format(sec, offset):
	sec = sec.split('.')
	s = int(sec[0]) + offset
	ms = sec[1]
	st = f"{time.strftime('%H:%M:%S', time.gmtime(s))},{ms}"
	return st

def convert_to_subtitles(line_counter, jsonfile, offset, filepath):
	l = get_as_list(jsonfile)

	for i in l:
		line_counter += 1
		begin = change_format(i['begin'], offset)
		end = change_format(i['end'], offset)
		lines = i['lines']

		subtitle = f"{line_counter}\n"
		subtitle += f"{begin} --> {end}"
		for line in lines:
			subtitle += f"\n{line}"
		subtitle += "\n\n"
		with open(filepath, 'a') as f: f.write(subtitle)
	
	return line_counter


def main():
	slice_counter = get_count_of_audio_slices()

	print("SPLITTING audios")
	split_audios()

	print("SPLITTING subtitles")
	split_subtitles(slice_counter)

	print("SENDING api is started")
	line_counter = 0
	for index in range(slice_counter):
		response = "EMPTY RESPONSE"

		# audio slice
		audio_slice_path = f"{INPUT_AUDIO_CHUNKS_PATH}_{index}.mp3"

		# subtitle slice
		subtitle_slice_path = f"{INPUT_SUBTITLE_CHUNKS_PATH}_{index}.txt"

		# send to fog
		if (index % 2 == 0):
			print("SENDING TO FOG")
			response = sendto(audio_slice_path, subtitle_slice_path, FOG_API_ENDPOINT)
			print("RETRIEVING FROM FOG")
		# send to cloud
		else:
			print("SENDING TO CLOUD")
			response = sendto(audio_slice_path, subtitle_slice_path, CLOUD_API_ENDPOINT)
			print("RETRIEVING FROM CLOUD")

		# merging
		offset = index * 10
		line_counter = convert_to_subtitles(line_counter, response, offset, OUTPUT_SUBTITLE_PATH)

		# remove slices
		os.remove(audio_slice_path)
		os.remove(subtitle_slice_path)


if __name__ == '__main__':
	main()