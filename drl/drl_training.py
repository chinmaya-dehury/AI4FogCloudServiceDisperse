import torch
import numpy as np
from c_user_factory import generate_users
from c_service_factory import generate_services_for_users
from c_system_modelling import set_users_priorities, get_efficient_times_to_allocate_services
from drl_agent_factory import generate_agent
from drl_environment import Environment
import h_utils as utils
from h_configs import EPISODES, Params
import h_utils_state_space as ssutils

def train():
    # set seeds
    seed = 42
    torch.manual_seed(seed)
    np.random.seed(seed)

    # set cuda
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    if torch.cuda.is_available():
        print(f"Cuda is enabled: {torch.cuda.get_device_name(0)}")

    # set count of slices, count of services
    slices_count = Params.get_params()['slice_count']
    services_count = Params.get_params()['service_count']

    # generate agent
    input_layer_size = ssutils.get_state_space_len(services_count, slices_count)
    hidden_layer_size = input_layer_size * 2
    output_layer_size = ssutils.get_state_space_len(services_count, slices_count)
    agent = generate_agent(input_layer_size, hidden_layer_size, output_layer_size)

    # start training
    episode_rewards = []
    episode_losses = []
    episode_success = []
    total_episode_reward = 0
    total_episode_loss = 0
    total_episode_success = 0
    for episode in range(EPISODES):
        # increment agent episodeations
        agent.n_iterations += 1

        if (episode % 1000 == 0):
            # reset environments configuration
            # Cloud.reset()
            # Fog.reset()
            # SmartGateway.reset()
            
            # generate users. 
            # user object need for several cases such as:
            # 1. keeping track of user priorities;
            # 2. keeping track of what services are availing by user;
            # 3. etc
            users = generate_users(n=1)
            set_users_priorities(users)

            # generate services for each users
            generate_services_for_users(users)
            services = [service for user in users for service in user.services]

            if (len(services) != services_count):
                raise Exception(f"The length of services should be match!")

            # calculate efficient times for success rate measurement
            # efficient_times = get_efficient_times_to_allocate_services(users, services)

            # debug necessary information
            utils.debug_users(users, is_printable=True)
            utils.debug_services(services, is_printable=True)
            utils.debug_fog(is_printable=True)
            utils.debug_cloud(is_printable=True)

            # generate environment
            environment = Environment(users)

        done = False
        environment.reset()
    
        total_times = 0
        episode_reward = 0
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

            if not done:
                total_times += 1

            #log, print
            utils.debug(log_msg=
                f"Users: {len(users)}, Services: {services_count}, Slices per Service: {slices_count} , \n" + \
                f"Total times: {total_times}, Action has chosen by {chosen} \n" + \
                f"Episode: {agent.n_iterations},  Current Reward = {reward}, Eplisode Reward = {episode_reward}, Done = {done}, \n" + \
                f"Total Slices: {info[1]}, Total Assigned Slices: {info[2]}, \n" + \
                f"Slices tracker:  {info[0]}, \n",
                #"\n\n",
                is_printable=True)

            #log, print
            utils.debug(log_msg=
                f"Current state:  {str(current_state)}, \n" + \
                f"Action:         {action}, \n" + \
                f"Next state:     {str(next_state)}" +\
                "\n\n",
                is_printable=False)

        # store the transition (s, a, r, d, s′) in the long memory
        agent.train_long_memory()

        # store episode reward
        total_episode_reward += episode_reward
        episode_rewards.append(total_episode_reward/agent.n_iterations)
        utils.debug_rewards(episode_rewards)

        # store losses
        total_episode_loss += agent.get_loss()
        episode_losses.append(total_episode_loss/agent.n_iterations)
        utils.debug_losses(episode_losses)

        # store success
        total_episode_success +=- 0 if episode_reward < 0 else 1/total_times*100
        episode_success.append(total_episode_success/agent.n_iterations)
        utils.debug_success_rates(episode_success)

    # save plots
    ### save rewards
    rewards = utils.f_read_plot_list(utils.get_rewards_log_file())
    utils.f_save_plot_list(rewards, "Iterations", "Rewards", utils.get_rewards_plot_file())
    ### save losses
    losses = utils.f_read_plot_list(utils.get_losses_log_file())
    utils.f_save_plot_list(losses, "Iterations", "Losses", utils.get_losses_plot_file())
    ### save together
    utils.f_save_plot_lists(EPISODES, rewards, losses, utils.get_together_plot_file())
    ### save success
    success_rates = utils.f_read_plot_list(utils.get_success_log_file())
    utils.f_save_plot_list(success_rates, "Iterations", "Success Rates", utils.get_success_plot_file())

    # save model
    agent.model.save()
