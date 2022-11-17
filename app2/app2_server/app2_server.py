"""
python -m aeneas.tools.execute_task \
    ../p001.mp3 \
    ../p001.xhtml \
    "task_language=eng|os_task_file_format=json|is_text_type=plain" \
    ../map.json
"""

import os
import uuid
import aeneas.tools.execute_task as aat
from flask import Flask, request, Response, jsonify

def save_file(file_path, file_bytes):
	with open(file_path, "wb") as binary_file:
		binary_file.write(file_bytes)

app = Flask(__name__)

@app.route('/api/sync', methods=['POST'])
def main():
	mainfolder = '..'
	audio_ext = 'mp3'
	subtitle_ext = 'xhtml'
	output_ext = 'json'

	unique_filename = str(uuid.uuid4())

	audio_path = f'{mainfolder}/{unique_filename}.{audio_ext}'
	subtitle_path = f'{mainfolder}/{unique_filename}.{subtitle_ext}'
	output_path = f'{mainfolder}/{unique_filename}.{output_ext}'
	cfg = 'task_language=eng|os_task_file_format=json|is_text_type=plain'

	audio_file = request.files["audio"].read()
	subtitle_file = request.files["subtitle"].read()

	save_file(audio_path, audio_file)
	save_file(subtitle_path, subtitle_file)

	aat.ExecuteTaskCLI().run(arguments=['', audio_path, subtitle_path, cfg, output_path])

	output_content = ''
	if(os.path.exists(output_path)): 
		with open(output_path, "r") as txt_file:
			output_content = txt_file.readlines()
		os.remove(output_path)
	if(os.path.exists(audio_path)):
		os.remove(audio_path)
	if(os.path.exists(subtitle_path)):
		os.remove(subtitle_path)

	return Response(response = output_content, status = 200, mimetype = "application/json")



if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
