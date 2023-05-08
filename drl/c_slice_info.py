from c_service import Service
from h_configs import ENVIRONMENT_NAMES

class SliceInfo:
    def __init__(self, service: Service, service_priority: int, slice_index: int, assigned_env: int, slice_reward = 0):
        self.service = service
        self.service_priority = service_priority
        self.slice_index = slice_index
        self.slice_reward = slice_reward
        self.assigned_env = assigned_env 

    def __repr__(self):
        return f"service_id={self.service.id}, service_priority={self.service_priority}, " + \
            f"slice_index = {self.slice_index}, slice_reward = {self.slice_reward}, assigned_env = {ENVIRONMENT_NAMES[self.assigned_env]} \n"