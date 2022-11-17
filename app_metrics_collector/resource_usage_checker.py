import time
import psutil as pu
from flask import Flask, request, Response, jsonify

def get_cpu_usage():
	cpu_usage = pu.cpu_percent()
	while cpu_usage == 0 or cpu_usage == 100:
		cpu_usage = pu.cpu_percent()
		time.sleep(1)
	return cpu_usage
	
def get_ram_usage():
	ram_usage = pu.virtual_memory().percent
	return ram_usage

app = Flask(__name__)

@app.route('/', methods=['GET'])
def main():
	cu = get_cpu_usage()
	ru = get_ram_usage()
    return jsonify(cpu = cu, ram = ru)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3333)