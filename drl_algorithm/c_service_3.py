import os
import json
import requests
from pydub import AudioSegment
from c_service import Service
from h_configs import SMART_GATEWAY_METRICS_ENDPOINT, DEADLINE_FOR_1_SEGMENT_AUDIO

class Service3(Service):
    def __init__(self, id, user, sensitivity, slice_count, input_path_list, output_path_list, api_endpoint_list):
        super().__init__(id, user, sensitivity, slice_count, input_path_list, output_path_list, api_endpoint_list)
        self.type = 3
        self.slicable = True
        self.base_cpu_demand = None
        self.base_mem_demand = None
        self.aux_cpu_demand = None
        self.aux_mem_demand = None

    def get_deadline_per_slice(self, slice_index):
        deadline_per_slice = 0
        slice_path_list = self._get_slice_path_list(slice_index)
        slice_path = slice_path_list[0]
        segment = AudioSegment.from_file(slice_path)
        n_segments = int(len(segment) / 1000.0)
        deadline_per_slice = n_segments * DEADLINE_FOR_1_SEGMENT_AUDIO
        return deadline_per_slice

    def get_cpu_demand_base(self):
        if self.base_cpu_demand is None:
            response = requests.get(url = SMART_GATEWAY_METRICS_ENDPOINT)
            response = json.loads(response.content)
            self.base_cpu_demand = response['service3_cpu_demand'] 
        return self.base_cpu_demand    
        
    def get_mem_demand_base(self):
        if self.base_mem_demand is None:
            response = requests.get(url = SMART_GATEWAY_METRICS_ENDPOINT)
            response = json.loads(response.content)
            self.base_mem_demand = response['service3_mem_demand'] 
        return self.base_mem_demand

    def get_cpu_demand_aux(self):
        if self.aux_cpu_demand is None:
            response = requests.get(url = SMART_GATEWAY_METRICS_ENDPOINT)
            response = json.loads(response.content)
            self.aux_cpu_demand = response['service3_cpu_aux_demand'] 
        return self.aux_cpu_demand    
        
    def get_mem_demand_aux(self):
        if self.aux_mem_demand is None:
            response = requests.get(url = SMART_GATEWAY_METRICS_ENDPOINT)
            response = json.loads(response.content)
            self.aux_mem_demand = response['service3_mem_aux_demand'] 
        return self.aux_mem_demand

    def merge_slices(self):
        final_slice_output_path = self._get_slice_output_path('final')
        for slice_index in range(self.slice_count):
            slice_output_path = self._get_slice_output_path(slice_index)
            with open(slice_output_path, 'r') as slice_file, open(final_slice_output_path, 'a') as merge_file:
                slice_file_content = slice_file.read()
                merge_file.write(slice_file_content)

    def _do_action(self, slice_index, assigned_to_fog):
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
        slice_output_path = self._get_slice_output_path(slice_index)
        with open(slice_output_path, "a+") as out_file:
            out_file.write(output)

    def make_slices(self):
        for slice_index in range(self.slice_count):
            slice_path_list = self._get_slice_path_list(slice_index)
            slice_path = slice_path_list[0]
            if os.path.exists(slice_path):
                self.slicable = False
                break
        if self.slicable:
            self._split_audio()

    # def _split_audio(self):
    #     input_path = self.input_path_list[0]
    #     audio = AudioSegment.from_file(input_path)
    #     slice_durations = [len(audio) // self.slice_count] * self.slice_count
    #     slice_durations[-1] = len(audio) - sum(slice_durations[:-1])
    #     for slice_index, slice_duration in enumerate(slice_durations):
    #         slice_path_list = self._get_slice_path_list(slice_index)
    #         slice_path = slice_path_list[0]
    #         start_time = sum(slice_durations[:slice_index])
    #         end_time = start_time + slice_duration
    #         slice = audio[start_time:end_time]
    #         with open(slice_path, "wb") as f:
    #             slice.export(f, format="wav")

    def _split_audio(self):
        input_path = self.input_path_list[0]
        with open(input_path, 'rb') as wav_file:
            header = wav_file.read(44)
            num_frames = int.from_bytes(header[40:44], byteorder='little')
            num_channels = int.from_bytes(header[22:24], byteorder='little')
            sample_width = int.from_bytes(header[34:36], byteorder='little')
            for slice_index, slice_size in enumerate(self.slices_size_map.values()):
                frame_size = num_channels * sample_width
                frames_per_part = slice_size if frame_size == 0 else slice_size // frame_size
                bytes_per_part = frames_per_part * frame_size
                segment_data = wav_file.read(bytes_per_part)
                slice_path_list = self._get_slice_path_list(slice_index)
                slice_path = slice_path_list[0]
                with open(slice_path, 'wb') as output_wav_file:
                    output_wav_file.write(header)
                    output_wav_file.write(segment_data)