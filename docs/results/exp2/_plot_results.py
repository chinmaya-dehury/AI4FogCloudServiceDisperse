import os
import ast
import glob
import random
import numpy as np
import matplotlib.pyplot as plt

################################################################################################## FUNCTIONS -> HELPERS
def f_read_plot_dict(file_pattern):
    rdict = {}
    ldict = {}
    matching_files = glob.glob(file_pattern)
    for path in matching_files:
        with open(path) as file_in:
            for line in file_in:
                ldict = ast.literal_eval(line)
                break
        # add to result dict
        for key, value in ldict.items():
            rdict[key] = value
    # sort by key
    rdict = dict(sorted(rdict.items()))
    # convert to array
    rarr = []
    for _, value in rdict.items():
        rarr.append(value)
    return rarr

def f_convert_to_ms(lst):
    n_lst = []
    for i in lst:
        n_lst.append(i*1000)
    return n_lst

def f_get_nth_time(lst, nth_time, collected_time):
    if nth_time == 1:
        return lst
    c = 0
    n_lst = []
    n_lst.append(0) # 0th second datas should be 0
    for i in lst:
        if c == (nth_time/collected_time):
            n_lst.append(i)
            c = 0
        c += 1
    return n_lst

################################################################################################## FUNCTIONS -> PLOTTING CORE
def f_plot(x, y1, y2, y3, title, x_label, y_label, output_path):
    # plotting
    if y1 is not None:
        plt.plot(x, y1, marker='o', color='green', label='Smart Gateway')
    if y2 is not None:
        plt.plot(x, y2, marker='o', color='red', label='Fog')
    if y3 is not None:
        plt.plot(x, y3, marker='o', color='blue', label='Cloud')

    # styling
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.grid(axis='both', linestyle='--', alpha=0.7)
    plt.xlim(0)
    plt.ylim(0)
    plt.xticks(x)

    # save
    plt.savefig(output_path, dpi=300)
    # plt.show()
    plt.close()

def f_plot_new(x, y1, y2, y3, title, x_label, y_label, output_path):
    fig, ax1 = plt.subplots()

    # Plotting y2 and y3 on the left y-axis
    if y2 is not None:
        ax1.plot(x, y2, marker='o', color='red', label='Fog')
    if y3 is not None:
        ax1.plot(x, y3, marker='o', color='blue', label='Cloud')

    ax1.set_xlabel(x_label)
    ax1.set_ylabel(f"{y_label} \n Fog and Cloud")
    ax1.grid(axis='both', linestyle='--', alpha=0.7)
    ax1.set_xlim(0)
    ax1.set_ylim(0)
    ax1.set_xticks(x)

    # Create a twin y-axis for y1
    ax2 = ax1.twinx()

    # Plotting y1 on the right y-axis
    if y1 is not None:
        ax2.plot(x, y1, marker='o', color='green', label='Smart Gateway')
        ax2.set_ylabel("Smart Gateway")
        ax2.tick_params(axis='y')

    # Combine legends from both y-axes
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='lower right')

    plt.title(title)
    plt.savefig(output_path, dpi=300)
    # plt.show()
    plt.close()


def f_plot_bar_2(x, fog_percentages, cloud_percentages, title, x_label, y_label, output_path):
    # datas
    total_percentage = np.arange(len(fog_percentages))
    _, ax = plt.subplots()
    bar_width = 0.35
    plt.title(title)
    ax.bar(total_percentage - bar_width/2, fog_percentages, bar_width, color='skyblue', edgecolor='gray', label='Fog')
    ax.bar(total_percentage + bar_width/2, cloud_percentages, bar_width, color='lightgreen', edgecolor='gray', label='Cloud')
    ax.set_xticks(total_percentage)
    ax.set_xticklabels(x)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.legend()
    plt.grid(axis='both', linestyle='--', alpha=0.7)
    plt.xlim(0)
    plt.ylim(0)
    # plt.xticks(x)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    # plt.show()
    plt.close("all")


################################################################################################## FUNCTIONS -> PLOTTING GENERAL


def plot_throughputs(apptype, nth_time, collected_time = 6):
    y1 = f_read_plot_dict(f"{apptype}*throughputs_smartgateway.txt")
    y2 = f_read_plot_dict(f"{apptype}*throughputs_fog.txt")
    y3 = f_read_plot_dict(f"{apptype}*throughputs_cloud.txt")
    x = list(range(0, (len(y3)*collected_time), nth_time))
    y1 = f_get_nth_time(y1, nth_time, collected_time)
    y2 = f_get_nth_time(y2, nth_time, collected_time)
    y3 = f_get_nth_time(y3, nth_time, collected_time)
    f_plot(x, y1, y2, y3, "Throughputs Metrics", "Streaming Time (seconds)", "Throughputs (total frames per second)", f"app{apptype}_throughputs.png")

def plot_commtimes(apptype, nth_time, collected_time = 6):
    y1 = f_read_plot_dict(f"{apptype}*commtimes_smartgateway.txt")
    y2 = f_read_plot_dict(f"{apptype}*commtimes_fog.txt")
    y3 = f_read_plot_dict(f"{apptype}*commtimes_cloud.txt")
    x = list(range(0, ((len(y3))*collected_time), nth_time))
    y1 = f_convert_to_ms(y1)
    y2 = f_convert_to_ms(y2)
    y3 = f_convert_to_ms(y3)
    y1 = f_get_nth_time(y1, nth_time, collected_time)
    y2 = f_get_nth_time(y2, nth_time, collected_time)
    y3 = f_get_nth_time(y3, nth_time, collected_time)
    f_plot(x, y1, y2, y3, "Communication Time Metrics", "Streaming Time (seconds)", "Communication Time (millisecond)", f"app{apptype}_commtimes.png")

def plot_cpu(apptype, nth_time, collected_time = 6):
    y2 = f_read_plot_dict(f"{apptype}*fog_cpu_percentage.txt")
    y3 = f_read_plot_dict(f"{apptype}*cloud_cpu_percentage.txt")
    x = list(range(0, ((len(y3))*collected_time), nth_time))
    y2 = f_get_nth_time(y2, nth_time, collected_time)
    y3 = f_get_nth_time(y3, nth_time, collected_time)
    f_plot_bar_2(x, y2, y3, "CPU Usage", "Streaming Time (seconds)", "Percentage of CPU Usage", f"app{apptype}_cpus.png")

def plot_mem(apptype, nth_time, collected_time = 6):
    y2 = f_read_plot_dict(f"{apptype}*fog_mem_percentage.txt")
    y3 = f_read_plot_dict(f"{apptype}*cloud_mem_percentage.txt")
    x = list(range(0, ((len(y3))*collected_time), nth_time))
    y2 = f_get_nth_time(y2, nth_time, collected_time)
    y3 = f_get_nth_time(y3, nth_time, collected_time)
    f_plot_bar_2(x, y2, y3, "RAM Usage", "Streaming Time (seconds)", "Percentage of RAM Usage", f"app{apptype}_rams.png")    

if __name__ == '__main__':
    ################################################################################################## APP1
    apptype=1
    nth_time = 6
    plot_throughputs(apptype, nth_time)
    plot_commtimes(apptype, nth_time)
    plot_cpu(apptype, nth_time)
    plot_mem(apptype, nth_time)

    ################################################################################################## APP2
    apptype=2
    plot_throughputs(apptype, nth_time)
    plot_commtimes(apptype, nth_time)
    plot_cpu(apptype, nth_time)
    plot_mem(apptype, nth_time)

    ################################################################################################## APP3
    apptype=3
    plot_throughputs(apptype, nth_time)
    plot_commtimes(apptype, nth_time)
    plot_cpu(apptype, nth_time)
    plot_mem(apptype, nth_time)
