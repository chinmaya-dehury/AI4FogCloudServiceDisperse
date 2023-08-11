import ast
import numpy as np
import matplotlib.pyplot as plt

def f_read_plot_list(path):
    ls = []
    with open(path) as file_in:
        for line in file_in:
            ls = ast.literal_eval(line)
            break
    return ls

def f_plot(y1, y2, y3, x_label, y_label, file_path):
    # datas
    x = np.arange(1, 11, 1)

    # plotting
    if y1 is not None:
        plt.plot(x, y1, marker='o', color='green', label='Application 1')
    if y2 is not None:
        plt.plot(x, y2, marker='o', color='red', label='Application 2')
    if y3 is not None:
        plt.plot(x, y3, marker='o', color='blue', label='Application 3')

    # styling
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.grid(axis='both', linestyle='--', alpha=0.7)
    plt.ylim(0)
    plt.xticks(np.arange(1, 11, 1))

    # save
    plt.savefig(file_path)
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
    plt.show()
    plt.close("all")

if __name__ == '__main__':
    main_folder = "."
    ################################################################################################## LOSSESS
    # y1 = f_read_plot_list(f"{main_folder}/1_6_losses.txt")
    # y2 = f_read_plot_list(f"{main_folder}/2_6_losses.txt")
    # y3 = f_read_plot_list(f"{main_folder}/3_6_losses.txt")
    # f_plot(y1, y2, y3, "Episodes (thousands)", "Losses", f"{main_folder}/all_losses.png")

    ################################################################################################## REWARDS
    # y1 = f_read_plot_list(f"{main_folder}/1_6_rewards.txt")
    # y2 = f_read_plot_list(f"{main_folder}/2_6_rewards.txt")
    # y3 = f_read_plot_list(f"{main_folder}/3_6_rewards.txt")
    # f_plot(y1, y2, y3, "Episodes (thousands)", "Cum Avg Rewards", f"{main_folder}/all_rewards.png")

    ################################################################################################## SUCCESS
    y1 = f_read_plot_list(f"{main_folder}/1_6_success_rates.txt")
    y2 = f_read_plot_list(f"{main_folder}/2_6_success_rates.txt")
    y3 = f_read_plot_list(f"{main_folder}/3_6_success_rates.txt")
    f_plot(y1, y2, y3, "Episodes (thousands)", "Success Rates", f"{main_folder}/all_success_rates.png")

    ################################################################################################## DEADLINES
    y1 = f_read_plot_list(f"{main_folder}/1_6_missed_deadlines.txt")
    y2 = f_read_plot_list(f"{main_folder}/2_6_missed_deadlines.txt")
    y3 = f_read_plot_list(f"{main_folder}/3_6_missed_deadlines.txt")
    f_plot(y1, y2, y3, "Episodes (thousands)", "Percentage of Missed Deadlines", f"{main_folder}/all_deadlines.png")

    ################################################################################################## SLICES
    fog_percentages = f_read_plot_list(f"{main_folder}/1_6_fog_percentage.txt")
    cloud_percentages = f_read_plot_list(f"{main_folder}/1_6_cloud_percentage.txt")
    x = list(range(0, (len(fog_percentages)+1), 1))
    fog_percentages = [0] + fog_percentages
    cloud_percentages = [0] + cloud_percentages
    f_plot_bar_2(x, fog_percentages, cloud_percentages, "Application 1", "Episodes (thousands)", "Percentage of Slices", f"{main_folder}/app1_slices.png")

    fog_percentages = f_read_plot_list(f"{main_folder}/2_6_fog_percentage.txt")
    cloud_percentages = f_read_plot_list(f"{main_folder}/2_6_cloud_percentage.txt")
    fog_percentages = [0] + fog_percentages
    cloud_percentages = [0] + cloud_percentages
    f_plot_bar_2(x, fog_percentages, cloud_percentages, "Application 2", "Episodes (thousands)", "Percentage of Slices", f"{main_folder}/app2_slices.png")

    fog_percentages = f_read_plot_list(f"{main_folder}/3_6_fog_percentage.txt")
    cloud_percentages = f_read_plot_list(f"{main_folder}/3_6_cloud_percentage.txt")
    fog_percentages = [0] + fog_percentages
    cloud_percentages = [0] + cloud_percentages
    f_plot_bar_2(x, fog_percentages, cloud_percentages, "Application 3", "Episodes (thousands)", "Percentage of Slices", f"{main_folder}/app3_slices.png")
