import os
import uuid
import time
import psutil
from flask_caching import Cache
import speech_recognition as sr

from flask import Flask, request, Response, jsonify

def save_file(file_path, file_bytes):
	with open(file_path, "wb") as binary_file:
		binary_file.write(file_bytes)

app = Flask(__name__)
config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}
app.config.from_mapping(config)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})  

@app.route('/api/sync', methods=['POST'])
def main():
	mainfolder = '..'
	audio_ext = 'wav'

	unique_filename = str(uuid.uuid4())
	audio_path = f'{mainfolder}/{unique_filename}.{audio_ext}'
	audio_file = request.files["audio"].read()
	save_file(audio_path, audio_file)

	r = sr.Recognizer()
	with sr.AudioFile(audio_path) as source:
		audio = r.record(source)

	output_content = r.recognize_sphinx(audio)

	if(os.path.exists(audio_path)):
		os.remove(audio_path)

	return Response(response = output_content, status = 200, mimetype = "application/json")

KEY_TOTAL_CPU_USAGE = "TOTAL_CPU_USAGE"
KEY_TOTAL_MEMORY_USAGE = "TOTAL_MEMORY_USAGE"
KEY_TOTAL_POWER_USAGE = "TOTAL_POWER_USAGE"

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
    total_cpu_usage = (end_cpu_usage - start_cpu_usage)

    # get memory usage
    end_mem_info = psutil.Process().memory_info()
    total_memory_usage = (end_mem_info.rss - start_mem_info.rss) / 1_000_000 # convert bytes to MB

    # get the estimated energy consumption
    total_power_usage = total_cpu_usage * 10  # assume 10 watts per 100% CPU usage

    return output, round(total_cpu_usage, 3), round(total_memory_usage, 3), round(total_power_usage, 3)

def get_from_cache(key):
    return cache.get(key)

def set_to_cache(key, value):
    cache.set(key, value)


@app.route('/api/metrics', methods=['GET'])
def metrics():
    total_cpu_usage = get_from_cache(KEY_TOTAL_CPU_USAGE)
    total_memory_usage = get_from_cache(KEY_TOTAL_MEMORY_USAGE)
    total_power_usage = get_from_cache(KEY_TOTAL_POWER_USAGE)

    output = { 
        'total_cpu_usage': total_cpu_usage, 
        'total_memory_usage': total_memory_usage, 
        'total_power_usage': total_power_usage 
    }
    
    return jsonify(output)

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
