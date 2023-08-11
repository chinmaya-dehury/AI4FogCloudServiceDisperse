import os
import pyaudio
from pydub import AudioSegment
import time
import torch
import shutil
import random
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from c_service_3 import Service3
from drl_model import DRLModel
from drl_environment import Environment
import h_utils_state_space as ssutils
from c_user_factory import generate_users
from c_system_modelling import set_users_priorities
from drl_agent_factory import generate_agent
import h_utils as utils
from h_configs import SERVICE3_OUTPUT_PATH_LIST, SERVICE3_FOG_ENDPOINT, SERVICE3_CLOUD_ENDPOINT, \
    SERVICE_SENSITIVITY, DynamicParams, INFERENCE_RUN_TIME

### GENERAL
plot_folder = "plots"
input_stream_folder = "input_stream"
output_stream_folder = "output_stream"
semaphore = threading.Semaphore(value=1)

def run_inference():
    # watcher_thread = threading.Thread(target=start_watcher, args=(output_stream_folder,))
    # watcher_thread.start()
    # watcher_thread.join()
    if os.path.exists(plot_folder):
        shutil.rmtree(plot_folder)
    if os.path.exists(input_stream_folder):
        shutil.rmtree(input_stream_folder)
    if os.path.exists(output_stream_folder):
        shutil.rmtree(output_stream_folder)
    if not os.path.exists(output_stream_folder):
        os.makedirs(output_stream_folder)
    for _ in range(INFERENCE_RUN_TIME):
        print(f"STARTING {_}th run time")
        input_run_stream()

### INPUT PART
def input_run_stream():
    request_sent_time_smartgateway = time.time()

    # general settings
    model_threads = []
    timestap_h = 6
    service_id = 1
    slice_index = 0
    current_part = 0
    audio_path = f"input/streaming.wav"

    # audio settings
    audio_sr = []
    audio_parts = {}
    audio_parts_len = 0
    chunk_size = 1024 # default chuck size value for playing audio
    audio = AudioSegment.from_file(audio_path)
    audio = audio[(service_id-1) * 1000:]
    audio_len = len(audio) / 1000 # convert milliseconds to seconds
    audio_channels = audio.channels
    audio_frame_rate = audio.frame_rate
    audio_raw_data = audio.raw_data
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(audio.sample_width),
                    channels=audio_channels,
                    rate=audio_frame_rate,
                    output=True)

    # play audio
    idx = 0
    start_time = time.time()
    start_throughput_time = time.time()
    while idx < len(audio_raw_data):
        timestap = timestap_h * service_id

        # sr folder, file setting
        sr_folder = f"sr{service_id}"
        out_sr_folder = f"{input_stream_folder}/{sr_folder}"
        sr_audio_name = f"sr{service_id}.wav"
        out_sr_audio_name = f"{out_sr_folder}/{sr_audio_name}"
        if not os.path.exists(out_sr_folder):
            os.makedirs(out_sr_folder)

        # slice folder, file setting
        slice_folder = f"{sr_folder}_slices"
        out_slice_folder = f"{input_stream_folder}/{sr_folder}/{slice_folder}"
        slice_audio_name = f"sr{service_id}_{slice_index}.wav"
        out_slice_audio_name = f"{out_slice_folder}/{slice_audio_name}"
        if not os.path.exists(out_slice_folder):
            os.makedirs(out_slice_folder)

        chunk = audio_raw_data[idx:idx + chunk_size]
        stream.write(chunk)
        idx += chunk_size

        request_receive_time_smartgateway = time.time()
        smartgateway_commtimes = request_receive_time_smartgateway - request_sent_time_smartgateway

        # save played chunk of audio
        if not current_part in audio_parts:
            audio_parts[current_part] = []
        audio_parts[current_part].extend(chunk)

        # save 1 sec part of audio
        end_time = time.time()
        passed_time = end_time-start_time
        if abs(passed_time - 1.0) <= 0.1:
            # audio slice handling
            audio_sr.extend(audio_parts[current_part])
            audio_part = AudioSegment(bytes(audio_parts[current_part]), sample_width=2, channels=audio_channels, frame_rate=audio_frame_rate)
            audio_part.export(out_slice_audio_name, format="wav")
            audio_parts[current_part] = []
            audio_part_len = len(audio_part) / 1000  # convert milliseconds to seconds
            audio_parts_len += audio_part_len

            # resetting
            current_part += 1
            slice_index += 1
            start_time = time.time()
            if (slice_index >= 6 or (slice_index < 6 and abs(audio_len - audio_parts_len) <= 0.5)):
                # audio sr handling
                audio_sr = AudioSegment(bytes(audio_sr), sample_width=2, channels=audio_channels, frame_rate=audio_frame_rate)
                audio_sr.export(out_sr_audio_name, format="wav")

                end_throughput_time = time.time() # end throughtput time before assinging envs
                slices_count = slice_index
                total_frames_smartgateway = len(audio_sr) / 1000
                start_throughput_time = time.time()
                model_thread = threading.Thread(target=run_model_thread, args=(service_id, timestap, slices_count, smartgateway_commtimes, total_frames_smartgateway, start_throughput_time, end_throughput_time))
                model_threads.append(model_thread)
                model_thread.start()


                slice_index = 0
                service_id += 1
                audio_sr = []
            # logging
            #print(f"current_part = {current_part},  audio_len = {audio_len} seconds,  audio_parts_len = {audio_parts_len} seconds,  ")
        request_sent_time_smartgateway = time.time()

    for model_thread in model_threads:
        model_thread.join()
    stream.stop_stream()
    stream.close()
    p.terminate()


### OUTPUT PART
def output_play_video(fragment_path):
    fragment = ""
    with open(fragment_path, "r") as file:
        for line in file:
            fragment += f"{line.strip()} "  
    # print(fragment)  

def start_watcher(path_to_watch):
    event_handler = FolderWatcher()
    observer = Observer()
    observer.schedule(event_handler, path=path_to_watch, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

class FolderWatcher(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        output_play_video(event.src_path)

    def on_created(self, event):
        if event.is_directory:
            return


    def on_deleted(self, event):
        if event.is_directory:
            return

    def on_moved(self, event):
        if event.is_directory:
            return


### AI PART
def run_model_thread(service_id, timestap, slices_count, smartgateway_commtimes, total_frames_smartgateway, start_throughput_time, end_throughput_time):
    with semaphore:
        run_model(service_id, timestap, slices_count, smartgateway_commtimes, total_frames_smartgateway, start_throughput_time, end_throughput_time)
        time.sleep(3)

def run_model(service_id, timestap, slices_count, smartgateway_commtimes, total_frames_smartgateway, start_throughput_time, end_throughput_time):
    app_type = 3
    service_count = 1
    DynamicParams.set_params(app_type, service_count, slices_count)
    run_model_helper(service_id, timestap, smartgateway_commtimes, total_frames_smartgateway, start_throughput_time, end_throughput_time)

def run_model_helper(service_id, timestap, smartgateway_commtimes, total_frames_smartgateway, start_throughput_time, end_throughput_time):
    # get count of slices, count of services
    app_type = DynamicParams.get_params()['service_type']
    slices_count = DynamicParams.get_params()['slice_count']
    services_count = DynamicParams.get_params()['service_count']

    # generate agent
    input_layer_size = ssutils.get_state_space_len(services_count, slices_count)
    hidden_layer_size = input_layer_size * 2
    output_layer_size = ssutils.get_state_space_len(services_count, slices_count)

    # generate users
    users = generate_users(n=1)
    set_users_priorities(users)

    # generate services for each users
    user = users[0]
    service_sensitity = random.choice(SERVICE_SENSITIVITY)
    service = Service3(
                id = service_id, 
                user = user,
                sensitivity = service_sensitity, 
                slice_count = DynamicParams.get_params()['slice_count'], 
                input_path_list = [f"{input_stream_folder}/sr{service_id}/sr{service_id}.wav"], 
                output_path_list = SERVICE3_OUTPUT_PATH_LIST,
                api_endpoint_list = [SERVICE3_FOG_ENDPOINT, SERVICE3_CLOUD_ENDPOINT]
            )
    slice_sizes = service.get_slices_size_from_disk()
    service.set_slices_size(slice_sizes)
    user.services.append(service)
    

    # init environment
    done = False
    total_reward = 0
    environment = Environment(users)
    environment.reset()

    # load back the model
    model_name = f"models/model_{app_type}_{(services_count*slices_count)}.pth"
    if os.path.exists(model_name):
        model = DRLModel(input_layer_size, hidden_layer_size, output_layer_size)
        state_dict = torch.load(model_name)
        model.load_state_dict(state_dict)
        while not done:
            # get state
            state = environment.get_state_space()

            # get action 
            action = get_model_action(model, state, output_layer_size)

            # perform action and get new state
            reward, done, info = environment.step(action)
            total_reward += reward
            slices_tracker = info[0]
            if done:
                metrics_logger(service_id, timestap, slices_tracker, smartgateway_commtimes, total_frames_smartgateway, start_throughput_time, end_throughput_time)
    # load back agent
    else:
        agent = generate_agent(input_layer_size, hidden_layer_size, output_layer_size)
        print(f"OFFLINE TRAINING IS STARTED")
        print(f"app_type={app_type},  slices_count={slices_count},  services_count={services_count}")
        while not done:
            # observe the current state s
            current_state = environment.get_state_space()
            
            # select an action a
            action, _ = agent.get_action(current_state)

            # execute the action a, move to the next state s′ and observe the reward r
            reward, done, info = environment.step(action)
            total_reward += reward
            slices_tracker = info[0]
            print(f"OFFLINE TRAINING REWARD = {reward}, ACTION = {action.index(1)}, DONE = {done}")
            next_state = environment.get_state_space()

            # store the transition (s, a, r, d, s′) in the buffer
            agent.train_short_memory(current_state, action, reward, done, next_state)
            agent.remember(current_state, action, reward, done, next_state)
            if done:
                metrics_logger(service_id, timestap, slices_tracker, smartgateway_commtimes, total_frames_smartgateway, start_throughput_time, end_throughput_time)

        # store the transition (s, a, r, d, s′) in the long memory
        agent.train_long_memory()

    # copy to output stream folder
    file_name = f"{SERVICE3_OUTPUT_PATH_LIST[1]}_final.{SERVICE3_OUTPUT_PATH_LIST[2]}"
    src_path = SERVICE3_OUTPUT_PATH_LIST[0] + "/" + f"user{user.id}" + '/' + f"service{service.id}" + "/" + file_name
    dest_path = output_stream_folder + "/" + file_name
    if os.path.exists(src_path):
        shutil.copyfile(src_path, dest_path)

def get_model_action(model, state, output_layer_size):
    action = [0] * output_layer_size
    with torch.no_grad():
        state0 = torch.tensor(state, dtype = torch.float)
        prediction = model(state0)
        prediction = torch.argmax(prediction).item()
    action[prediction] = 1
    return action

def metrics_logger(service_id, timestap, slices_tracker, smartgateway_commtimes, total_frames_smartgateway, start_throughput_time, end_throughput_time):
    metrics_id = f"{service_id}_{timestap}"

    passed_throughput_time = end_throughput_time-start_throughput_time
    passed_throughput_time = passed_throughput_time if passed_throughput_time > 1 else 1
    smartgateway_throughput = total_frames_smartgateway/passed_throughput_time

    ### collect metrics
    fog_cpu = 0; cloud_cpu = 0; fog_mem = 0; cloud_mem = 0
    fog_throughput = 0; cloud_throughput = 0
    fog_commtimes = 0; cloud_commtimes = 0
    if slices_tracker is not None:
        for _, value in slices_tracker.items():
            env = value.assigned_env
            throughput = value.slice_throughput
            commtime = value.slice_communication_time
            if env == 1:
                fog_throughput += throughput
                fog_commtimes += commtime
                fog_cpu += value.slice_cpu_usage
                fog_mem += value.slice_mem_usage
            if env == 2:
                cloud_throughput += throughput
                cloud_commtimes += commtime
                cloud_cpu += value.slice_cpu_usage
                cloud_mem += value.slice_mem_usage
        fog_cpu = fog_cpu if fog_cpu < 100 else fog_cpu / (fog_cpu//100+1)
        fog_mem = fog_mem if fog_mem < 100 else fog_mem / (fog_mem//100+1)
        cloud_cpu = cloud_cpu if cloud_cpu < 100 else cloud_cpu / (cloud_cpu//100+1)
        cloud_mem = cloud_mem if cloud_mem < 100 else cloud_mem / (cloud_mem//100+1)
        # SLICE	CPU USAGE (%)
        # 1	40
        # 2	55
        # 3	50
        # ----------
        # Slice 1 and 2 executed together and almost used all cpu in env,
        # Slice 3 assigned later. To calculate total usage use following formula: 145/(145//100+1)

    ### log throughput
    # for smartgateway
    envtype=0
    throughputs = utils.f_read_plot_dict(utils.get_throughputs_log_file(envtype))
    smartgateway_throughput /= INFERENCE_RUN_TIME
    throughputs[metrics_id] = utils.get_sum_in_dict(throughputs, metrics_id, smartgateway_throughput)
    utils.debug_throughput(throughputs, envtype)
    # for fog
    envtype=1
    throughputs = utils.f_read_plot_dict(utils.get_throughputs_log_file(envtype))
    fog_throughput /= INFERENCE_RUN_TIME
    throughputs[metrics_id] = utils.get_sum_in_dict(throughputs, metrics_id, fog_throughput) 
    utils.debug_throughput(throughputs, envtype)
    # for cloud
    envtype=2
    throughputs = utils.f_read_plot_dict(utils.get_throughputs_log_file(envtype))
    cloud_throughput /= INFERENCE_RUN_TIME
    throughputs[metrics_id] = utils.get_sum_in_dict(throughputs, metrics_id, cloud_throughput) 
    utils.debug_throughput(throughputs, envtype)


    ### log communication time
    # for smartgateway
    envtype=0
    commtimes = utils.f_read_plot_dict(utils.get_commtimes_log_file(envtype))
    smartgateway_commtimes /= INFERENCE_RUN_TIME
    commtimes[metrics_id] = utils.get_sum_in_dict(commtimes, metrics_id, smartgateway_commtimes) 
    utils.debug_commtime(commtimes, envtype)
    # for fog
    envtype=1
    commtimes = utils.f_read_plot_dict(utils.get_commtimes_log_file(envtype))
    fog_commtimes /= INFERENCE_RUN_TIME
    commtimes[metrics_id] = utils.get_sum_in_dict(commtimes, metrics_id, fog_commtimes)
    utils.debug_commtime(commtimes, envtype)
    # for cloud
    envtype=2
    commtimes = utils.f_read_plot_dict(utils.get_commtimes_log_file(envtype))
    cloud_commtimes /= INFERENCE_RUN_TIME
    commtimes[metrics_id] = utils.get_sum_in_dict(commtimes, metrics_id, cloud_commtimes) 
    utils.debug_commtime(commtimes, envtype)


    ### log cpu percentages
    # for fog
    cpus = utils.f_read_plot_dict(utils.get_fog_cpu_percentage_log_file())
    fog_cpu /= INFERENCE_RUN_TIME
    cpus[metrics_id] = utils.get_sum_in_dict(cpus, metrics_id, fog_cpu) 
    utils.debug_fog_cpu_percentage(cpus)
    # for cloud
    cpus = utils.f_read_plot_dict(utils.get_cloud_cpu_percentage_log_file())
    cloud_cpu /= INFERENCE_RUN_TIME
    cpus[metrics_id] = utils.get_sum_in_dict(cpus, metrics_id, cloud_cpu) 
    utils.debug_cloud_cpu_percentage(cpus)


    ### log mem percentages
    # for fog
    mems = utils.f_read_plot_dict(utils.get_fog_mem_percentage_log_file())
    fog_mem /= INFERENCE_RUN_TIME
    mems[metrics_id] = utils.get_sum_in_dict(mems, metrics_id, fog_mem) 
    utils.debug_fog_mem_percentage(mems)
    # for cloud
    mems = utils.f_read_plot_dict(utils.get_cloud_mem_percentage_log_file())
    cloud_mem /= INFERENCE_RUN_TIME
    mems[metrics_id] = utils.get_sum_in_dict(mems, metrics_id, cloud_mem) 
    utils.debug_cloud_mem_percentage(mems)