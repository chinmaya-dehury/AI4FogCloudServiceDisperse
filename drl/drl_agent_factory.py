from drl_agent import Agent
from h_configs import AGENT_EPSILON, AGENT_DISCOUNT_RATE, AGENT_LEARNING_RATE, AGENT_MAX_MEMORY, AGENT_BATCH_SIZE


def generate_agent(input_layer_size, hidden_layer_size, output_layer_size, alpha = None, gamma = None):
    agent = Agent(
        input_layer_size = input_layer_size, 
        hidden_layer_size = hidden_layer_size, 
        output_layer_size = output_layer_size, 
        epsilon = AGENT_EPSILON, 
        discount_rate = AGENT_DISCOUNT_RATE if gamma == None else gamma, 
        learning_rate = AGENT_LEARNING_RATE if alpha == None else alpha, 
        max_memory = AGENT_MAX_MEMORY, 
        batch_size = AGENT_BATCH_SIZE
    )
    return agent