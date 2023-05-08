import os
import json
import random
import requests
import numpy as np
from io import BytesIO
from c_service import Service
from h_configs import SIMULATION, SERVICE_CPU_DEMAND, SERVICE_MEM_DEMAND, SMART_GATEWAY_METRICS_ENDPOINT
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import concatenate_videoclips

class Service1(Service):
    def __init__(self, id, user, sensitivity, slice_count, input_path_list, output_path_list, api_endpoint_list):
        super().__init__(id, user, sensitivity, slice_count, input_path_list, output_path_list, api_endpoint_list)
        self.type = 1
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
                self.base_cpu_demand = response['service1_cpu_demand'] 
        return self.base_cpu_demand    
        
    def get_mem_demand_base(self):
        if self.base_mem_demand is None:
            if SIMULATION:
                self.base_mem_demand = random.randint(SERVICE_MEM_DEMAND[0], SERVICE_MEM_DEMAND[1])
            else:
                response = requests.get(url = SMART_GATEWAY_METRICS_ENDPOINT)
                response = json.loads(response.content)
                self.base_mem_demand = response['service1_mem_demand'] 
        return self.base_mem_demand

    def get_cpu_demand_aux(self):
        if self.aux_cpu_demand is None:
            if SIMULATION:
                self.aux_cpu_demand = random.randint(SERVICE_CPU_DEMAND[0], SERVICE_CPU_DEMAND[1])
            else:
                response = requests.get(url = SMART_GATEWAY_METRICS_ENDPOINT)
                response = json.loads(response.content)
                self.aux_cpu_demand = response['service1_cpu_aux_demand'] 
        return self.aux_cpu_demand    
        
    def get_mem_demand_aux(self):
        if self.aux_mem_demand is None:
            if SIMULATION:
                self.aux_mem_demand = random.randint(SERVICE_MEM_DEMAND[0], SERVICE_MEM_DEMAND[1])
            else:
                response = requests.get(url = SMART_GATEWAY_METRICS_ENDPOINT)
                response = json.loads(response.content)
                self.aux_mem_demand = response['service1_mem_aux_demand'] 
        return self.aux_mem_demand

    def merge_slices(self):
        if SIMULATION:
            pass
        else:
            final_slice_output_path = self._get_slice_output_path('final')
            slice_output_path_list = []
            for slice_index in range(self.slice_count):
                slice_output_path = self._get_slice_output_path(slice_index)
                slice_output_path_list.append(slice_output_path)
            clips = [VideoFileClip(v) for v in slice_output_path_list]
            final_clip = concatenate_videoclips(clips)
            final_clip.write_videofile(final_slice_output_path)
    
    def _do_action(self, slice_index, assigned_env):
        if SIMULATION:
            output = ''
        else:
            slice_path_list = self._get_slice_path_list(slice_index)
            endpoint_url = self.api_endpoint_list[0] if assigned_env == 1 else self.api_endpoint_list[1]
            response = requests.post(url = endpoint_url, files={'video': open(slice_path_list[0], 'rb')})
            output = response.content
        return output


    def _save_output(self, slice_index, output):
        if SIMULATION:
            pass
        else:
            slice_output_path = self._get_slice_output_path(slice_index)
            with open(slice_output_path, "wb") as out_file:
                out_file.write(output)

    def _make_slices(self):
        if SIMULATION:
            pass
        else:
            self._slice_video()

    def _slice_video(self):
        input_path = self.input_path_list[0]

        slice_start_time = 0
        for slice_index in range(self.slice_count):
            slice_path_list = self._get_slice_path_list(slice_index)
            slice_path = slice_path_list[0]

            if not os.path.exists(slice_path):
                video = VideoFileClip(input_path)
                video_duration = video.duration
                slice_duration = video_duration / self.slice_count

                slice_end_time = min(slice_start_time + slice_duration, video_duration)
                slice = video.subclip(slice_start_time, slice_end_time)
                slice.write_videofile(slice_path)
                slice_start_time = slice_end_time