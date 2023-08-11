import os
import uuid
import time
import psutil
from pydub import AudioSegment
from flask_caching import Cache
import aeneas.tools.execute_task as aat
from flask import Flask, request, Response, jsonify

# Initialize the Flask application
app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})  

# Caching logic
KEY_TOTAL_CPU_USAGE = "TOTAL_CPU_USAGE"
KEY_TOTAL_MEMORY_USAGE = "TOTAL_MEMORY_USAGE"
def get_from_cache(key):
    return cache.get(key)
def set_to_cache(key, value):
    cache.set(key, value)
def metrics_normalizer(start, end):
	return abs(max(start, end) - min(start, end))
def measure_metrics(func, value1, value2):
    # measure CPU usage during the function call
    start_cpu_usage = psutil.cpu_percent(interval=None)
    start_cpu_time = time.perf_counter()

    # measure memory usage during the function call
    start_mem_info = psutil.Process().memory_info()

    output, total_throughput = func(value1, value2)

    # get cpu usage
    end_cpu_usage = psutil.cpu_percent(interval=None)
    end_cpu_time = time.perf_counter()
    total_cpu_usage = metrics_normalizer(start_cpu_usage, end_cpu_usage)

    # get memory usage
    end_mem_info = psutil.Process().memory_info()
    total_memory_usage = metrics_normalizer(start_mem_info.rss, end_mem_info.rss) / 1_000_000 # convert bytes to MB

    return output, round(total_cpu_usage, 3), round(total_memory_usage, 3), round(total_throughput, 3)

def save_file(file_path, file_bytes):
	with open(file_path, "wb") as binary_file:
		binary_file.write(file_bytes)
def run_detection(audio_file, subtitle_file):
	start_throughput_time = time.time()
	mainfolder = '..'
	audio_ext = 'mp3'
	subtitle_ext = 'txt'
	output_ext = 'json'

	unique_filename = str(uuid.uuid4())

	audio_path = f'{mainfolder}/{unique_filename}.{audio_ext}'
	subtitle_path = f'{mainfolder}/{unique_filename}.{subtitle_ext}'
	output_path = f'{mainfolder}/{unique_filename}.{output_ext}'
	cfg = f'task_language=eng|os_task_file_format={output_ext}|is_text_type=plain'


	save_file(audio_path, audio_file)
	save_file(subtitle_path, subtitle_file)

	# calculate total len of input
	subtitle = ""
	with open(subtitle_path, "r", encoding="utf-8") as file:
		for line in file:
			subtitle += f"{line.strip()} "
	subtitle_sr_len = len(subtitle.split(" "))
	audio = AudioSegment.from_file(audio_path)
	audio_len = len(audio) / 1000 # convert milliseconds to seconds
	total_frames = audio_len + subtitle_sr_len

	aat.ExecuteTaskCLI().run(arguments=['', audio_path, subtitle_path, cfg, output_path])

    # measure throughput
	end_throughput_time = time.time()
	total_throughput = total_frames / (end_throughput_time-start_throughput_time)


	output_content = ''
	if(os.path.exists(output_path)): 
		with open(output_path, "r") as txt_file:
			output_content = txt_file.readlines()
		os.remove(output_path)
	if(os.path.exists(audio_path)):
		os.remove(audio_path)
	if(os.path.exists(subtitle_path)):
		os.remove(subtitle_path)
	
	return output_content, total_throughput

@app.route('/api/sync', methods=['POST'])
def detect():
    # measure communication time    
	request_receive_time = time.time()

	audio_file = request.files["audio"].read()
	subtitle_file = request.files["subtitle"].read()
	
	output, total_cpu_usage, total_memory_usage, total_throughput = measure_metrics(run_detection, audio_file, subtitle_file)

	response = {
		'output': output,
        'total_cpu_usage': total_cpu_usage, 
        'total_memory_usage': total_memory_usage,
        'total_throughput': total_throughput,
        'request_receive_time': request_receive_time
	}

	return jsonify(response)

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
