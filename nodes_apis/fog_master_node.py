import json
import math
import psutil
import requests
from flask import Flask, jsonify

# Initialize the Flask application
app = Flask(__name__)

@app.route('/api/infos', methods=['GET'])
def infos():
	available_cpu, available_mem = get_total_resources()
	response = { 
		'available_cpu': available_cpu,
		'available_mem': available_mem, # MB
	}
	return jsonify(response)

def get_total_resources():
	total_cpu = psutil.cpu_count(logical=False) # master node available_cpu
	total_mem = math.floor(psutil.virtual_memory().available / 1024 / 1204) # master node available_mem
	slave_nodes_ips = ["172.17.142.124", "172.17.142.129", "172.17.141.56", "172.17.143.73"]
	for slave_node_ip in slave_nodes_ips:
		url = f"http://{slave_node_ip}:5000/api/infos"
		response = requests.get(url = url)
		response = json.loads(response.content)
		total_cpu += response['available_cpu']
		total_mem += response['available_mem']
	return total_cpu, total_mem

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')