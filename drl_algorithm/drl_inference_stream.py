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
    # setup webcam
    cap = cv2.VideoCapture("input/streaming.mp4") #cv2.VideoCapture(0)
    if not cap.isOpened():
        raise IOError("Cannot open webcam")
    service_id = 1
    slice_index = 0
    frame_counter = 0
    all_frames = []
    slice_frames = []
    elapsed_sets = set()
    start_time = time.time()
    while True:
        _, frame = cap.read()
        frame_counter += 1
        frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        cv2.imshow('Input', frame)

        sr_folder =  f"sr{service_id}"

        is_all_frames_done, is_slice_frames_done = \
            input_make_slices_by_frame(all_frames, slice_frames, frame, elapsed_sets, start_time)
        if is_slice_frames_done:
            slices_folder = f"{sr_folder}_slices"
            slice_mp4 = f"sr{service_id}_{slice_index}.mp4"
            input_save_frames(slice_frames, f"{input_stream_folder}/{sr_folder}/{slices_folder}", slice_mp4)
            slice_index += 1
        if is_all_frames_done:
            sr_mp4 = f"sr{service_id}.mp4"
            input_save_frames(all_frames, f"{input_stream_folder}/{sr_folder}", sr_mp4)
            model_thread = threading.Thread(target=run_model_thread, args=(service_id,))
            model_thread.start()
            service_id += 1
            slice_index = 0
            all_frames = []
            slice_frames = []
            elapsed_sets = set()
            start_time = time.time()

        if is_slice_frames_done or is_all_frames_done:
            slice_frames = []


        if cv2.waitKey(1) == 27:
            break
        if frame_counter == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            frame_counter = 0
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    cap.release()

def input_make_slices_by_frame(all_frames, slice_frames, frame, elapsed_sets, start_time):
    is_all_frames_done = False
    is_slice_frames_done = False
    all_frames.append(frame)
    slice_frames.append(frame)
    elapsed_sets.add(time.time())
    is_slice_frames_done = True
    if len(elapsed_sets) == 6:
        is_all_frames_done = True
    return is_all_frames_done, is_slice_frames_done

def input_make_slices_by_time(all_frames, slice_frames, frame, elapsed_sets, start_time):
    is_all_frames_done = False
    is_slice_frames_done = False
    all_frames.append(frame)
    slice_frames.append(frame)
    slicing_duration = 1 # seconds
    requesting_duration = 6 # seconds
    elapsed_time = round((time.time() - start_time))
    if elapsed_time % slicing_duration==0 and elapsed_time not in elapsed_sets and elapsed_time != 0:
        elapsed_sets.add(elapsed_time)
        is_slice_frames_done = True
    if elapsed_time >= requesting_duration:
        is_all_frames_done = True
    return is_all_frames_done, is_slice_frames_done

def input_save_frames(frames, folder, filename):
    fps = 30
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    frame_width, frame_height = frames[0].shape[1], frames[0].shape[0]
    if not os.path.exists(folder):
        os.makedirs(folder)
    out = cv2.VideoWriter(f"{folder}/{filename}", fourcc, fps, (frame_width, frame_height))
    for frame in frames:
        out.write(frame)
    out.release()

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
def run_model_thread(service_id):
    with semaphore:
        run_model(service_id)
        time.sleep(3)

def run_model(service_id):
    service_type = 1
    service_count = 1
    slice_count = 6
    DynamicParams.set_params(service_type, service_count, slice_count)
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
    environment = Environment(users)
    environment.reset()

    # load back the model
    model_name = f"models/model_{app_type}_{(services_count*slices_count)}.pth"
    model = DRLModel(input_layer_size, hidden_layer_size, output_layer_size)
    state_dict = torch.load(model_name)
    model.load_state_dict(state_dict)

    total_reward = 0
    while not done:
        # get state
        state = environment.get_state_space()

        # get action 
        action = get_model_action(model, state, output_layer_size)

        # perform action and get new state
        reward, done, _ = environment.step(action)
        total_reward += reward

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

