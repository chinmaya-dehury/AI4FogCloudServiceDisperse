import torch
import random
import numpy as np
from collections import deque
from drl_model import DRLModel, DRLTrainer

class Agent:
    def __init__(self, input_layer_size, hidden_layer_size, output_layer_size, epsilon, discount_rate, learning_rate, max_memory, batch_size):
        self.output_layer_size = output_layer_size
        self.batch_size = batch_size
        self.epsilon = epsilon
        self.epsilon_decay = 0.99
        self.min_epsilon = 0.01
        self.memory = deque(maxlen=max_memory)
        self.model = DRLModel(input_layer_size, hidden_layer_size, output_layer_size)
        self.trainer = DRLTrainer(self.model, lr=learning_rate, gamma=discount_rate)
        self.n_iterations = 0

    def get_action(self, state):
        action = [0] * self.output_layer_size
        chosen = None
        if np.random.rand() < self.epsilon:
            prediction = random.randint(0, self.output_layer_size-1)
            chosen = "RANDOMLY"
        else:
            with torch.no_grad():
                state0 = torch.tensor(state, dtype = torch.float)
                prediction = self.model (state0)
                prediction = torch.argmax(prediction).item()
                chosen = "BY AGENT"
        action[prediction] = 1
        self.epsilon = max(self.epsilon * self.epsilon_decay, self.min_epsilon)
        return action, chosen

    def remember(self, state_old, action, reward, done, state_new):
        self.memory.append((state_old, action, reward, done, state_new))

    def train_short_memory(self, state_old, action, reward, done, state_new):
        self.trainer.train(state_old, action, reward, done, state_new)

    def train_long_memory(self):
        if len(self.memory) > self.batch_size:
            mini_sample = random.sample(self.memory, self.batch_size)
        else:
            mini_sample = self.memory
        states_old, actions, rewards, dones, states_new = zip(*mini_sample)
        self.trainer.train(states_old, actions, rewards, dones, states_new)
    
    def get_loss(self):
        return self.trainer.loss