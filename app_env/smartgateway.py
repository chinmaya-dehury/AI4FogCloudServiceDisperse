import random
from flask import Flask, jsonify

# Initialize the Flask application
app = Flask(__name__)

@app.route('/api/infos', methods=['GET'])
def infos():
    cpu_demands = [1, 2]
    mem_demands = [0.5*1024, 1*1024]
    response = { 
		'latitude': 59.4055351164239,
		'longtitude': 24.732632394943135,
		'max_communication_range': 1000,     # meter
    'service1_cpu_demand': random.choice(cpu_demands),
    'service1_mem_demand': random.choice(mem_demands),
    'service1_cpu_aux_demand': random.choice(cpu_demands),
    'service1_mem_aux_demand': random.choice(mem_demands),
    'service2_cpu_demand': random.choice(cpu_demands),
    'service2_mem_demand': random.choice(mem_demands),
    'service2_cpu_aux_demand': random.choice(cpu_demands),
    'service2_mem_aux_demand': random.choice(mem_demands),
    'service3_cpu_demand': random.choice(cpu_demands),
    'service3_mem_demand': random.choice(mem_demands),
    'service3_cpu_aux_demand': random.choice(cpu_demands),
    'service3_mem_aux_demand': random.choice(mem_demands),
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')