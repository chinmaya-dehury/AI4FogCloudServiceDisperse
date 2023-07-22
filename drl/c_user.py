import math
import random
from c_env_gateway import SmartGateway
import h_utils as utils

class User:
    def __init__(self, id, latitude, longitude):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.services = []
        self.user_priority = 0
        self.avail_services_map = {}
        self.latency = None

    def set_user_priority(self, user_priority):
        self.user_priority = user_priority
    
    def get_user_priority(self):
        return self.user_priority

    def get_user_latency(self):
        if self.latency is None:
            latency = utils.get_latency(SmartGateway.get_ip(), SmartGateway.get_port())
            self.latency = round(latency, 3)
        return self.latency

    def get_distance_priority(self):
        distance = self._haversine(self.latitude, self.longitude, SmartGateway.get_latitude(), SmartGateway.get_longitude())
        distance_priority = distance / SmartGateway.get_max_comm_range()
        distance_priority = round(distance_priority, 3)
        return distance_priority
    
    def get_services(self):
        return self.services

    def set_services(self, services):
        self.services = services
        self._init_avail_services_map()

    def is_service_avail(self, service_type):
        is_avail = False
        for key, value in self.avail_services_map.items():
            if(key == service_type):
                is_avail = value
                break
        return is_avail
    
    def set_service_avail(self, service_type, is_avail):
        for key, _ in self.avail_services_map.items():
            if(key == service_type):
                self.avail_services_map[key] = is_avail
                break

    def _init_avail_services_map(self):
        for service in self.services:
            self.avail_services_map[service.type] = True

    def _haversine(self, lat1, lon1, lat2, lon2):
        lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
        # haversine formula
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a)) 
        r = 6371 # radius of earth in kilometers
        return c * r * 1000 # convert to meter