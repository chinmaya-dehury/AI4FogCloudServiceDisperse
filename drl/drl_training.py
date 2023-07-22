import time
import torch
import numpy as np
from c_user_factory import generate_users
from c_service_factory import generate_services_for_users
from c_system_modelling import set_users_priorities
from drl_agent_factory import generate_agent
from drl_environment import Environment
import h_utils as utils
from h_configs import EPISODES, TRAINING_SERVICE_SLICE_PAIRS, DynamicParams
import h_utils_state_space as ssutils

def train():
    for _, value in TRAINING_SERVICE_SLICE_PAIRS.items():
        service_type = value[0]
        service_count = value[1]
        slice_count = value[2]
        DynamicParams.set_params(service_type, service_count, slice_count)
        print(f"Training is starting for App{service_type} with SRs = {service_count} and Slices = {slice_count}")
        start_time = time.time()
        train_helper()
        end_time = time.time()
        execution_time = (end_time-start_time)/60
        print(f"End of training for App{service_type}. Total Execution time is {execution_time} minutes")

def train_helper():
    # setup pytorch
    setup_pytorch()

    # set count of slices, count of services
    slices_count = DynamicParams.get_params()['slice_count']
    services_count = DynamicParams.get_params()['service_count']

    # generate agent
    input_layer_size = ssutils.get_state_space_len(services_count, slices_count)
    hidden_layer_size = input_layer_size * 2
    output_layer_size = ssutils.get_state_space_len(services_count, slices_count)
    agent = generate_agent(input_layer_size, hidden_layer_size, output_layer_size)

    # generate users
    users = generate_users(n=1)
    set_users_priorities(users)

    # generate services for each users
    generate_services_for_users(users)
    services = [service for user in users for service in user.services]

    if (len(services) != services_count):
        raise Exception(f"The length of services should be match!")

    # debug necessary information
    utils.debug_users(users, is_printable=True)
    utils.debug_services(services, is_printable=True)
    utils.debug_fog(is_printable=True)
    utils.debug_cloud(is_printable=True)

    # generate environment
    environment = Environment(users)

    # keep infos during each episode
    episode_success_rates = []
    episode_rewards = []; episode_losses = []; episode_missed_deadlines = []
    episode_fog_percentages = []; episode_cloud_percentages = []
    episode_fog_cpu_percentages = []; episode_cloud_cpu_percentages = []
    episode_fog_mem_percentages = []; episode_cloud_mem_percentages = []

    # start training
    for episode in range(EPISODES):
        episode_reward = 0
        episode_missed_deadline = 0
        agent.n_iterations += 1

        done = False
        slices_tracker = None
        environment.reset()
        while not done:
            # observe the current state s
            current_state = environment.get_state_space()
            
            # select an action a
            action, chosen = agent.get_action(current_state)

            # execute the action a, move to the next state s′ and observe the reward r
            reward, done, info = environment.step(action)
            next_state = environment.get_state_space()

            # store the transition (s, a, r, d, s′) in the buffer
            agent.train_short_memory(current_state, action, reward, done, next_state)

            agent.remember(current_state, action, reward, done, next_state)

            episode_reward += reward
            episode_reward = round(episode_reward, 3)
            episode_missed_deadline = info[3]

            slices_tracker = info[0]

            print(f"Episode = {episode}/{EPISODES}  Reward = {reward}  Episode Reward = {episode_reward}  " +
                    f"Miss deadline = {episode_missed_deadline}  Action = {action.index(1)}  ActionBy = {chosen}  Done = {done}")

        # store the transition (s, a, r, d, s′) in the long memory
        agent.train_long_memory()
        # store episode reward
        episode_rewards.append(episode_reward)
        # store losses
        episode_losses.append(agent.get_loss())
        # store success rates
        total_slices = services_count * slices_count
        missed_slices = episode_missed_deadline
        episode_success_rate = ((total_slices-missed_slices)/total_slices)*100
        episode_success_rates.append(episode_success_rate)
        # store missed deadlines
        episode_missed_rate = (missed_slices/total_slices)*100
        episode_missed_deadlines.append(episode_missed_rate)
        # store fog and cloud percentages
        store_fog_cloud_infos(slices_tracker, episode_fog_percentages, episode_cloud_percentages, episode_fog_cpu_percentages, 
                              episode_cloud_cpu_percentages, episode_fog_mem_percentages, episode_cloud_mem_percentages)

    # save model
    agent.model.save()
    # save plots
    save_plots(episode_rewards, episode_losses, episode_fog_percentages, episode_cloud_percentages, episode_fog_cpu_percentages, 
                episode_cloud_cpu_percentages, episode_fog_mem_percentages, episode_cloud_mem_percentages, episode_missed_deadlines,
                episode_success_rates)

def setup_pytorch():
    # set seeds
    seed = 42
    torch.manual_seed(seed)
    np.random.seed(seed)

    # set cuda
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    if torch.cuda.is_available():
        print(f"Cuda is enabled: {torch.cuda.get_device_name(0)}")

def store_fog_cloud_infos(slices_tracker, episode_fog_percentages, episode_cloud_percentages, episode_fog_cpu_percentages, 
                          episode_cloud_cpu_percentages, episode_fog_mem_percentages, episode_cloud_mem_percentages):

    slices_count = DynamicParams.get_params()['slice_count']
    services_count = DynamicParams.get_params()['service_count']

    if slices_tracker is not None and len(slices_tracker) == (services_count * slices_count):
        fog_count = 0; cloud_count = 0
        fog_cpu_demand = 0; cloud_cpu_demand = 0; total_cpu_demand = 0
        fog_mem_demand = 0; cloud_mem_demand = 0; total_mem_demand = 0
        for slice_info in slices_tracker.values():
            if slice_info.assigned_env == 1:
                fog_count += 1
                fog_cpu_demand += slice_info.cpu_demand
                fog_mem_demand += slice_info.mem_demand
            elif slice_info.assigned_env == 2:
                cloud_count += 1
                cloud_cpu_demand += slice_info.cpu_demand
                cloud_mem_demand += slice_info.mem_demand
            total_cpu_demand += slice_info.total_cpu_demand
            total_mem_demand += slice_info.total_mem_demand
        episode_fog_percentage = fog_count/len(slices_tracker) * 100
        episode_cloud_percentage = cloud_count/len(slices_tracker) * 100
        episode_fog_cpu_percentage = fog_cpu_demand/total_cpu_demand * 100
        episode_cloud_cpu_percentage = cloud_cpu_demand/total_cpu_demand * 100
        episode_fog_mem_percentage = fog_mem_demand/total_mem_demand*100
        episode_cloud_mem_percentage = cloud_mem_demand/total_mem_demand*100
    else:
        episode_fog_percentage = 50
        episode_cloud_percentage = 50
        episode_fog_cpu_percentage = 50
        episode_cloud_cpu_percentage = 50
        episode_fog_mem_percentage = 50
        episode_cloud_mem_percentage = 50
    episode_fog_percentages.append(episode_fog_percentage)
    episode_cloud_percentages.append(episode_cloud_percentage)
    episode_fog_cpu_percentages.append(episode_fog_cpu_percentage)
    episode_cloud_cpu_percentages.append(episode_cloud_cpu_percentage)
    episode_fog_mem_percentages.append(episode_fog_mem_percentage)
    episode_cloud_mem_percentages.append(episode_cloud_mem_percentage)

def save_plots(episode_rewards, episode_losses, episode_fog_percentages, episode_cloud_percentages, episode_fog_cpu_percentages, 
               episode_cloud_cpu_percentages, episode_fog_mem_percentages, episode_cloud_mem_percentages, episode_missed_deadlines,
               episode_success_rates):
    
    episode_range = list(range(1, EPISODES+1))
    
    # divide 1000
    episode_range = list(range(1, 10+1))
    episode_rewards = utils.divide_1000(episode_rewards)
    episode_losses = utils.divide_1000(episode_losses)
    episode_success_rates = utils.divide_1000(episode_success_rates)
    episode_missed_deadlines = utils.divide_1000(episode_missed_deadlines)
    episode_fog_percentages = utils.divide_1000(episode_fog_percentages)
    episode_cloud_percentages = utils.divide_1000(episode_cloud_percentages)
    episode_fog_cpu_percentages = utils.divide_1000(episode_fog_cpu_percentages)
    episode_cloud_cpu_percentages = utils.divide_1000(episode_cloud_cpu_percentages)
    episode_fog_mem_percentages = utils.divide_1000(episode_fog_mem_percentages)
    episode_cloud_mem_percentages = utils.divide_1000(episode_cloud_mem_percentages)

    # cummulative average
    episode_rewards = utils.cum_avg(episode_rewards)
    # episode_success_rates = utils.cum_avg(episode_success_rates)
    # episode_missed_deadlines = utils.cum_avg(episode_missed_deadlines)

    # save logs
    utils.debug_rewards(episode_rewards)
    utils.debug_losses(episode_losses)
    utils.debug_success_rates(episode_success_rates)
    utils.debug_missed_deadlines(episode_missed_deadlines)
    utils.debug_fog_percentage(episode_fog_percentages)
    utils.debug_cloud_percentage(episode_cloud_percentages)
    utils.debug_fog_cpu_percentage(episode_fog_cpu_percentages)
    utils.debug_cloud_cpu_percentage(episode_cloud_cpu_percentages)
    utils.debug_fog_mem_percentage(episode_fog_mem_percentages)
    utils.debug_cloud_mem_percentage(episode_cloud_mem_percentages)

    # save plots
    utils.f_save_plot_list(episode_rewards, "Episodes", "Cummulative Average Rewards", utils.get_rewards_plot_file())
    utils.f_save_plot_list(episode_losses,  "Episodes", "Losses", utils.get_losses_plot_file())
    utils.f_save_plot_list(episode_success_rates,  "Episodes", "Success Rates", utils.get_success_plot_file())
    utils.f_save_plot_list(episode_missed_deadlines,  "Episodes", "Missed Deadlines", utils.get_missed_deadlines_plot_file())
    # utils.f_save_plot_bar(episode_range, episode_missed_deadlines,  "Episodes", "Missed Deadlines", utils.get_missed_deadlines_plot_file())
    utils.f_save_plot_bar_2(episode_range, episode_fog_percentages, episode_cloud_percentages, "Episodes", "Percentage of Slices", utils.get_slices_percentage_plot_file())
    utils.f_save_plot_bar_2(episode_range, episode_fog_cpu_percentages, episode_cloud_cpu_percentages, "Episodes", "Percentage of CPU", utils.get_cpu_percentage_plot_file())
    utils.f_save_plot_bar_2(episode_range, episode_fog_mem_percentages, episode_cloud_mem_percentages, "Episodes", "Percentage of MEM", utils.get_mem_percentage_plot_file())
