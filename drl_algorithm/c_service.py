import cv2
import os
import time
from c_user import User

class Service:
    def __init__(self, id, user:User, sensitivity, slice_count, input_path_list, output_path_list, api_endpoint_list):
        self.id = id
        self.type = 0
        self.user = user
        self.assigned_slices_count = 0
        self.sensitivity = sensitivity
        self.slice_count = slice_count
        self.input_path_list = input_path_list
        self.output_path_list = output_path_list
        self.api_endpoint_list = api_endpoint_list
        self.input_size = None
        self.slices_size_map = None

    def __repr__(self):
        return f"Service{self.id}"

    def get_deadline_per_slice(self, slice_index):
        pass

    def get_cpu_demand(self):
        return self.get_cpu_demand_base() + self.get_cpu_demand_aux()

    def get_mem_demand(self):
        return self.get_mem_demand_base() + self.get_mem_demand_aux()

    def get_cpu_demand_per_slice(self, slice_index):
        cpu_demand_per_slice = self.get_cpu_demand_base() + self.get_cpu_demand_aux() * self.get_slice_size(slice_index) / self.get_input_size()
        cpu_demand_per_slice = round(cpu_demand_per_slice, 2)
        return cpu_demand_per_slice

    def get_mem_demand_per_slice(self, slice_index):
        mem_demand_per_slice = self.get_mem_demand_base() + self.get_mem_demand_aux() * self.get_slice_size(slice_index) / self.get_input_size()
        mem_demand_per_slice = round(mem_demand_per_slice, 2)
        return mem_demand_per_slice

    def get_sensitivity(self):
        return self.sensitivity
    
    def get_input_size(self):
        if self.input_size is None:
            input_size = 0
            for input_path in self.input_path_list:
                input_size += os.path.getsize(input_path)
            self.input_size = input_size
        return self.input_size
    
    def set_slices_size(self, slices_size_map):
        self.slices_size_map = slices_size_map

    def get_slice_size(self, slice_index):
        return self.slices_size_map[slice_index]


    def get_slices_size_from_disk(self):
        slices_size_map = {}
        for slice_index in range(self.slice_count):
            slice_size = 0
            for input_path in self.input_path_list:
                slice_path = self._get_slice_path(input_path, slice_index)
                slice_size += os.path.getsize(slice_path)
            slices_size_map[slice_index] = slice_size
        return slices_size_map

    def get_slice_count(self):
        return self.slice_count
    
    def is_completed(self):
        return self.assigned_slices_count == self.slice_count
    
    def do_action_with_metrics(self, slice_index, assigned_env):
        slice_execution_time = 0
        start_time = time.time()
        request_sent_time = time.time()
        slice_id, output, throughput, request_receive_time = self._do_action(slice_index, assigned_env)
        end_time = time.time()
        self._save_output(slice_index, output)
        slice_execution_time = (end_time - start_time)
        communication_time = request_receive_time - request_sent_time 
        return slice_id, slice_execution_time, throughput, communication_time

    def merge_slices(self):
        pass

    def _do_action(self, slice_index, assigned_env):
        pass

    def _save_output(self, slice_index, output):
        pass

    def make_slices(self):
        pass

    def _get_slice_path_list(self, slice_index):
        slice_path_list = []
        for input_path in self.input_path_list:
            slice_path = self._get_slice_path(input_path, slice_index)
            slice_path_list.append(slice_path)
        return slice_path_list

    def _get_slice_path(self, input_path, slice_index):
        slice_path = ''
        input_path_parts = input_path.split('/')
        input_file = input_path_parts[-1].split('.')
        input_file_name = input_file[0]
        input_file_ext = input_file[1]
        slice_path = ''
        for input_path_part in input_path_parts[:-1]:
            slice_path += f'{input_path_part}/'
        slice_path += f'{input_file_name}_slices/'#{input_file_ext}/'
        if not os.path.exists(slice_path):
            os.makedirs(slice_path)
        slice_path += f'{input_file_name}_{slice_index}.{input_file_ext}'
        return slice_path

    def _get_slice_output_path(self, slice_index):
        slice_output_path = ''
        output_path_list = self.output_path_list
        output_folder = output_path_list[0]
        userid = f"user{self.user.id}"
        serviceid = f"service{self.id}"

        output_folder = output_folder + '/' + userid + '/' + serviceid
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        output_file = output_path_list[1]
        output_ext = output_path_list[2]
        slice_output_path = output_folder + '/' + output_file + '_' + str(slice_index) + '.' + output_ext
        return slice_output_path