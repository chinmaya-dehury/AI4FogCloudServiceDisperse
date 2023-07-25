import json
import random
import requests
import h_utils as utils
from h_configs import CLOUD_ID, CLOUD_IP, CLOUD_PORT, CLOUD_METRICS_ENDPOINT

class Cloud:
    __available_cpu = None
    __available_mem = None
    __latency = None

    @staticmethod
    def reset():
        Cloud.__available_cpu = None
        Cloud.__available_mem = None
        Cloud.__latency = None

    @staticmethod
    def get_id():
        return CLOUD_ID

    @staticmethod
    def get_ip():
        return CLOUD_IP
    
    @staticmethod
    def get_port():
        return CLOUD_PORT

    @staticmethod
    def get_latency():
        if Cloud.__latency is None:
            latency = utils.get_latency(Cloud.get_ip(), Cloud.get_port())
            Cloud.__latency = round(latency, 3)
        return Cloud.__latency

    @staticmethod
    def get_available_cpu():
        if Cloud.__available_cpu is None:
            response = requests.get(url = CLOUD_METRICS_ENDPOINT)
            response = json.loads(response.content)
            Cloud.__available_cpu = response['available_cpu']
        return Cloud.__available_cpu

    @staticmethod    
    def get_available_memory():
        if Cloud.__available_mem is None:
            response = requests.get(url = CLOUD_METRICS_ENDPOINT)
            response = json.loads(response.content)
            Cloud.__available_mem = response['available_mem']
        return Cloud.__available_mem