import os
import json
import requests
from c_service import Service
from h_configs import SMART_GATEWAY_METRICS_ENDPOINT, DEADLINE_FOR_1_FRAME_VIDEO
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import concatenate_videoclips

class Service1(Service):
    def __init__(self, id, user, sensitivity, slice_count, input_path_list, output_path_list, api_endpoint_list):
        super().__init__(id, user, sensitivity, slice_count, input_path_list, output_path_list, api_endpoint_list)
        self.type = 1
        self.slicable = True
        self.base_cpu_demand = None
        self.base_mem_demand = None
        self.aux_cpu_demand = None
        self.aux_mem_demand = None

    def get_deadline_per_slice(self, slice_index):
        deadline_per_slice = 0
        slice_path_list = self._get_slice_path_list(slice_index)
        slice_path = slice_path_list[0]
        clip = VideoFileClip(slice_path)
        n_frames = int(clip.reader.nframes)
        deadline_per_slice = n_frames * DEADLINE_FOR_1_FRAME_VIDEO
        return deadline_per_slice

    def get_cpu_demand_base(self):
        if self.base_cpu_demand is None:
            response = requests.get(url = SMART_GATEWAY_METRICS_ENDPOINT)
            response = json.loads(response.content)
            self.base_cpu_demand = response['service1_cpu_demand'] 
        return self.base_cpu_demand    
        
    def get_mem_demand_base(self):
        if self.base_mem_demand is None:
            response = requests.get(url = SMART_GATEWAY_METRICS_ENDPOINT)
            response = json.loads(response.content)
            self.base_mem_demand = response['service1_mem_demand'] 
        return self.base_mem_demand

    def get_cpu_demand_aux(self):
        if self.aux_cpu_demand is None:
            response = requests.get(url = SMART_GATEWAY_METRICS_ENDPOINT)
            response = json.loads(response.content)
            self.aux_cpu_demand = response['service1_cpu_aux_demand'] 
        return self.aux_cpu_demand    
        
    def get_mem_demand_aux(self):
        if self.aux_mem_demand is None:
            response = requests.get(url = SMART_GATEWAY_METRICS_ENDPOINT)
            response = json.loads(response.content)
            self.aux_mem_demand = response['service1_mem_aux_demand'] 
        return self.aux_mem_demand

    def merge_slices(self):
        final_slice_output_path = self._get_slice_output_path('final')
        slice_output_path_list = []
        for slice_index in range(self.slice_count):
            slice_output_path = self._get_slice_output_path(slice_index)
            slice_output_path_list.append(slice_output_path)
        clips = [VideoFileClip(v) for v in slice_output_path_list]
        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile(final_slice_output_path)
    
    def _do_action(self, slice_index, assigned_env):
        slice_path_list = self._get_slice_path_list(slice_index)
        endpoint_url = self.api_endpoint_list[0] if assigned_env == 1 else self.api_endpoint_list[1]
        response = requests.post(url = endpoint_url, files={'video': open(slice_path_list[0], 'rb')})
        output = response.content
        return output


    def _save_output(self, slice_index, output):
        slice_output_path = self._get_slice_output_path(slice_index)
        with open(slice_output_path, "wb") as out_file:
            out_file.write(output)

    def make_slices(self):
        for slice_index in range(self.slice_count):
            slice_path_list = self._get_slice_path_list(slice_index)
            slice_path = slice_path_list[0]
            if os.path.exists(slice_path):
                self.slicable = False
                break
        if self.slicable:
            self._slice_video()

    def _slice_video(self):
        input_path = self.input_path_list[0]
        input_size = self.get_input_size()
        video_clip = VideoFileClip(input_path)
        video_clip = video_clip.without_audio()
        total_duration = video_clip.duration
        start_time = 0
        for slice_index, slice_size in self.slices_size_map.items():
            slice_duration = total_duration * slice_size / input_size
            end_time = start_time + slice_duration
            end_time = min(end_time, total_duration)
            slice_path_list = self._get_slice_path_list(slice_index)
            slice_path = slice_path_list[0]
            subclip = video_clip.subclip(start_time, end_time)
            subclip = subclip.resize(height=360)
            subclip.write_videofile(slice_path, bitrate="500k")
            start_time = end_time
        video_clip.reader.close()