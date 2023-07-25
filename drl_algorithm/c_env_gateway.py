import json
import requests
from h_configs import SMART_GATEWAY_IP, SMART_GATEWAY_PORT, SMART_GATEWAY_METRICS_ENDPOINT

class SmartGateway:
    __metrics = None

    @staticmethod
    def reset():
        SmartGateway.__metrics = None

    @staticmethod
    def get_ip():
        return SMART_GATEWAY_IP
    
    @staticmethod
    def get_port():
        return SMART_GATEWAY_PORT
    
    @staticmethod
    def get_metrics():
        if SmartGateway.__metrics is None:
            response = requests.get(url = SMART_GATEWAY_METRICS_ENDPOINT)
            SmartGateway.__metrics = json.loads(response.content)
        return SmartGateway.__metrics

    @staticmethod
    def get_latitude():
        return SmartGateway.get_metrics()["latitude"]
    
    @staticmethod
    def get_longitude():
        return SmartGateway.get_metrics()["longtitude"]

    @staticmethod
    def get_max_comm_range():
        return SmartGateway.get_metrics()["max_communication_range"]