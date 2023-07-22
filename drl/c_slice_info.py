from c_service import Service
from h_configs import ENVIRONMENT_NAMES

class SliceInfo:
    def __init__(self, service: Service, service_priority: int, slice_index: int, assigned_env: int, 
                 cpu_demand, mem_demand, total_cpu_demand, total_mem_demand, slice_reward):
        self.service = service
        self.service_priority = service_priority
        self.slice_index = slice_index
        self.slice_reward = slice_reward
        self.assigned_env = assigned_env
        self.cpu_demand = cpu_demand
        self.mem_demand = mem_demand
        self.total_cpu_demand = total_cpu_demand
        self.total_mem_demand = total_mem_demand

    def __repr__(self):
        return f"service_id={self.service.id}, service_priority={self.service_priority}, " + \
            f"cpu_demand={self.cpu_demand}, mem_demand={self.mem_demand}, total_cpu_demand = {self.total_cpu_demand}, total_mem_demand = {self.total_mem_demand}, " + \
            f"slice_index = {self.slice_index}, slice_reward = {self.slice_reward}, assigned_env = {ENVIRONMENT_NAMES[self.assigned_env]} \n"