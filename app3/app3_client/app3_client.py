import os
import time
import json
import requests
from pydub import AudioSegment


###################################################################### CONSTANTS
INPUT_FOLDER = "input/input1"
INPUT_AUDIO_FILE_NAME = "simple_audio.wav"
INPUT_AUDIO_PATH = f"{INPUT_FOLDER}/{INPUT_AUDIO_FILE_NAME}"
INPUT_AUDIO_CHUNKS_PATH = f"{INPUT_FOLDER}/audio_chunks/{INPUT_AUDIO_FILE_NAME}"

OUTPUT_FOLDER = "output/output1"
OUTPUT_SUBTITLE_FILE_NAME = "video.txt"
OUTPUT_SUBTITLE_PATH = f"{OUTPUT_FOLDER}/{OUTPUT_SUBTITLE_FILE_NAME}"

FOG_API_ENDPOINT = "http://172.17.142.22:30002/api/sync"
CLOUD_API_ENDPOINT = "http://172.17.90.194:83/api/sync"


###################################################################### AUDIO SLICING
def get_audio_slices():
	audio = AudioSegment.from_wav(INPUT_AUDIO_PATH)
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
		audio_slice_path = f"{INPUT_AUDIO_CHUNKS_PATH}_{index}.wav"	
		with open(audio_slice_path, "wb") as f:
			chunk.export(f, format="wav")
		
###################################################################### SYNC PART
def sendto(audio_path, api_endpoint):
	files = {
		'audio': open(audio_path, 'rb')
	}
	response = requests.post(url = api_endpoint, files=files)
	return response.content


def main():
	slice_counter = get_count_of_audio_slices()

	print("SPLITTING audios")
	split_audios()

	print("SENDING api is started")

	output = ''

	for index in range(slice_counter):
		response = "EMPTY RESPONSE"

		# audio slice
		audio_slice_path = f"{INPUT_AUDIO_CHUNKS_PATH}_{index}.wav"

		# send to fog
		if (index % 2 == 0):
			print("SENDING TO FOG")
			response = sendto(audio_slice_path, FOG_API_ENDPOINT)
			print("RETRIEVING FROM FOG")
		# send to cloud
		else:
			print("SENDING TO CLOUD")
			response = sendto(audio_slice_path, CLOUD_API_ENDPOINT)
			print("RETRIEVING FROM CLOUD")

		# save output
		output += response.decode("utf-8")

		# remove slices
		os.remove(audio_slice_path)

	print(output)

if __name__ == '__main__':
	main()