import os
import uuid
import time
import psutil
from flask_caching import Cache
import speech_recognition as sr
from flask import Flask, request, Response, jsonify, session

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
def measure_metrics(func, value):
    # measure CPU usage during the function call
    start_cpu_usage = psutil.cpu_percent(interval=None)
    start_cpu_time = time.perf_counter()

    # measure memory usage during the function call
    start_mem_info = psutil.Process().memory_info()

    output = func(value)

    # get cpu usage
    end_cpu_usage = psutil.cpu_percent(interval=None)
    end_cpu_time = time.perf_counter()
    total_cpu_usage = metrics_normalizer(start_cpu_usage, end_cpu_usage)

    # get memory usage
    end_mem_info = psutil.Process().memory_info()
    total_memory_usage = metrics_normalizer(start_mem_info.rss, end_mem_info.rss) / 1_000_000 # convert bytes to MB

    return output, round(total_cpu_usage, 3), round(total_memory_usage, 3)

def save_file(file_path, file_bytes):
	with open(file_path, "wb") as binary_file:
		binary_file.write(file_bytes)
def run_detection(audio_file):
	mainfolder = '..'
	audio_ext = 'wav'

	unique_filename = str(uuid.uuid4())
	audio_path = f'{mainfolder}/{unique_filename}.{audio_ext}'
	save_file(audio_path, audio_file)

	r = sr.Recognizer()
	with sr.AudioFile(audio_path) as source:
		audio = r.record(source)

	output_content = r.recognize_sphinx(audio)

	if(os.path.exists(audio_path)):
		os.remove(audio_path)
	
	return output_content

@app.route('/api/sync', methods=['POST'])
def detect():
	audio_file = request.files["audio"].read()

	output, total_cpu_usage, total_memory_usage = measure_metrics(run_detection, audio_file)

	response = { 
		'output': output,
		'total_cpu_usage': total_cpu_usage, 
		'total_memory_usage': total_memory_usage
	}

	return jsonify(response)

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
