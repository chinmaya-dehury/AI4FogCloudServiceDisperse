import numpy as np
from c_env_cloud import Cloud
from c_env_fog import Fog
from c_env_gateway import SmartGateway
from c_slice_info import SliceInfo
from c_system_modelling import get_service_priority
from h_utils import debug
import h_utils_state_space as ssutils
from h_configs import Params, ENVIRONMENT_NAMES, W1, W2, W3, W4, W5

class Environment:
	def __init__(self, users):
		self.users = users
		self.services = [service for user in users for service in user.services]
		self.slices_count = Params.get_params()['slice_count']
		self.services_count = len(self.services)
		self.total_slices = self.services_count * self.slices_count
		self.state_space_len = ssutils.get_state_space_len(self.services_count, self.slices_count)
		self.action_space_len = self.state_space_len

	def reset(self):
		self.state = self._get_initial_state()
		self.state_space = self._get_initial_state_space()
		self.slices_tracker = {}
		self.total_assigned_slices = 0
		# reset environments configuration
		Cloud.reset()
		Fog.reset()
		SmartGateway.reset()

	def step(self, action):
		reward = 0
		done = False
		selected_slices = []
		next_state_space = self._get_initial_state_space()
		next_state = self._get_next_state(action)

		# if agent moves last state
		if self._is_state_last_state(next_state):
			done = True
			reward = Params.get_params()['reward_for_last_state_when_all_slices_assigned']
			# if there are still not assigned slices
			if self.total_slices - self.total_assigned_slices > 0:
				reward = Params.get_params()['penalty_for_last_state_when_unassigned_slices']
		# otherwise, agent moves other state
		else:
			# get selected slices from state
			selected_fog_slices, selected_cloud_slices, _ = self._get_selected_slices_by_state(next_state)
			selected_slices = selected_fog_slices + selected_cloud_slices
			# if no slices selected in new state
			if len(selected_slices) == 0:
				reward = Params.get_params()['penalty_for_wasted_movements']
			# otherwise, calculate reward by selected slices
			else:
				rewards = []
				for selected_slice in selected_slices:
					rewards.append(self._assign_slice(selected_slice))
				reward = np.sum(rewards)
		
		next_state_space[action.index(1)] = 1

		# merge slices of services if all slices are assigned
		if len(selected_slices) > 0:
			for service in self.services:
				if service.is_completed():
					service.user.set_service_avail(service.type, False)
					service.merge_slices()

		# set state
		self._set_state(next_state)
		self._set_state_space(next_state_space)

		# return reward, done, infos
		return reward, done, [self.slices_tracker, self.total_slices, self.total_assigned_slices]

	# get state space
	def get_state_space(self):
		return self.state_space

	# set state space
	def _set_state_space(self, next_state_space):
		self.state_space = next_state_space

	# initial state space
	def _get_initial_state_space(self):
		return [0] * self.state_space_len

	# terminal state space
	def _get_terminal_state_space(self):
		return [1] * self.state_space_len

	# get state
	def get_state(self):
		return self.state

	# set state
	def _set_state(self, next_state):
		self.state = next_state

	# initial state
	def _get_initial_state(self):
		return ssutils.get_state_by_action(num_requests=self.services_count, num_slices=self.slices_count, action = 0)

	# terminal state
	def _get_terminal_state(self):
		return ssutils.get_state_by_action(num_requests=self.services_count, num_slices=self.slices_count, action = self.action_space_len-1)
	
	# next state
	def _get_next_state(self, action):
		# agent can not move from first state to last state
		is_previous_state_first_state = self._is_state_first_state(self.state)
		is_agent_moves_last_state = action[-1] == 1
		if is_previous_state_first_state and is_agent_moves_last_state:
			return self.state.copy()

		# agent can not move from last state to other state
		is_previous_state_last_state = self._is_state_last_state(self.state)
		if is_previous_state_last_state:
			return self.state.copy()

		# agent can move the state
		action = action.index(1)
		return ssutils.get_state_by_action(num_requests=self.services_count, num_slices=self.slices_count, action = action)

	# is first state
	def _is_state_first_state(self, state):
		return all(element == 0 for inner_lst in state for element in inner_lst)

	# is last state
	def _is_state_last_state(self, state):
		return all(element == 1 for inner_lst in state for element in inner_lst)

	# assigning slice to the environment by using action info
	def _assign_slice(self, selected_slice: SliceInfo):
		reward = 0
		service = selected_slice.service
		user = service.user
		slice_index = selected_slice.slice_index
		assigned_env = selected_slice.assigned_env
		service.do_action_with_metrics(slice_index, assigned_env)
		reward = self._calculate_slice_reward(user, service, slice_index, assigned_env)
		return reward

	# calculate reward function
	def _calculate_slice_reward(self, user, service, slice_index, assigned_env):
		reward = 0

		user_priority = user.get_user_priority()
		# we need users to find service prioirty, because we need to know 
		# users priorities, and what user is availing the given service
		# in order to find service priority
		service_priority = get_service_priority(self.users, service)
		service_sensitivity = service.get_sensitivity()
		slice_size = service.get_slice_size(slice_index)
		input_size = service.get_input_size()
		slice_cpu_demand = service.get_cpu_demand_per_slice(slice_index)
		slice_mem_demand = service.get_mem_demand_per_slice(slice_index)
		available_cpu = 0
		available_mem = 0
		environment_latency = 0

		if assigned_env == Fog.get_id():
			available_cpu = Fog.get_available_cpu()
			available_mem = Fog.get_available_memory()
			environment_latency = Fog.get_latency()
		if assigned_env == Cloud.get_id():
			available_cpu = Cloud.get_available_cpu()
			available_mem = Cloud.get_available_memory()
			environment_latency = Cloud.get_latency()

		slice_size_ratio = round(slice_size/input_size, 3)
		cpu_demand_ratio = round(slice_cpu_demand/available_cpu, 3)
		mem_demand_ratio = round(slice_mem_demand/available_mem, 3)
		# user_latency 			-> latency between user and smartgateway
		# environment_latency	-> latency between smartgateway and environment (fog or cloud)
		communication_latency = round(user.get_user_latency()/environment_latency, 3)
		computation_latency = slice_size_ratio + cpu_demand_ratio + mem_demand_ratio

		reward = W1 * user_priority + W2 * service_priority + W3 * service_sensitivity + \
			W4 * communication_latency + W5 * computation_latency
		
		reward = round(reward)

		# update reward in slices tracker
		slice_id = f"{service.id}_{slice_index}"
		slice_info = SliceInfo(
			service = service,
			service_priority = service_priority,
			slice_index = slice_index,
			assigned_env = assigned_env,
			slice_reward=reward
		)
		self.slices_tracker[slice_id] = slice_info
		self.total_assigned_slices += 1

		debug(
			f"\tReward calculation for {service} slice{slice_index} assigned to {ENVIRONMENT_NAMES[assigned_env]}:\n"
			f"\t\tReward = {reward}\n" + \
			f"\t\tuser_priority = {user_priority}, service_priority = {service_priority}, service_sensitivity = {service_sensitivity}\n" + \
			f"\t\tslice_size = {slice_size}, input_size = {input_size}, slice_size_ratio = {slice_size_ratio}\n"
			f"\t\tslice_cpu_demand = {slice_cpu_demand}, available_cpu = {available_cpu}, cpu_demand_ratio = {cpu_demand_ratio}\n"
			f"\t\tslice_mem_demand = {slice_mem_demand}, available_mem = {available_mem}, mem_demand_ratio = {mem_demand_ratio}\n\n",
			is_printable=False
		)

		return reward

	# get environment by slice
	def _get_environment_by_slice(self, slice):
		assigned_env = 0
		if slice[0] == 1:
			assigned_env = Fog.get_id()
		elif slice[1] == 1:
			assigned_env = Cloud.get_id()
		return assigned_env

	# this function converts "binary state vector" to "list of SliceInfo"
	def _convert_state_to_slices(self, state):
		i = 0
		selected_slices = []
		for service in self.services:
			for slice_index in range(self.slices_count):
				slice = state[i]
				slice_id = f"{service.id}_{slice_index}"
				if slice_id not in self.slices_tracker:
					service_priority = get_service_priority(self.users, service)
					assigned_env = self._get_environment_by_slice(slice)
					if assigned_env != 0:
						slice_info = SliceInfo(
							service = service,
							service_priority = service_priority,
							slice_index = slice_index,
							assigned_env = assigned_env
						)
						selected_slices.append(slice_info)
				i += 1
		return selected_slices
	
	# this function splits "list of SliceInfo" by fog and cloud
	def _partition_slices_by_environment(self, all_slices: list[SliceInfo]):
		fog_slices = []
		cloud_slices = []
		for slice in all_slices:
			if slice.assigned_env == Fog.get_id():
				fog_slices.append(slice)
			elif slice.assigned_env == Cloud.get_id():
				cloud_slices.append(slice)
		return fog_slices, cloud_slices

	# this function filters fog slices by available resource in fog
	def _filter_fog_slices_by_available_resources(self, all_fog_slices: list[SliceInfo]):
		selected_slices = []
		skipped_slices = []

		# sort by priority
		all_fog_slices.sort(key=lambda x: x.service_priority, reverse=True)

		# select by resource demand
		total_cpu_demand = 0
		total_mem_demand = 0
		available_cpu = Fog.get_available_cpu()
		available_mem = Fog.get_available_memory()
		for action_info in all_fog_slices:
			slice_cpu_demand = action_info.service.get_cpu_demand_per_slice(action_info.slice_index)
			slice_mem_demand = action_info.service.get_mem_demand_per_slice(action_info.slice_index)
			if total_cpu_demand + slice_cpu_demand <= available_cpu and \
			total_mem_demand + slice_mem_demand <= available_mem:
				selected_slices.append(action_info)
				total_cpu_demand += slice_cpu_demand
				total_mem_demand += slice_mem_demand
			else:
				skipped_slices.append(action_info)
		
		return selected_slices, skipped_slices

	# this function forwards skipped fog slices to cloud
	def _forward_slices_to_cloud(self, cloud_slices: list[SliceInfo], skipped_fog_slices: list[SliceInfo]):
		for skipped_fog_slice in skipped_fog_slices:
			skipped_fog_slice.assigned_env = Cloud.get_id()
			cloud_slices.append(skipped_fog_slice)
		return cloud_slices

	# this function filters cloud slices by available resource in cloud
	def _filter_cloud_slices_by_available_resources(self, all_cloud_slices: list[SliceInfo]):
		selected_slices = []
		skipped_slices = []

		# sort by priority
		all_cloud_slices.sort(key=lambda x: x.service_priority, reverse=True)

		# select by resource demand
		total_cpu_demand = 0
		total_mem_demand = 0
		available_cpu = Cloud.get_available_cpu()
		available_mem = Cloud.get_available_memory()
		for action_info in all_cloud_slices:
			slice_cpu_demand = action_info.service.get_cpu_demand_per_slice(action_info.slice_index)
			slice_mem_demand = action_info.service.get_mem_demand_per_slice(action_info.slice_index)
			if total_cpu_demand + slice_cpu_demand <= available_cpu and \
			total_mem_demand + slice_mem_demand <= available_mem:
				selected_slices.append(action_info)
				total_cpu_demand += slice_cpu_demand
				total_mem_demand += slice_mem_demand
			else:
				skipped_slices.append(action_info)
		
		return selected_slices, skipped_slices

	# this function returns selected slices (or assignable slices)
	def _get_selected_slices_by_state(self, state):
		slice_info_list = self._convert_state_to_slices(state)
		#print(f"slice_info_list = {len(slice_info_list)}")
		fog_slices, cloud_slices = self._partition_slices_by_environment(slice_info_list)
		#print(f"fog_slices = {len(fog_slices)}")
		#print(f"cloud_slices = {len(cloud_slices)}")
		selected_fog_slices, skipped_fog_slices = self._filter_fog_slices_by_available_resources(fog_slices)
		#print(f"selected_fog_slices = {len(selected_fog_slices)}")
		#print(f"skipped_fog_slices = {len(skipped_fog_slices)}")
		cloud_slices = self._forward_slices_to_cloud(cloud_slices, skipped_fog_slices)
		selected_cloud_slices, skipped_cloud_slices = self._filter_cloud_slices_by_available_resources(cloud_slices)
		#print(f"selected_cloud_slices = {len(selected_cloud_slices)}")
		#print(f"skipped_cloud_slices = {len(skipped_cloud_slices)}")
		selected_slices = fog_slices + cloud_slices
		skipped_slices = skipped_cloud_slices
		#print(f"total_skipped_slices = {len(skipped_slices)}")
		#print(f"total_selected_slices = {len(selected_slices)}")
		return selected_fog_slices, selected_cloud_slices, skipped_slices

	# this function adds selected slices (or assignable slices) to slices tracker
	# def _add_selected_slices_to_tracker(self, selected_slices):
	# 	for slice in selected_slices:
	# 		slice_id = f"{slice.service.id}_{slice.slice_index}"
	# 		if slice_id not in self.slices_tracker:
	# 			self.slices_tracker[slice_id] = slice
	# 			self.total_assigned_slices += 1