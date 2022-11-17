import os
import requests
from pydub import AudioSegment

AUDIO_INPUT_PATH = "input/audio.mp3"
SUBTITLE_INPUT_PATH = "input/subtitle.txt"
FOG_API_ENDPOINT = "http://localhost:81/api/sync"
CLOUD_API_ENDPOINT = "http://172.17.90.194:81/api/sync"

def sendto(audio, subtitle, api_endpoint):
	response = requests.post(url = api_endpoint, files={'audio': audio, 'subtitle': subtitle})
	return response.content

def readfile(filepath):
	try:
		with open(filepath, "rb") as f:
			b = f.read(1)
			mybytearray = bytearray()
			while b:
				mybytearray += b
				b = f.read(1)
	except IOError:
		raise Exception('Error While Opening the file!')  

def main():
	subtitle = readfile(SUBTITLE_INPUT_PATH)
	#audio = readfile(AUDIO_INPUT_PATH)
	audio = AudioSegment.from_mp3(AUDIO_INPUT_PATH)
	audio_slices = audio[::10000]

	for index, chunk in enumerate(audio_slices):
		response = "EMPTY RESPONSE"

		# read audio slice
		audio_slice_path = f'sound_{index}.mp3'		
		with open(audio_slice_path, "wb") as f:
			chunk.export(f, format="mp3")
		audio_slice = readfile(audio_slice_path)

		# read subtitle slice
		## TODO

		# send to fog
		if (index % 2 == 0):
			print("SENDING TO FOG")
			response = sendto(audio_slice, subtitle, FOG_API_ENDPOINT)
			print("RETRIEVING FROM FOG")
		# send to cloud
		else:
			print("SENDING TO CLOUD")
			response = sendto(audio_slice, subtitle, CLOUD_API_ENDPOINT)
			print("RETRIEVING FROM CLOUD")

		#os.remove(audio_slice_path)
		print(response)

if __name__ == '__main__':
	main()