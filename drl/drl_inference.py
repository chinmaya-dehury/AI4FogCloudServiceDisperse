import time
import torch
from drl_model import DRLModel
from drl_environment import Environment
import h_utils_state_space as ssutils
from c_user_factory import generate_users
from c_system_modelling import set_users_priorities
from c_service_factory import generate_services_for_users
from h_configs import TRAINING_SERVICE_SLICE_PAIRS, DynamicParams

def run_inference():
    for _, value in TRAINING_SERVICE_SLICE_PAIRS.items():
        service_type = value[0]
        service_count = value[1]
        slice_count = value[2]
        DynamicParams.set_params(service_type, service_count, slice_count)
        print(f"Inference is starting for App{service_type} with SRs = {service_count} and Slices = {slice_count}")
        start_time = time.time()
        run_inference_helper()
        end_time = time.time()
        execution_time = (end_time-start_time)/60
        print(f"End of inference for App{service_type}. Total Execution time is {execution_time} minutes")
        print("\n\n")

def run_inference_helper():
    # get count of slices, count of services
    app_type = DynamicParams.get_params()['service_type']
    slices_count = DynamicParams.get_params()['slice_count']
    services_count = DynamicParams.get_params()['service_count']

    # generate
    input_layer_size = ssutils.get_state_space_len(services_count, slices_count)
    hidden_layer_size = input_layer_size * 2
    output_layer_size = ssutils.get_state_space_len(services_count, slices_count)

    # generate users
    users = generate_users(n=1)
    set_users_priorities(users)

    # generate services for each users
    generate_services_for_users(users)

    # init environment
    done = False
    environment = Environment(users)
    environment.reset()

    # load back the model
    model_name = f"models/model_{app_type}_{(services_count*slices_count)}.pth"
    model = DRLModel(input_layer_size, hidden_layer_size, output_layer_size)
    state_dict = torch.load(model_name)
    model.load_state_dict(state_dict)
    print(f"Model is loaded: {model_name}")

    total_reward = 0
    while not done:
        # get state
        state = environment.get_state_space()

        # get action 
        action = get_action(model, state, output_layer_size)

        # perform action and get new state
        reward, done, _ = environment.step(action)
        total_reward += reward
        print(f"App:{app_type}  Total slice: {(services_count*slices_count)}  Total Reward:{total_reward}  Done:{done}")


def get_action(model, state, output_layer_size):
    action = [0] * output_layer_size
    with torch.no_grad():
        state0 = torch.tensor(state, dtype = torch.float)
        prediction = model(state0)
        prediction = torch.argmax(prediction).item()
    action[prediction] = 1
    return action