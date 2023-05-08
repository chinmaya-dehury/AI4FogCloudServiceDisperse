import os
import ast
import multiprocessing
from h_configs import STATE_SPACE_FILE

def get_state_space_len(num_requests:int, num_slices:int) -> int:
    '''
    Finds the state space length

    @param num_requests - number of service requests
    @param num_slices - number of slices
    '''
    possible_values = [[0, 0], [0, 1], [1, 0]]
    return len(possible_values) ** (num_requests*num_slices) + 1 # + 1 is last state

def get_state_by_action(num_requests:int, num_slices:int, action:int) -> list:
    '''
    Finds the state from disk by action

    @param num_requests - number of service requests
    @param num_slices - number of slices
    @param action - represents action that taken by agent
    '''
    state_space = []
    filename = STATE_SPACE_FILE.format(num_requests, num_slices)
    with open(filename) as file:
        for i, line in enumerate(file):
            if i == action:
                state_space = ast.literal_eval(line)
    return state_space

def verify_state_space_correctness(num_requests:int, num_slices:int) -> bool:
    '''
    Verify the correctness of state space that stored in disk

    @param num_requests - number of service requests
    @param num_slices - number of slices
    '''
    filename = STATE_SPACE_FILE.format(num_requests, num_slices)
    states_by_formula = get_state_space_len(num_requests, num_slices)
    states_in_disk = 0
    filename = STATE_SPACE_FILE.format(num_requests, num_slices)
    with open(filename) as file:
        for _ in file:
            states_in_disk += 1
    return states_by_formula == states_in_disk
    

def generate_state_space(num_requests:int, num_slices:int):
    '''
    Generates the state space

    @param num_requests - number of service requests
    @param num_slices - number of slices
    '''
    possible_values = [[0, 0], [0, 1], [1, 0]]
    memo = {(0,): [[]]} # memoize empty case
    for i in range(1, num_requests*num_slices+1):
        memo[(i,)] = [comb + [value] for value in possible_values for comb in memo[(i-1,)]]
    return memo[(num_requests*num_slices,)]

def save_state_space(num_requests:int, num_slices:int):
    '''
    Saves the state space in disk

    @param num_requests - number of service requests
    @param num_slices - number of slices
    '''
    print(f"State Space for SR={num_requests}, SLICE={num_slices} is started")
    filename = STATE_SPACE_FILE.format(num_requests, num_slices)
    already_generated = os.path.exists(filename) and verify_state_space_correctness(num_requests, num_slices)
    if not already_generated:
        with open(filename, "w") as f:
            combinations = generate_state_space(num_requests, num_slices)
            for combination in combinations:
                f.write(str(combination) + "\n")
    print(f"State Space for SR={num_requests}, SLICE={num_slices} is created. filename={filename}")

def save_state_space_parallelly(num_requests_start:int, num_requests_stop:int, num_requests_step:int, num_slices_start:int, num_slices_stop:int, num_slices_step:int) -> None:
    '''
    Allows to save parallely multiple state space in disk

    @param num_requests_start - starting point for range of number of service requests
    @param num_requests_stop - ending point for range of number of service requests
    @param num_requests_step - step for range of number of service requests
    @param num_slices_start - starting point for range of number of slices
    @param num_slices_stop - ending point for range of number of slices
    @param num_slices_step - step for range of number of slices
    '''
    num_requests_params = range(num_requests_start, num_requests_stop+1, num_requests_step)
    num_slices_params = range(num_slices_start, num_slices_stop+1, num_slices_step)
    pool = multiprocessing.Pool()
    state_space_params = [(num_requests_chunk, num_slices_chunk) for num_requests_chunk in num_requests_params for num_slices_chunk in num_slices_params]
    pool.starmap(save_state_space, state_space_params)
    pool.close()
    pool.join()

if __name__ == '__main__':
    # save_state_space_parallelly(
    #     num_requests_start=2, num_requests_stop=4, num_requests_step=1,     # SRs       = 2, 3, 4
    #     num_slices_start=2, num_slices_stop=4, num_slices_step=1            # Slices    = 2, 3, 4
    # )

    #combination = [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1]]
    # filename = STATE_SPACE_FILE.format(4, 4)
    # with open(filename, "a") as f:
    #         f.write(str(combination) + "\n")
    combination = get_state_by_action(4,4,get_state_space_len(4,4)-1)
    print(combination)