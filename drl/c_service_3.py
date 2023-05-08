import os
import json
import random
import requests
from pydub import AudioSegment
from c_service import Service
from h_configs import SIMULATION, SERVICE_CPU_DEMAND, SERVICE_MEM_DEMAND, SMART_GATEWAY_METRICS_ENDPOINT
from h_utils import divide_unequal

class Service3(Service):
    def __init__(self, id, user, sensitivity, slice_count, input_path_list, output_path_list, api_endpoint_list):
        super().__init__(id, user, sensitivity, slice_count, input_path_list, output_path_list, api_endpoint_list)
        self.type = 3
        self.base_cpu_demand = None
        self.base_mem_demand = None
        self.aux_cpu_demand = None
        self.aux_mem_demand = None

    def get_cpu_demand_base(self):
        if self.base_cpu_demand is None:
            if SIMULATION:
                self.base_cpu_demand = random.randint(SERVICE_CPU_DEMAND[0], SERVICE_CPU_DEMAND[1])
            else:
                response = requests.get(url = SMART_GATEWAY_METRICS_ENDPOINT)
                response = json.loads(response.content)
                self.base_cpu_demand = response['service3_cpu_demand'] 
        return self.base_cpu_demand    
        
    def get_mem_demand_base(self):
        if self.base_mem_demand is None:
            if SIMULATION:
                self.base_mem_demand = random.randint(SERVICE_MEM_DEMAND[0], SERVICE_MEM_DEMAND[1])
            else:
                response = requests.get(url = SMART_GATEWAY_METRICS_ENDPOINT)
                response = json.loads(response.content)
                self.base_mem_demand = response['service3_mem_demand'] 
        return self.base_mem_demand

    def get_cpu_demand_aux(self):
        if self.aux_cpu_demand is None:
            if SIMULATION:
                self.aux_cpu_demand = random.randint(SERVICE_CPU_DEMAND[0], SERVICE_CPU_DEMAND[1])
            else:
                response = requests.get(url = SMART_GATEWAY_METRICS_ENDPOINT)
                response = json.loads(response.content)
                self.aux_cpu_demand = response['service3_cpu_aux_demand'] 
        return self.aux_cpu_demand    
        
    def get_mem_demand_aux(self):
        if self.aux_mem_demand is None:
            if SIMULATION:
                self.aux_mem_demand = random.randint(SERVICE_MEM_DEMAND[0], SERVICE_MEM_DEMAND[1])
            else:
                response = requests.get(url = SMART_GATEWAY_METRICS_ENDPOINT)
                response = json.loads(response.content)
                self.aux_mem_demand = response['service3_mem_aux_demand'] 
        return self.aux_mem_demand

    def merge_slices(self):
        if SIMULATION:
            pass
        else:
            final_slice_output_path = self._get_slice_output_path('final')
            for slice_index in range(self.slice_count):
                slice_output_path = self._get_slice_output_path(slice_index)
                with open(slice_output_path, 'r') as slice_file, open(final_slice_output_path, 'a') as merge_file:
                    slice_file_content = slice_file.read()
                    merge_file.write(slice_file_content)

    def _do_action(self, slice_index, assigned_to_fog):
        if SIMULATION:
            output = ''
        else:
            slice_path_list = self._get_slice_path_list(slice_index)
            endpoint_url = self.api_endpoint_list[0] if assigned_to_fog == 1 else self.api_endpoint_list[1]
            files = {
                'audio': open(slice_path_list[0], 'rb')
            }
            response = requests.post(url = endpoint_url, files=files)
            response = json.loads(response.content)
            output = response['output']
        return output

    def _save_output(self, slice_index, output):
        if SIMULATION:
            pass 
        else:
            slice_output_path = self._get_slice_output_path(slice_index)
            with open(slice_output_path, "a+") as out_file:
                out_file.write(output)

    def _make_slices(self):
        if SIMULATION:
            pass
        else:
            self._split_audio()

    def _split_audio(self):
        input_path = self.input_path_list[0]
        audio = AudioSegment.from_file(input_path)
        slice_durations = [len(audio) // self.slice_count] * self.slice_count
        slice_durations[-1] = len(audio) - sum(slice_durations[:-1])

        for slice_index, slice_duration in enumerate(slice_durations):
            slice_path_list = self._get_slice_path_list(slice_index)
            slice_path = slice_path_list[0]

            start_time = sum(slice_durations[:slice_index])
            end_time = start_time + slice_duration
            slice = audio[start_time:end_time]

            with open(slice_path, "wb") as f:
                slice.export(f, format="wav")

    # def _split_audio(self):
    #     input_path = self.input_path_list[0]
    #     input_size = os.path.getsize(input_path)
    #     slice_sizes = divide_unequal(input_size, self.slice_count)
    #     with open(input_path, 'rb') as input_file:
    #         for slice_index, slice_size in enumerate(slice_sizes.values()):
    #             slice_path_list = self._get_slice_path_list(slice_index)
    #             slice_path = slice_path_list[0]
    #             with open(slice_path, 'wb') as output_file:
    #                 output_file.write(input_file.read(slice_size))
    #                 input_size -= slice_size