import random
from c_service_1 import Service1
from c_service_2 import Service2
from c_service_3 import Service3
from c_system_modelling import get_service_priority
import h_utils as utils
from h_configs import SERVICE1_INPUT_PATH_LIST, SERVICE1_OUTPUT_PATH_LIST, SERVICE1_FOG_ENDPOINT, SERVICE1_CLOUD_ENDPOINT, \
    SERVICE2_INPUT_PATH_LIST, SERVICE2_OUTPUT_PATH_LIST, SERVICE2_FOG_ENDPOINT, SERVICE2_CLOUD_ENDPOINT, \
    SERVICE3_INPUT_PATH_LIST, SERVICE3_OUTPUT_PATH_LIST, SERVICE3_FOG_ENDPOINT, SERVICE3_CLOUD_ENDPOINT, \
    SERVICE_SENSITIVITY, DynamicParams

def generate_service(user, service_id, service_type, input_path_list):
    service_sensitity = random.choice(SERVICE_SENSITIVITY)
    service1 = Service1(
                id = service_id, 
                user = user,
                sensitivity = service_sensitity, 
                slice_count = DynamicParams.get_params()['slice_count'], 
                input_path_list = input_path_list, #[SERVICE1_INPUT_PATH], 
                output_path_list = SERVICE1_OUTPUT_PATH_LIST,
                api_endpoint_list = [SERVICE1_FOG_ENDPOINT, SERVICE1_CLOUD_ENDPOINT]
            )
    service2 = Service2(
                id = service_id, 
                user = user,
                sensitivity = service_sensitity, 
                slice_count = DynamicParams.get_params()['slice_count'], 
                input_path_list = input_path_list, #[SERVICE2_AUDIO_PATH, SERVICE2_SUBTITLE_PATH], 
                output_path_list = SERVICE2_OUTPUT_PATH_LIST,
                api_endpoint_list = [SERVICE2_FOG_ENDPOINT, SERVICE2_CLOUD_ENDPOINT]
            )
    service3 = Service3(
                id = service_id, 
                user = user,
                sensitivity = service_sensitity, 
                slice_count = DynamicParams.get_params()['slice_count'], 
                input_path_list = input_path_list, #[SERVICE3_INPUT_PATH], 
                output_path_list = SERVICE3_OUTPUT_PATH_LIST,
                api_endpoint_list = [SERVICE3_FOG_ENDPOINT, SERVICE3_CLOUD_ENDPOINT]
            )
    services = { 1: service1, 2: service2, 3: service3 }
    service = services[service_type]
    user.services.append(service)

service_id = 0
def generate_services_for_user(user, services_per_user_count):
    global service_id
    for i in range(services_per_user_count):
        service_id += 1
        type = DynamicParams.get_params()['service_type']
        input_path_list = get_input_path_list(type, i)
        generate_service(user, service_id, type, input_path_list)

def generate_services_for_users(users):
    users_count = len(users)
    slices_count = DynamicParams.get_params()['slice_count']
    services_count = DynamicParams.get_params()['service_count']
    services_per_users = get_services_per_users(users_count, services_count)
    user_index = 0
    for services_per_user_count in services_per_users:
        user = users[user_index]
        generate_services_for_user(user, services_per_user_count)
        user_index += 1
    
    # set slice size for each services
    for user in users:
        for service in user.services:
            user_priority = user.get_user_priority()
            service_priority = get_service_priority(users, service)
            slice_sizes = utils.divide_unequal_2(service.get_input_size(), slices_count, user_priority, service_priority)
            service.set_slices_size(slice_sizes)
            service.make_slices()
            if not service.slicable:
                slice_sizes = service.get_slices_size_from_disk()
                service.set_slices_size(slice_sizes)                

def get_services_per_users(users_count, services_count):
    services_per_user = services_count // users_count

    users_with_extra_service = services_count % users_count

    assigned_services = [services_per_user for _ in range(users_count)]

    for i in range(users_with_extra_service):
        assigned_services[i] += 1

    return assigned_services

def get_input_path_list(service_type, i):
    if service_type == 1:
        return [SERVICE1_INPUT_PATH_LIST[i]]
    if service_type == 2:
        return [SERVICE2_INPUT_PATH_LIST[i][0], SERVICE2_INPUT_PATH_LIST[i][1]]
    if service_type == 3:
        return [SERVICE3_INPUT_PATH_LIST[i]]