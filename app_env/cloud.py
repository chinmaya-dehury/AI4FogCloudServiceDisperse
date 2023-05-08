import math
import psutil
from flask import Flask, jsonify

# Initialize the Flask application
app = Flask(__name__)

@app.route('/api/infos', methods=['GET'])
def infos():
	available_cpu = psutil.cpu_count(logical=False)
	available_mem = math.floor(psutil.virtual_memory().available / 1024 / 1204)
	response = { 
		'available_cpu': available_cpu,
		'available_mem': available_mem, # MB
	}
	return jsonify(response)

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')