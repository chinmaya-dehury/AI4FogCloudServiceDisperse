import json
import random
import requests
import h_utils as utils
from h_configs import FOG_ID, FOG_IP, FOG_PORT, FOG_METRICS_ENDPOINT

class Fog:
    __available_cpu = None
    __available_mem = None
    __latency = None

    @staticmethod
    def reset():
        Fog.__available_cpu = None
        Fog.__available_mem = None
        Fog.__latency = None

    @staticmethod
    def get_id():
        return FOG_ID

    @staticmethod
    def get_ip():
        return FOG_IP
    
    @staticmethod
    def get_port():
        return FOG_PORT

    @staticmethod
    def get_latency():
        if Fog.__latency is None:
            latency = utils.get_latency(Fog.get_ip(), Fog.get_port())
            Fog.__latency = round(latency, 3)
        return Fog.__latency

    @staticmethod
    def get_available_cpu():
        if Fog.__available_cpu is None:
            response = requests.get(url = FOG_METRICS_ENDPOINT)
            response = json.loads(response.content)
            Fog.__available_cpu = response['available_cpu']
        return Fog.__available_cpu

    @staticmethod    
    def get_available_memory():
        if Fog.__available_mem is None:
            response = requests.get(url = FOG_METRICS_ENDPOINT)
            response = json.loads(response.content)
            Fog.__available_mem = response['available_mem']
        return Fog.__available_mem