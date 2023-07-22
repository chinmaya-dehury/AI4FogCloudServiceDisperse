from multiprocessing import Pool
from c_env_cloud import Cloud
from c_env_fog import Fog
from c_env_gateway import SmartGateway
from c_slice_info import SliceInfo
from c_system_modelling import get_service_priority
from h_utils import debug
import h_utils_state_space as ssutils
from h_configs import DynamicParams, W1, W2, W3, W4, W5

class Environment:
	def __init__(self, users, w1=None, w2=None, w3=None, w4=None, w5=None):
		self.users = users
		self.services = [service for user in users for service in user.services]
		self.slices_count = DynamicParams.get_params()['slice_count']
		self.services_count = len(self.services)
		self.total_slices = self.services_count * self.slices_count
		self.state_space_len = ssutils.get_state_space_len(self.services_count, self.slices_count)
		self.action_space_len = self.state_space_len
		self.min_reward = 0
		self.max_reward = 0
		self.w1 = W1 if w1 is None else w1 
		self.w2 = W2 if w2 is None else w2 
		self.w3 = W3 if w3 is None else w3
		self.w4 = W4 if w4 is None else w4
		self.w5 = W5 if w5 is None else w5

	def reset(self):
		self.action = None
		self.state = self._get_initial_state()
		self.state_space = self._get_initial_state_space()
		self.slices_tracker = {}
		self.miss_deadline = 0
		self.total_assigned_slices = 0

	def step(self, action):
		reward = 0
		done = False
		selected_slices = []
		next_state_space = self._get_initial_state_space()
		next_state = self._get_next_state(action)
		self.action = action

		# if agent moves other state
		if not self._is_state_last_state(next_state):
			next_state_space[action.index(1)] = 1
			selected_fog_slices, selected_cloud_slices, _ = self._get_selected_slices_by_state(next_state)
			selected_slices = selected_fog_slices + selected_cloud_slices

			if len(selected_slices) > 0:
				# parallel computation:
				with Pool() as pool:
					slice_infos = pool.map(self._assign_slice, selected_slices)
				self._update_slices_tracker(slice_infos)
				reward = self._get_reward_from_slices_tracker(slice_infos)
				reward = round(reward, 3)

				# serial computation:
				# slice_infos = []
				# for selected_slice in selected_slices:
				# 	slice_infos.append(self._assign_slice(selected_slice))
				# self._update_slices_tracker(slice_infos)
				# reward = self._get_reward_from_slices_tracker(slice_infos)
				# reward = round(reward, 3)

		# if agent moves last state
		if self._is_state_last_state(next_state) or self.total_assigned_slices == self.total_slices:
			done = True
			next_state_space = self._get_terminal_state_space()

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
		return reward, done, [self.slices_tracker, self.total_slices, self.total_assigned_slices, self.miss_deadline]

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
		service = selected_slice.service
		user = service.user
		slice_index = selected_slice.slice_index
		assigned_env = selected_slice.assigned_env
		slice_execution_time = service.do_action_with_metrics(slice_index, assigned_env)
		slice_info = self._calculate_slice_reward(user, service, slice_index, assigned_env, slice_execution_time)
		return slice_info

	# calculate reward function
	def _calculate_slice_reward(self, user, service, slice_index, assigned_env, slice_execution_time):
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
		slice_deadline = service.get_deadline_per_slice(slice_index)
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

		w_user_priority = round(self.w1 * user_priority, 3)
		w_service_priority = round(self.w2 * service_priority, 3)
		w_service_sensitivity = round(self.w3 * service_sensitivity, 3)
		w_communication_latency = round(self.w4 * communication_latency, 3)
		w_computation_latency =  round(self.w5 * computation_latency, 3)
		w_latency = w_communication_latency + w_computation_latency

		reward = w_user_priority + w_service_priority + w_service_sensitivity + w_latency

		if slice_execution_time > slice_deadline:
			reward = -reward

		slice_info = SliceInfo(
			service = service,
			service_priority = service_priority,
			slice_index = slice_index,
			assigned_env = assigned_env,
			cpu_demand=slice_cpu_demand,
			mem_demand=slice_mem_demand,
			total_cpu_demand=service.get_cpu_demand(),
			total_mem_demand=service.get_mem_demand(),
			slice_reward=reward
		)

		return slice_info

	# get reward from slices tracker
	def _get_reward_from_slices_tracker(self, slice_infos):
		reward = 0
		for slice_info in slice_infos:
			reward += slice_info.slice_reward
		return reward

	# update reward in slices tracker
	def _update_slices_tracker(self, slice_infos):
		for slice_info in slice_infos:
			self.total_assigned_slices += 1
			if slice_info.slice_reward < 0:
				self.miss_deadline += 1
			slice_info_id = f"{slice_info.service.id}_{slice_info.slice_index}"
			self.slices_tracker[slice_info_id] = slice_info

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
							assigned_env = assigned_env,
							cpu_demand=0,
							mem_demand=0,
							total_cpu_demand=0,
							total_mem_demand=0,
							slice_reward=0
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
		# cloud_slices = self._forward_slices_to_cloud(cloud_slices, skipped_fog_slices)
		selected_cloud_slices, skipped_cloud_slices = self._filter_cloud_slices_by_available_resources(cloud_slices)
		#print(f"selected_cloud_slices = {len(selected_cloud_slices)}")
		#print(f"skipped_cloud_slices = {len(skipped_cloud_slices)}")
		selected_slices = fog_slices + cloud_slices
		skipped_slices = skipped_cloud_slices
		#print(f"total_skipped_slices = {len(skipped_slices)}")
		#print(f"total_selected_slices = {len(selected_slices)}")
		return selected_fog_slices, selected_cloud_slices, skipped_slices
