import os
import cv2
import time
import torch
import shutil
import random
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from c_service_1 import Service1
from drl_model import DRLModel
from drl_environment import Environment
import h_utils_state_space as ssutils
from c_user_factory import generate_users
from c_system_modelling import set_users_priorities
from drl_agent_factory import generate_agent
import h_utils as utils
from h_configs import SERVICE1_OUTPUT_PATH_LIST, SERVICE1_FOG_ENDPOINT, SERVICE1_CLOUD_ENDPOINT, \
    SERVICE_SENSITIVITY, DynamicParams

### GENERAL
input_stream_folder = "input_stream"
output_stream_folder = "output_stream"
semaphore = threading.Semaphore(value=1)

def run_inference():
    if os.path.exists(input_stream_folder):
        shutil.rmtree(input_stream_folder)
    if os.path.exists(output_stream_folder):
        shutil.rmtree(output_stream_folder)
    if not os.path.exists(output_stream_folder):
        os.makedirs(output_stream_folder)

    input_thread = threading.Thread(target=input_run_stream)
    input_thread.start()
    watcher_thread = threading.Thread(target=start_watcher, args=(output_stream_folder,))
    watcher_thread.start()
    input_thread.join()
    watcher_thread.join()
    cv2.destroyAllWindows()

### INPUT PART
def input_run_stream():
    # setup settings
    slice_index = 0
    service_id = 1
    current_slice_frame = 0
    current_sr_frame = 0
    out_slice = None
    out_sr = None
    # setup webcam settings
    cap = cv2.VideoCapture("input/streaming.mp4") #cv2.VideoCapture(0)
    if not cap.isOpened():
        raise IOError("Cannot open webcam")
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_slice_sec = int(fps * 1)
    frame_sr_sec = int(fps * 6)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, ((service_id-1)*frame_sr_sec))
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('Input', frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
        # frames tracker
        current_slice_frame += 1
        current_sr_frame += 1
        # sr folder, file setting
        sr_folder = f"sr{service_id}"
        out_sr_folder = f"{input_stream_folder}/{sr_folder}"
        sr_name = f"sr{service_id}.mp4"
        out_sr_name = f"{out_sr_folder}/{sr_name}"
        # slice folder, file setting
        slice_folder = f"{sr_folder}_slices"
        out_slice_folder = f"{input_stream_folder}/{sr_folder}/{slice_folder}"
        slice_name = f"sr{service_id}_{slice_index}.mp4"
        out_slice_name = f"{out_slice_folder}/{slice_name}"
        # save input frames
        if out_slice is None:
            if not os.path.exists(out_slice_folder):
                os.makedirs(out_slice_folder)
            out_slice = cv2.VideoWriter(f"{out_slice_name}", cv2.VideoWriter_fourcc(*'mp4v'), fps, (int(cap.get(3)), int(cap.get(4))))
        if out_sr is None:
            if not os.path.exists(out_sr_folder):
                os.makedirs(out_sr_folder)
            out_sr = cv2.VideoWriter(f"{out_sr_name}", cv2.VideoWriter_fourcc(*'mp4v'), fps, (int(cap.get(3)), int(cap.get(4))))
        if current_slice_frame <= frame_slice_sec:
            out_slice.write(frame)
            if current_slice_frame == frame_slice_sec:
                out_slice.release()
                out_slice = None
                slice_index += 1
                current_slice_frame = 0
        if current_sr_frame <= frame_sr_sec:
            out_sr.write(frame)
            if current_sr_frame == frame_sr_sec:
                slices_count = slice_index
                model_thread = threading.Thread(target=run_model_thread, args=(service_id, slices_count))
                model_thread.start()
                out_sr.release()
                out_sr = None
                service_id += 1
                slice_index = 0
                current_sr_frame = 0
        current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        if current_frame == total_frames:
            slices_count = slice_index + 1
            model_thread = threading.Thread(target=run_model_thread, args=(service_id, slices_count))
            model_thread.start()

    cap.release()


### OUTPUT PART
def output_play_video(video_path):
    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            cv2.imshow('Output', frame)
            if cv2.waitKey(25) & 0xFF == 27:
                break
        else:
            break

    cap.release()

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
def run_model_thread(service_id, slices_count):
    with semaphore:
        run_model(service_id, slices_count)
        time.sleep(3)

def run_model(service_id, slices_count):
    app_type = 1
    service_count = 1
    DynamicParams.set_params(app_type, service_count, slices_count)
    run_model_helper(service_id)

def run_model_helper(service_id):
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
    service = Service1(
                id = service_id, 
                user = user,
                sensitivity = service_sensitity, 
                slice_count = DynamicParams.get_params()['slice_count'], 
                input_path_list = [f"{input_stream_folder}/sr{service_id}/sr{service_id}.mp4"], 
                output_path_list = SERVICE1_OUTPUT_PATH_LIST,
                api_endpoint_list = [SERVICE1_FOG_ENDPOINT, SERVICE1_CLOUD_ENDPOINT]
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
                metrics_logger(slices_tracker)
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
                metrics_logger(slices_tracker)

        # store the transition (s, a, r, d, s′) in the long memory
        agent.train_long_memory()

    # copy to output stream folder
    file_name = f"{SERVICE1_OUTPUT_PATH_LIST[1]}_final.{SERVICE1_OUTPUT_PATH_LIST[2]}"
    src_path = SERVICE1_OUTPUT_PATH_LIST[0] + "/" + f"user{user.id}" + '/' + f"service{service.id}" + "/" + file_name
    dest_path = output_stream_folder + "/" + file_name
    shutil.copyfile(src_path, dest_path)

def get_model_action(model, state, output_layer_size):
    action = [0] * output_layer_size
    with torch.no_grad():
        state0 = torch.tensor(state, dtype = torch.float)
        prediction = model(state0)
        prediction = torch.argmax(prediction).item()
    action[prediction] = 1
    return action

def metrics_logger(slices_tracker):
    ### collect metrics
    fog_cpu = 0; cloud_cpu = 0; fog_mem = 0; cloud_mem = 0
    fog_frames = 0; cloud_frames = 0; smartgateway_frames = 0
    fog_commtimes = 0; cloud_commtimes = 0; smartgateway_commtimes = 0
    for _, value in slices_tracker.items():
        env = value.assigned_env
        frames = value.slice_frame_count
        commtime = value.slice_execution_time
        if env == 1:
            fog_frames += frames
            fog_commtimes += commtime
            fog_cpu += value.slice_cpu_demand_ratio
            fog_mem += value.slice_mem_demand_ratio
        if env == 2:
            cloud_frames += frames
            cloud_commtimes += commtime
            cloud_cpu += value.slice_cpu_demand_ratio
            cloud_mem += value.slice_mem_demand_ratio
        smartgateway_frames += frames
        smartgateway_commtimes += commtime


    ### log throughput
    # for smartgateway
    envtype=0
    throughputs = utils.f_read_plot_list(utils.get_throughputs_log_file(envtype))
    throughputs.append(smartgateway_frames)
    utils.debug_throughput(throughputs, envtype)
    # for fog
    envtype=1
    throughputs = utils.f_read_plot_list(utils.get_throughputs_log_file(envtype))
    throughputs.append(fog_frames)
    utils.debug_throughput(throughputs, envtype)
    # for cloud
    envtype=2
    throughputs = utils.f_read_plot_list(utils.get_throughputs_log_file(envtype))
    throughputs.append(cloud_frames)
    utils.debug_throughput(throughputs, envtype)


    ### log communication time
    # for smartgateway
    envtype=0
    commtimes = utils.f_read_plot_list(utils.get_commtimes_log_file(envtype))
    commtimes.append(smartgateway_commtimes)
    utils.debug_commtime(commtimes, envtype)
    # for fog
    envtype=1
    commtimes = utils.f_read_plot_list(utils.get_commtimes_log_file(envtype))
    commtimes.append(fog_commtimes)
    utils.debug_commtime(commtimes, envtype)
    # for cloud
    envtype=2
    commtimes = utils.f_read_plot_list(utils.get_commtimes_log_file(envtype))
    commtimes.append(cloud_commtimes)
    utils.debug_commtime(commtimes, envtype)


    ### log cpu percentages
    # for fog
    cpus = utils.f_read_plot_list(utils.get_fog_cpu_percentage_log_file())
    cpus.append(fog_cpu)
    utils.debug_fog_cpu_percentage(cpus)
    # for cloud
    cpus = utils.f_read_plot_list(utils.get_cloud_cpu_percentage_log_file())
    cpus.append(cloud_cpu)
    utils.debug_cloud_cpu_percentage(cpus)


    ### log mem percentages
    # for fog
    mems = utils.f_read_plot_list(utils.get_fog_mem_percentage_log_file())
    mems.append(fog_mem)
    utils.debug_fog_mem_percentage(mems)
    # for cloud
    mems = utils.f_read_plot_list(utils.get_cloud_mem_percentage_log_file())
    mems.append(cloud_mem)
    utils.debug_cloud_mem_percentage(mems)

