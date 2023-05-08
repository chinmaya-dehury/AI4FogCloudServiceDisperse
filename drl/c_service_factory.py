import random
from c_service_1 import Service1
from c_service_2 import Service2
from c_service_3 import Service3
from h_configs import SERVICE1_INPUT_PATH, SERVICE1_OUTPUT_PATH_LIST, SERVICE1_FOG_ENDPOINT, SERVICE1_CLOUD_ENDPOINT, \
    SERVICE2_AUDIO_PATH, SERVICE2_SUBTITLE_PATH, SERVICE2_OUTPUT_PATH_LIST, SERVICE2_FOG_ENDPOINT, SERVICE2_CLOUD_ENDPOINT, \
    SERVICE3_INPUT_PATH, SERVICE3_OUTPUT_PATH_LIST, SERVICE3_FOG_ENDPOINT, SERVICE3_CLOUD_ENDPOINT, \
    SERVICE_SENSITIVITY, SERVICES_TYPES, Params

def generate_service(user, service_id, service_type):
    service_sensitity = random.choice(SERVICE_SENSITIVITY)
    services = {
        1: Service1(
                id = service_id, 
                user = user,
                sensitivity = service_sensitity, 
                slice_count = Params.get_params()['slice_count'], 
                input_path_list = [SERVICE1_INPUT_PATH], 
                output_path_list = SERVICE1_OUTPUT_PATH_LIST,
                api_endpoint_list = [SERVICE1_FOG_ENDPOINT, SERVICE1_CLOUD_ENDPOINT]
            ),
        2: Service2(
                id = service_id, 
                user = user,
                sensitivity = service_sensitity, 
                slice_count = Params.get_params()['slice_count'], 
                input_path_list = [SERVICE2_AUDIO_PATH, SERVICE2_SUBTITLE_PATH], 
                output_path_list = SERVICE2_OUTPUT_PATH_LIST,
                api_endpoint_list = [SERVICE2_FOG_ENDPOINT, SERVICE2_CLOUD_ENDPOINT]
            ),
        3: Service3(
                id = service_id, 
                user = user,
                sensitivity = service_sensitity, 
                slice_count = Params.get_params()['slice_count'], 
                input_path_list = [SERVICE3_INPUT_PATH], 
                output_path_list = SERVICE3_OUTPUT_PATH_LIST,
                api_endpoint_list = [SERVICE3_FOG_ENDPOINT, SERVICE3_CLOUD_ENDPOINT]
            )
    }

    service = services[service_type]
    user.services.append(service)

service_id = 0
def generate_services_for_user(user, services_per_user_count):
    global service_id
    for _ in range(services_per_user_count):
        type = random.choice(SERVICES_TYPES)
        service_id += 1
        generate_service(user, service_id, type)

def generate_services_for_users(users):
    users_count = len(users)
    services_count = Params.get_params()['service_count']
    services_per_users = get_services_per_users(users_count, services_count)
    user_index = 0
    for services_per_user_count in services_per_users:
        user = users[user_index]
        generate_services_for_user(user, services_per_user_count)
        user_index += 1

def get_services_per_users(users_count, services_count):
    services_per_user = services_count // users_count

    users_with_extra_service = services_count % users_count

    assigned_services = [services_per_user for _ in range(users_count)]

    for i in range(users_with_extra_service):
        assigned_services[i] += 1

    return assigned_services