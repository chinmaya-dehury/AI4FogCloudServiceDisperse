import os
import json
import time
import random
import requests
from c_service import Service
from pydub import AudioSegment
from h_configs import SIMULATION, SERVICE_CPU_DEMAND, SERVICE_MEM_DEMAND, SMART_GATEWAY_METRICS_ENDPOINT
from h_utils import divide_unequal

class Service2(Service):
    def __init__(self, id, user, sensitivity, slice_count, input_path_list, output_path_list, api_endpoint_list):
        super().__init__(id, user, sensitivity, slice_count, input_path_list, output_path_list, api_endpoint_list)
        self.type = 2
        self.output_offset = 0
        self.output_counter = 0
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
                self.base_cpu_demand = response['service2_cpu_demand'] 
        return self.base_cpu_demand    
        
    def get_mem_demand_base(self):
        if self.base_mem_demand is None:
            if SIMULATION:
                self.base_mem_demand = random.randint(SERVICE_MEM_DEMAND[0], SERVICE_MEM_DEMAND[1])
            else:
                response = requests.get(url = SMART_GATEWAY_METRICS_ENDPOINT)
                response = json.loads(response.content)
                self.base_mem_demand = response['service2_mem_demand'] 
        return self.base_mem_demand

    def get_cpu_demand_aux(self):
        if self.aux_cpu_demand is None:
            if SIMULATION:
                self.aux_cpu_demand = random.randint(SERVICE_CPU_DEMAND[0], SERVICE_CPU_DEMAND[1])
            else:
                response = requests.get(url = SMART_GATEWAY_METRICS_ENDPOINT)
                response = json.loads(response.content)
                self.aux_cpu_demand = response['service2_cpu_aux_demand'] 
        return self.aux_cpu_demand    
        
    def get_mem_demand_aux(self):
        if self.aux_mem_demand is None:
            if SIMULATION:
                self.aux_mem_demand = random.randint(SERVICE_MEM_DEMAND[0], SERVICE_MEM_DEMAND[1])
            else:
                response = requests.get(url = SMART_GATEWAY_METRICS_ENDPOINT)
                response = json.loads(response.content)
                self.aux_mem_demand = response['service2_mem_aux_demand'] 
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
                'audio': open(slice_path_list[0], 'rb'),
                'subtitle': open(slice_path_list[1], 'rb'),
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
            self.output_offset = self.output_counter * 10
            self.output_counter = self._save_output_helper(self.output_counter, output, self.output_offset, slice_output_path)

    def _make_slices(self):
        if SIMULATION:
            pass
        else:
            self._split_audio()
            self._split_subtitle()
    
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
                slice.export(f, format="mp3")

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

    def _split_subtitle(self):
        input_path = self.input_path_list[1]
        subtitle = self._read_subtitle(input_path)
        subtitle_slices = self._split_subtitle_helper(subtitle, self.slice_count)

        for slice_index in range(self.slice_count):
            slice_path_list = self._get_slice_path_list(slice_index)
            slice_path = slice_path_list[1]
            with open(slice_path, "w") as f:
                for subtitle in list(subtitle_slices[slice_index]):
                    f.write(subtitle)

    def _split_subtitle_helper(self, a, n):
        k, m = divmod(len(a), n)
        return [a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n)]
    
    def _read_subtitle(self, subtitle_path):
        with open(subtitle_path, 'r') as f:
            lines = f.readlines()
        return lines
    
    def _save_output_helper(self, line_counter, jsonfile, offset, filepath):
        jsonfile = ''.join(str(jf) for jf in jsonfile)
        l = self._json_to_list(jsonfile)

        for i in l:
            line_counter += 1
            begin = self._change_format(i['begin'], offset)
            end = self._change_format(i['end'], offset)
            lines = i['lines']

            subtitle = f"{line_counter}\n"
            subtitle += f"{begin} --> {end}"
            for line in lines:
                subtitle += f"\n{line}"
            subtitle += "\n\n"
            with open(filepath, 'a') as f: f.write(subtitle)
        
        return line_counter
    
    def _json_to_list(self, jsonfile):
        myjson = json.loads(jsonfile)
        return myjson['fragments']
    
    def _change_format(self, sec, offset):
        sec = sec.split('.')
        s = int(sec[0]) + offset
        ms = sec[1]
        st = f"{time.strftime('%H:%M:%S', time.gmtime(s))},{ms}"
        return st