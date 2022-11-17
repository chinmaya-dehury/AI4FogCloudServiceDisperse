import io
import cv2
import base64
import requests
import numpy as np
from PIL import Image
from io import BytesIO

VIDEO_INPUT_PATH = "input/traffic.mp4"
FOG_API_ENDPOINT = "http://localhost:80/api/detect"
CLOUD_API_ENDPOINT = "http://172.17.90.194:80/api/detect"

def frame_to_bts(frame):
	_, bts = cv2.imencode('.webp', frame)
	bts = bts.tobytes()
	return bts


def sendto(frame, api_endpoint):
	frame = frame_to_bts(frame)
	response = requests.post(url = api_endpoint, files={'image': frame})
	frame = Image.open(BytesIO(response.content))
	frame = np.array(frame)
	return frame



def main():
	index = 0
	vid = cv2.VideoCapture(VIDEO_INPUT_PATH)
	while(True):
		ret, frame = vid.read()

		# send to fog
		if (index % 2 == 0):
			print("SENDING TO FOG")
			frame = sendto(frame, FOG_API_ENDPOINT)
			print("RETRIEVING FROM FOG")
		# send to cloud
		else:
			print("SENDING TO CLOUD")
			frame = sendto(frame, CLOUD_API_ENDPOINT)
			print("RETRIEVING FROM CLOUD")

		index += 1
		cv2.imshow('frame', frame)

		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	vid.release()
	cv2.destroyAllWindows()

if __name__ == '__main__':
    main()