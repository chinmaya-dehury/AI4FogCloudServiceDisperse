from tcp_latency import measure_latency

def get_latency(host):
	result = measure_latency(host, port = 80)
	if isinstance(result, list):
		result = sum(result) / len(result)
	latency = round(result, 2)
	return latency