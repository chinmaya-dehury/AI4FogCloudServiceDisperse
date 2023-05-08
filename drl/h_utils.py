import os
import ast
import random
import shutil
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from tcp_latency import measure_latency
from c_env_cloud import Cloud
from c_env_fog import Fog
from h_configs import Params, PLOT_FOLDER, LOG_FOLDER, LOG_OUTPUT_PATH, \
    PLOT_LOG_REWARDS_OUTPUT_PATH, PLOT_LOG_LOSSES_OUTPUT_PATH, PLOT_LOG_SUCCESS_OUTPUT_PATH, \
    PLOT_PNG_REWARDS_OUTPUT_PATH, PLOT_PNG_LOSSES_OUTPUT_PATH, PLOT_PNG_TOGETHER_OUTPUT_PATH, PLOT_PNG_SUCCESS_OUTPUT_PATH \

############################################################################################################ OTHER HELPER FUNCTIONS

def get_latency(host, port):
	result = measure_latency(host, port)
	if isinstance(result, list):
		if len(result) > 0:
			result = sum(result) / len(result)
		else:
			result = 1
	latency = round(result, 2)
	return latency

# divides N into M unequal parts
def divide_unequal(N, M):
    parts = {}
    total = 0
    for m in range(M-1):
        part = random.uniform(0, N-total)
        parts[m] = round(part)
        total += part
    parts[M-1] = round(N-total)
    return parts

#################################################################################################################### DEBUGGING

def get_rewards_log_file():
    # create log folder if not exists
    if not os.path.exists(PLOT_FOLDER):
         os.makedirs(PLOT_FOLDER)

    log_file = PLOT_LOG_REWARDS_OUTPUT_PATH.format(PLOT_FOLDER, Params.get_params()['service_count'], Params.get_params()['slice_count'])

    return log_file

def get_losses_log_file():
    # create log folder if not exists
    if not os.path.exists(PLOT_FOLDER):
         os.makedirs(PLOT_FOLDER)

    log_file = PLOT_LOG_LOSSES_OUTPUT_PATH.format(PLOT_FOLDER, Params.get_params()['service_count'], Params.get_params()['slice_count'])

    return log_file

def get_success_log_file():
    # create log folder if not exists
    if not os.path.exists(PLOT_FOLDER):
         os.makedirs(PLOT_FOLDER)

    log_file = PLOT_LOG_SUCCESS_OUTPUT_PATH.format(PLOT_FOLDER, Params.get_params()['service_count'], Params.get_params()['slice_count'])

    return log_file     

def get_rewards_plot_file():
    # create log folder if not exists
    if not os.path.exists(PLOT_FOLDER):
         os.makedirs(PLOT_FOLDER)

    plot_file = PLOT_PNG_REWARDS_OUTPUT_PATH.format(PLOT_FOLDER, Params.get_params()['service_count'], Params.get_params()['slice_count'])

    return plot_file

def get_losses_plot_file():
    # create log folder if not exists
    if not os.path.exists(PLOT_FOLDER):
         os.makedirs(PLOT_FOLDER)

    plot_file = PLOT_PNG_LOSSES_OUTPUT_PATH.format(PLOT_FOLDER, Params.get_params()['service_count'], Params.get_params()['slice_count'])

    return plot_file

def get_together_plot_file():
    # create log folder if not exists
    if not os.path.exists(PLOT_FOLDER):
         os.makedirs(PLOT_FOLDER)

    plot_file = PLOT_PNG_TOGETHER_OUTPUT_PATH.format(PLOT_FOLDER, Params.get_params()['service_count'], Params.get_params()['slice_count'])

    return plot_file

def get_success_plot_file():
    # create log folder if not exists
    if not os.path.exists(PLOT_FOLDER):
         os.makedirs(PLOT_FOLDER)

    plot_file = PLOT_PNG_SUCCESS_OUTPUT_PATH.format(PLOT_FOLDER, Params.get_params()['service_count'], Params.get_params()['slice_count'])

    return plot_file

def clear_logs():
    folder_path = LOG_FOLDER
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")

log_file = None
log_line_counter = 0
def debug(log_msg, is_printable=False):
    global log_file
    global log_line_counter

    # create log folder if not exists
    log_folder = f"{LOG_FOLDER}/{Params.get_params()['service_count']}_{Params.get_params()['slice_count']}"
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    # split logs into different parts to avoid large log files
    if log_line_counter % 1000 == 0:
        log_line_counter = 0
        cur_date = datetime.now().strftime("%m_%d_%H_%M")
        log_file = LOG_OUTPUT_PATH.format(log_folder, cur_date)

    # write to log
    logfile = open(log_file, "a")
    logfile.write(log_msg)
    logfile.close()
	
    # print to console
    if (is_printable):
        print(log_msg)

    # increment log_line_counter
    log_line_counter += 1

def debug_users(users, is_printable=False):
    log_msg = "Users: \n"
    for user in users:
        log_msg += f"\tUser{user.id}: \n" + \
                f"\t\tpriority = {user.get_user_priority()}, services = {len(user.get_services())}\n\n"
    debug(log_msg, is_printable)

def debug_services(services, is_printable=False):
    log_msg = "Services: \n"
    for service in services:
        # slice size, slice demands
        slices_size = ''
        slices_cpu_demand = ''
        slices_mem_demand = ''
        for slice_index in range(Params.get_params()['slice_count']):
            comma = "" if slice_index == Params.get_params()['slice_count'] - 1 else ", "
            slices_size += f"{service.get_slice_size(slice_index)}{comma}"
            slices_cpu_demand += f"{service.get_cpu_demand_per_slice(slice_index)}{comma}"
            slices_mem_demand += f"{service.get_mem_demand_per_slice(slice_index)}{comma}"
        # service print
        log_msg += f"\tService{service.id}: \n" + \
                    f"\t\tavailing_user = User{service.user.id}\n" + \
                    f"\t\ttype = {service.type}, sensitivity = {service.sensitivity}\n" + \
                    f"\t\tinput_size = {service.get_input_size()}, slices_size = [{slices_size}]\n" + \
                    f"\t\tbase_cpu_demand = {service.get_cpu_demand_base()}, base_mem_demand = {service.get_mem_demand_base()}\n" + \
                    f"\t\taux_cpu_demand = {service.get_cpu_demand_aux()}, aux_mem_demand = {service.get_mem_demand_aux()}\n" + \
                    f"\t\tcpu_demand_per_slice = [{slices_cpu_demand}], mem_demand_per_slice = [{slices_mem_demand}]\n" + \
                    "\n\n"
    debug(log_msg, is_printable)

def debug_fog(is_printable=False):
    log_msg = "Fog: \n" + \
        f"\t\tid = {Fog.get_id()}\n" + \
        f"\t\tavailable_cpu = {Fog.get_available_cpu()}, available_mem = {Fog.get_available_memory()}" +\
        "\n\n"
    debug(log_msg, is_printable)

def debug_cloud(is_printable=False):
    log_msg = "Cloud: \n" + \
        f"\t\tid = {Cloud.get_id()}\n" + \
        f"\t\tavailable_cpu = {Cloud.get_available_cpu()}, available_mem = {Cloud.get_available_memory()}" +\
        "\n\n"
    debug(log_msg, is_printable)

def debug_rewards(rewards, is_printable=False):

    log_file = get_rewards_log_file()

    # write to log
    logfile = open(log_file, "w")
    rewards_text = '['
    for reward in rewards:
        rewards_text += f'{reward},'
    rewards_text += ']'
    logfile.write(rewards_text)
    logfile.write("\n")
    logfile.close()
	
    # print to console
    if (is_printable):
        print(rewards_text)

def debug_losses(losses, is_printable=False):
    log_file = get_losses_log_file()

    # write to log
    logfile = open(log_file, "w")
    losses_text = '['
    for loss in losses:
        losses_text += f'{loss},'
    losses_text += ']'
    logfile.write(losses_text)
    logfile.write("\n")
    logfile.close()
	
    # print to console
    if (is_printable):
        print(losses_text)

def debug_success_rates(sucess_rates, is_printable=False):
    log_file = get_success_log_file()

    # write to log
    logfile = open(log_file, "w")
    sucess_rates_text = '['
    for success in sucess_rates:
        sucess_rates_text += f'{success},'
    sucess_rates_text += ']'
    logfile.write(sucess_rates_text)
    logfile.write("\n")
    logfile.close()
	
    # print to console
    if (is_printable):
        print(sucess_rates_text)

#################################################################################################################### PLOTTING

def f_read_plot_list(path):
    ls = []
    with open(path) as file_in:
        for line in file_in:
            ls = ast.literal_eval(line)
            break
    return ls

def f_save_plot_list(elements, x_title, y_title, output_path):
    plt.plot(elements, color='navy', linewidth=2)
    plt.xlabel(x_title, fontsize=14, fontweight='bold')
    plt.ylabel(y_title, fontsize=14, fontweight='bold')
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(axis='both', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    # plt.plot(elements)
    # plt.xlabel(x_title)
    # plt.ylabel(y_title)
    # plt.savefig(output_path)
    # plt.close("all")

def f_save_plot_lists(num_iterations, rewards, losses, output_path):
    data = pd.DataFrame({'Iteration': range(num_iterations), 'Reward': rewards, 'Loss': losses})
    plt.figure(figsize=(10, 6))
    plt.plot(data['Iteration'], data['Reward'], color='blue', label='Reward')
    rolling_loss = data['Loss'].rolling(window=10).mean()
    plt.plot(data['Iteration'], rolling_loss, color='red', label='Loss')
    plt.grid(True)
    plt.xlabel('Iteration')
    plt.ylabel('Reward / Loss')
    plt.title('Training Performance')
    plt.legend()
    plt.savefig(output_path)
    plt.close("all")