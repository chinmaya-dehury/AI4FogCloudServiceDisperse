TRAINING_SERVICE_SLICE_PAIRS = {
     '2-2': [2, 2],
    # '2-3': [2, 3],
    # '2-4': [2, 4],
     '3-2': [3, 2],
    # '3-3': [3, 3],
    # '4-2': [4, 2],
    # '4-3': [4, 3],
    # '4-4': [4, 4],
}

class Params:
    __params = None

    @staticmethod
    def set_params(service_count, slice_count):
        Params.__params = {
            'service_count': service_count,
            'slice_count': slice_count,
            'reward_for_last_state_when_all_slices_assigned': 100 * service_count * slice_count,
            'penalty_for_last_state_when_unassigned_slices': -100 * service_count * slice_count,
            'penalty_for_wasted_movements': -1
        }
    @staticmethod
    def get_params():
        return Params.__params

########################################################################################################## GENERAL CONFIGS
ENDPOINT_BASE = "http"
ENDPOINT_METRICS = "api/infos"

STATE_SPACE_FILE = "state_spaces/file_{}_{}.txt"
LOG_FOLDER = "logs"
PLOT_FOLDER = "plots"
MODEL_FOLDER = "models"

LOG_OUTPUT_PATH = '{}/log_{}.txt'

PLOT_LOG_REWARDS_OUTPUT_PATH = '{}/{}_{}_rewards.txt'
PLOT_LOG_LOSSES_OUTPUT_PATH = '{}/{}_{}_losses.txt'
PLOT_LOG_SUCCESS_OUTPUT_PATH = '{}/{}_{}_success_rates.txt'
PLOT_PNG_REWARDS_OUTPUT_PATH = '{}/{}_{}_rewards.png'
PLOT_PNG_LOSSES_OUTPUT_PATH = '{}/{}_{}_losses.png'
PLOT_PNG_TOGETHER_OUTPUT_PATH = '{}/{}_{}_together.png'
PLOT_PNG_SUCCESS_OUTPUT_PATH = '{}/{}_{}_success_rates.png'

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

ENDPOINT_DETECT = "api/sync"

SERVICE1_INPUT_PATH = "input/app1_video.mp4"
SERVICE1_OUTPUT_PATH_LIST = ["output", "app1_output", "mp4"]        # [folder, filename, fileextension]
SERVICE1_FOG_PORT = "5002"                                          # PRODUCTION -> "5002"  |   LOCAL -> ""
SERVICE1_CLOUD_PORT = "5002"                                        # PRODUCTION -> "5002"  |   LOCAL -> ""
SERVICE1_FOG_ENDPOINT = f"{ENDPOINT_BASE}://{FOG_IP}:{SERVICE1_FOG_PORT}/{ENDPOINT_DETECT}"
SERVICE1_CLOUD_ENDPOINT = f"{ENDPOINT_BASE}://{CLOUD_IP}:{SERVICE1_CLOUD_PORT}/{ENDPOINT_DETECT}"

SERVICE2_AUDIO_PATH = "input/app2_audio.mp3"
SERVICE2_SUBTITLE_PATH = "input/app2_subtitle.txt"
SERVICE2_OUTPUT_PATH_LIST = ["output", "app2_output", "srt"]        # [folder, filename, fileextension]
SERVICE2_FOG_PORT = "30001"                                         # PRODUCTION -> "30001"  |   LOCAL -> "32769"
SERVICE2_CLOUD_PORT = "49154"                                       # PRODUCTION -> "49154"  |   LOCAL -> "32769"
SERVICE2_FOG_ENDPOINT = f"{ENDPOINT_BASE}://{FOG_IP}:{SERVICE2_FOG_PORT}/{ENDPOINT_DETECT}"
SERVICE2_CLOUD_ENDPOINT = f"{ENDPOINT_BASE}://{CLOUD_IP}:{SERVICE2_CLOUD_PORT}/{ENDPOINT_DETECT}"

SERVICE3_INPUT_PATH = "input/app3_audio.wav"
SERVICE3_OUTPUT_PATH_LIST = ["output", "app3_output", "txt"]        # [folder, filename, fileextension]
SERVICE3_FOG_PORT = "30002"                                         # PRODUCTION -> "30002"  |   LOCAL -> "32770"
SERVICE3_CLOUD_PORT = "49153"                                       # PRODUCTION -> "49153"  |   LOCAL -> "32770"
SERVICE3_FOG_ENDPOINT = f"{ENDPOINT_BASE}://{FOG_IP}:{SERVICE3_FOG_PORT}/{ENDPOINT_DETECT}"
SERVICE3_CLOUD_ENDPOINT = f"{ENDPOINT_BASE}://{CLOUD_IP}:{SERVICE3_CLOUD_PORT}/{ENDPOINT_DETECT}"



########################################################################################################## DRL CONFIGS
EPISODES = 10_000
AGENT_BATCH_SIZE = 32
AGENT_MAX_MEMORY = 1_000_000
AGENT_LEARNING_RATE = 0.001
AGENT_DISCOUNT_RATE = 0.99
AGENT_EPSILON = 1

########################################################################################################## SIMULATION CONFIGS
# NOTE: It is good approach to test DRL Model in simulation mod before testing it in real environment.
# After getting good results from simulation mod, the agent model only tested in real environment, and adapted to real envrionment.
# The below parameters (except SIMULATION) are assigned using proper APIs from environments.
SIMULATION = False
SMART_GATEWAY_LATITUDE = 59.4055351164239           # LATITUDE
SMART_GATEWAY_LONGITUDE = 24.732632394943135        # LONGITUDE
SMART_GATEWAY_MAX_COMM_RANGE = 1000                 # METER
FOG_CPU_AVAILABLE = [8, 16]
FOG_MEM_AVAILABLE = [20*1024, 50*1024]              # MB
CLOUD_CPU_AVAILABLE = [32, 64]
CLOUD_MEM_AVAILABLE = [50*1024, 100*1024]           # MB
SERVICE_CPU_DEMAND = [1, 4]
SERVICE_MEM_DEMAND = [0.5*1024, 1*1024]             # MB
SERVICE_INPUT_SIZE = [100, 500]                     # MB
LATENCY_BETWEEN_USER_AND_SMARTGATEWAY = [10, 30]    # MS
LATENCY_BETWEEN_SMARTGATEWAY_AND_FOG = [50, 100]    # MS
LATENCY_BETWEEN_SMARTGATEWAY_AND_CLOUD = [150, 200] # MS