from c_env_cloud import Cloud
from c_env_fog import Fog
from h_utils import debug
from h_configs import DynamicParams

########################################################################################################## USER MODELLING IMPL

# find max user latency from all users
# formula: max(li, 0 < i ≤ n)
def get_max_user_latency(users):
    max_user_latency = 0
    for user in users:
        user_latency = user.get_user_latency()
        max_user_latency = max(max_user_latency, user_latency)
    return max_user_latency

# find latency priority of user ui
# formula: Pli(user latency priority) = li (latency of user ui) / max(li, 0 < i ≤ n)
def get_user_latency_priority(user, max_user_latency):
    if max_user_latency == 0:
        return 0.1
    latency_priority = user.get_user_latency() / max_user_latency
    latency_priority = round(latency_priority, 3)
    return latency_priority

# set user priority for each user. 
# formula: Pi(user priority) = Pdi(user distance priority) + Pli(user latency priority)
def set_users_priorities(users):
    max_user_latency = get_max_user_latency(users)
    for user in users:
        user_latency_priority = get_user_latency_priority(user, max_user_latency)
        user_distance_priority = user.get_distance_priority()
        user_priority = user_latency_priority + user_distance_priority
        user_priority = round (user_priority, 3)
        user.set_user_priority(user_priority)


########################################################################################################## SERVICE MODELLING IMPL

# find service demand of given service sk
# formula: SD(sk) = sum of [ui(ˆsk) * ui(sk)
def get_service_demand(users, service):
    service_demand = 1 # prevent diving by zero
    service_size = service.get_input_size()
    for user in users:
        if(user.is_service_avail(service.type)):
            service_demand += service_size
    return service_demand

# find all services demands
def get_all_service_demands(users):
    all_service_demands = 0.1
    for user in users:
        for service in user.services:
            all_service_demands += get_service_demand(users, service)
    return all_service_demands

# find relative service demand
def get_service_relative_demand(users, service):
    service_demand = get_service_demand(users, service)
    all_service_demands = get_all_service_demands(users)
    relative_demand = round(service_demand/all_service_demands, 3)
    return relative_demand

# find sum of all users priority
def get_sum_of_users_priority(users, service):
    sum = 0
    for user in users:
        if (user.is_service_avail(service.type)):
            user_priority = user.get_user_priority()
            sum += user_priority
    return sum

# find service priority of given service sk
# formula: 0.5 * [Pi · ui(ˆsk)] + 0.5 * relative service demand
def get_service_priority(users, service):
    sum_of_users_priority = get_sum_of_users_priority(users, service)
    service_relative_demand = get_service_relative_demand(users, service)
    service_priority = 0.5 * sum_of_users_priority + 0.5 * service_relative_demand
    service_priority = round(service_priority, 3)
    return service_priority


################################################################################################################## HELPER FUNCTIONS
# helper function for measuring success rate
def get_efficient_times_to_allocate_services(users, services):
    times = 0

    # get slices
    slices = h_split_services_to_slices(services)

    while True:
        # increment step
        times += 1

        # set priorities to slices
        h_set_priorites_to_slices(users, slices)
        if times == 1:
            debug(f"slices count: {len(slices)}")
            #debug(slices)
            debug("\n")


        # sort by priority
        slices = sorted(slices, key=lambda x: x[-1], reverse=True)
        debug(f"{times}. {len(slices)} is sorted by priorities:")
        #debug(slices)
        debug("\n")

        # assign on fog
        debug(f"{times}. Slices are sending to Fog...")
        previous_count = len(slices)
        slices = h_assign_slice(slices, Fog.get_available_cpu(), Fog.get_available_memory(), Fog.get_id())
        current_count = len(slices)
        debug(f"{times}. {previous_count - current_count} slices are sended to Fog. Remaining slices:")
        #debug(slices)
        debug("\n")

        # assign on cloud
        debug(f"{times}. Slices are sending to Cloud...")
        previous_count = len(slices)
        slices = h_assign_slice(slices, Cloud.get_available_cpu(), Cloud.get_available_memory(), Cloud.get_id())
        current_count = len(slices)
        debug(f"{times}. {previous_count - current_count} slices are sended to Cloud. Remaining slices:")
        #debug(slices)
        debug("\n")

        if len(slices) == 0:
            break

    return times

def h_assign_slice(slices, available_cpu, available_mem, assigned_env):
    total_cpu_demand = 0
    total_mem_demand = 0
    slices_copy = slices.copy()
    for j in range(len(slices)):
        slice = slices[j]
        service = slice[0]
        slice_index = slice[1]
        slice_cpu_demand = service.get_cpu_demand_per_slice(slice_index)
        slice_mem_demand = service.get_mem_demand_per_slice(slice_index)
        if total_cpu_demand + slice_cpu_demand <= available_cpu and \
            total_mem_demand + slice_mem_demand <= available_mem:
            slices_copy.pop(0)
            debug(f"\t{service} slice{slice_index} is assigned to {h_convert_to_string(assigned_env)}")
            total_cpu_demand += slice_cpu_demand
            total_mem_demand += slice_mem_demand
            service.do_action_with_metrics(slice_index, assigned_env)
            if service.is_completed():
                debug(f"\t{service} is completed")
                service.user.set_service_avail(service.type, False)
        else:
            break
    return slices_copy

def h_split_services_to_slices(services):
    slices = []
    for service in services:
        priority = 0
        for slice_index in range(DynamicParams.get_params()['slice_count']):
            slice = [service, slice_index, priority]
            slices.append(slice)
    return slices

def h_set_priorites_to_slices(users, slices):
    for i in range(len(slices)):
        slice_infos = slices[i]
        for j in range(len(slice_infos)):
            service = slice_infos[0]
            slices[i][2] = get_service_priority(users, service)

def h_convert_to_string(assigned_env):
    assigned_env_str = "None"
    if assigned_env == Fog.get_id():
        assigned_env_str = "Fog"
    if assigned_env == Cloud.get_id():
        assigned_env_str = "Cloud"
    return assigned_env_str