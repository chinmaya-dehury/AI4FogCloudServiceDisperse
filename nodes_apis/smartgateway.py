from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/infos', methods=['GET'])
def infos():
    high_cpu = 3; high_mem = 1024
    medium_cpu = 2; medium_mem = 512
    low_cpu = 1; low_mem = 256
    response = { 
		'latitude': 59.4055351164239,
		'longtitude': 24.732632394943135,
		'max_communication_range': 1000,     # meter
    'service1_cpu_demand': high_cpu,
    'service1_mem_demand': high_mem,
    'service1_cpu_aux_demand': high_cpu,
    'service1_mem_aux_demand': high_mem,
    'service2_cpu_demand': medium_cpu,
    'service2_mem_demand': medium_mem,
    'service2_cpu_aux_demand': medium_cpu,
    'service2_mem_aux_demand': medium_mem,
    'service3_cpu_demand': low_cpu,
    'service3_mem_demand': low_mem,
    'service3_cpu_aux_demand': low_cpu,
    'service3_mem_aux_demand': low_mem,
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')