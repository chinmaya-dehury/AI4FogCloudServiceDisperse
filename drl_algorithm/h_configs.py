TRAINING_SERVICE_SLICE_PAIRS = {
    'app1-sr-slice': [1, 1, 2],
    # 'app2-sr-slice': [2, 3, 2],
    # 'app3-sr-slice': [3, 3, 2],
}

class DynamicParams:
    __params = None

    @staticmethod
    def set_params(service_type, service_count, slice_count):
        DynamicParams.__params = {
            'service_type': service_type,
            'service_count': service_count,
            'slice_count': slice_count
        }
    @staticmethod
    def get_params():
        return DynamicParams.__params

########################################################################################################## GENERAL CONFIGS
ENDPOINT_BASE = "http"
ENDPOINT_METRICS = "api/infos"

STATE_SPACE_FILE = "state_spaces/file_{}.txt"
LOG_FOLDER = "logs"
PLOT_FOLDER = "plots"
MODEL_FOLDER = "models"

LOG_OUTPUT_PATH = '{}/log_{}.txt'

PLOT_LOG_REWARDS_OUTPUT_PATH = '{}/{}_{}_rewards.txt'
PLOT_LOG_LOSSES_OUTPUT_PATH = '{}/{}_{}_losses.txt'
PLOT_LOG_SUCCESS_OUTPUT_PATH = '{}/{}_{}_success_rates.txt'
PLOT_LOG_FOG_PERCENTAGE_OUTPUT_PATH = '{}/{}_{}_fog_percentage.txt'
PLOT_LOG_CLOUD_PERCENTAGE_OUTPUT_PATH = '{}/{}_{}_cloud_percentage.txt'
PLOT_LOG_FOG_CPU_PERCENTAGE_OUTPUT_PATH = '{}/{}_{}_fog_cpu_percentage.txt'
PLOT_LOG_CLOUD_CPU_PERCENTAGE_OUTPUT_PATH = '{}/{}_{}_cloud_cpu_percentage.txt'
PLOT_LOG_FOG_MEM_PERCENTAGE_OUTPUT_PATH = '{}/{}_{}_fog_mem_percentage.txt'
PLOT_LOG_CLOUD_MEM_PERCENTAGE_OUTPUT_PATH = '{}/{}_{}_cloud_mem_percentage.txt'
PLOT_LOG_MISSED_DEADLINES_OUTPUT_PATH = '{}/{}_{}_missed_deadlines.txt'
PLOT_PNG_REWARDS_OUTPUT_PATH = '{}/{}_{}_rewards.png'
PLOT_PNG_LOSSES_OUTPUT_PATH = '{}/{}_{}_losses.png'
PLOT_PNG_TOGETHER_OUTPUT_PATH = '{}/{}_{}_together.png'
PLOT_PNG_SUCCESS_OUTPUT_PATH = '{}/{}_{}_success_rates.png'
PLOT_PNG_FOG_PERCENTAGE_OUTPUT_PATH = '{}/{}_{}_fog_percentage.png'
PLOT_PNG_CLOUD_PERCENTAGE_OUTPUT_PATH = '{}/{}_{}_cloud_percentage.png'
PLOT_PNG_SLICES_PERCENTAGE_OUTPUT_PATH = '{}/{}_{}_slices_percentage.png'
PLOT_PNG_CPU_PERCENTAGE_OUTPUT_PATH = '{}/{}_{}_cpu_demand.png'
PLOT_PNG_MEM_PERCENTAGE_OUTPUT_PATH = '{}/{}_{}_mem_demand.png'
PLOT_PNG_MISSED_DEADLINES_OUTPUT_PATH = '{}/{}_{}_missed_deadlines.png'

MODEL_OUTPUT_PATH = '{}/model_{}_{}_{}.pth'

########################################################################################################## USER CONFIGS
USERS_LOCATIONS = [
    [59.40430390828478, 24.730219100475903],
    [59.40529225202108, 24.730186911484836],
    [59.404811718560545, 24.734435530282703],
    [59.404795336617866, 24.731817694457753],
    [59.40429841392595, 24.731238337348955]
]

########################################################################################################## SMART GATEWAY CONFIGS
SMART_GATEWAY_IP = '192.168.8.102'
SMART_GATEWAY_PORT = '5000'
SMART_GATEWAY_METRICS_ENDPOINT = f"{ENDPOINT_BASE}://{SMART_GATEWAY_IP}:{SMART_GATEWAY_PORT}/{ENDPOINT_METRICS}"
                                                                                            # 192.168.8.102:5000/api/infos

########################################################################################################## FOG/CLOUD CONFIGS
ENVIRONMENT_COUNT = 2       # represents that there are 2 environments value: fog(=1) and cloud(2)
ENVIRONMENT_NAMES = {1: "Fog", 2: "Cloud"}
FOG_ID = 1
FOG_IP = "172.17.142.22"    # PRODUCTION -> "172.17.142.22" | LOCAL -> "127.0.0.1"
FOG_PORT = "5000"
FOG_METRICS_ENDPOINT = f"{ENDPOINT_BASE}://{FOG_IP}:{FOG_PORT}/{ENDPOINT_METRICS}"          # 172.17.142.22:5000/api/infos

CLOUD_ID = 2
CLOUD_IP = "172.17.90.194"  # PRODUCTION -> "172.17.90.194" | LOCAL -> "127.0.0.1"
CLOUD_PORT = "5000"
CLOUD_METRICS_ENDPOINT = f"{ENDPOINT_BASE}://{CLOUD_IP}:{CLOUD_PORT}/{ENDPOINT_METRICS}"    # 172.17.90.194:5000/api/infos

########################################################################################################## SERVICE CONFIGS
SERVICES_TYPES = [1, 2, 3]
SERVICE_SENSITIVITY = [1, 5]
DEADLINE_FOR_1_FRAME_VIDEO = 1000    # MS
DEADLINE_FOR_1_SEGMENT_AUDIO = 500  # MS

ENDPOINT_DETECT = "api/sync"

SERVICE1_INPUT_PATH_LIST = [
    "input/app1_sr1/app1_sr1.mp4", 
    "input/app1_sr2/app1_sr2.mp4", 
    "input/app1_sr3/app1_sr3.mp4", 
]
SERVICE1_OUTPUT_PATH_LIST = ["output", "app1_output", "mp4"]        # [folder, filename, fileextension]
SERVICE1_FOG_PORT = "5002"                                          # PRODUCTION -> "5002"  |   LOCAL -> ""
SERVICE1_CLOUD_PORT = "5002"                                        # PRODUCTION -> "5002"  |   LOCAL -> ""
SERVICE1_FOG_ENDPOINT = f"{ENDPOINT_BASE}://{FOG_IP}:{SERVICE1_FOG_PORT}/{ENDPOINT_DETECT}"
SERVICE1_CLOUD_ENDPOINT = f"{ENDPOINT_BASE}://{CLOUD_IP}:{SERVICE1_CLOUD_PORT}/{ENDPOINT_DETECT}"

SERVICE2_INPUT_PATH_LIST = [
    ["input/app2_sr1/app2_sr1.mp3", "input/app2_sr1/app2_sr1.txt"],
    ["input/app2_sr2/app2_sr2.mp3", "input/app2_sr2/app2_sr2.txt"],
    ["input/app2_sr3/app2_sr3.mp3", "input/app2_sr3/app2_sr3.txt"],
]
SERVICE2_OUTPUT_PATH_LIST = ["output", "app2_output", "srt"]        # [folder, filename, fileextension]
SERVICE2_FOG_PORT = "30001"                                         # PRODUCTION -> "30001"  |   LOCAL -> "32769"
SERVICE2_CLOUD_PORT = "49154"                                       # PRODUCTION -> "49154"  |   LOCAL -> "32769"
SERVICE2_FOG_ENDPOINT = f"{ENDPOINT_BASE}://{FOG_IP}:{SERVICE2_FOG_PORT}/{ENDPOINT_DETECT}"
SERVICE2_CLOUD_ENDPOINT = f"{ENDPOINT_BASE}://{CLOUD_IP}:{SERVICE2_CLOUD_PORT}/{ENDPOINT_DETECT}"

SERVICE3_INPUT_PATH_LIST = [
    "input/app3_sr1/app3_sr1.wav", 
    "input/app3_sr2/app3_sr2.wav", 
    "input/app3_sr3/app3_sr3.wav", 
]
SERVICE3_OUTPUT_PATH_LIST = ["output", "app3_output", "txt"]        # [folder, filename, fileextension]
SERVICE3_FOG_PORT = "30002"                                         # PRODUCTION -> "30002"  |   LOCAL -> "32770"
SERVICE3_CLOUD_PORT = "49153"                                       # PRODUCTION -> "49153"  |   LOCAL -> "32770"
SERVICE3_FOG_ENDPOINT = f"{ENDPOINT_BASE}://{FOG_IP}:{SERVICE3_FOG_PORT}/{ENDPOINT_DETECT}"
SERVICE3_CLOUD_ENDPOINT = f"{ENDPOINT_BASE}://{CLOUD_IP}:{SERVICE3_CLOUD_PORT}/{ENDPOINT_DETECT}"



########################################################################################################## DRL CONFIGS
EPISODES = 10_000
AGENT_BATCH_SIZE = 64
AGENT_MAX_MEMORY = 5_000
AGENT_LEARNING_RATE = 0.001
AGENT_DISCOUNT_RATE = 0.99
AGENT_EPSILON = 1
W1 = 0.2
W2 = 0.2
W3 = 0.2
W4 = 0.2
W5 = 0.2
