import time
from drl_training import train
from c_service_testing import test_services
from h_utils import clear_logs
from h_configs import TRAINING_SERVICE_SLICE_PAIRS, Params

if __name__ == '__main__':
    # clear logs
    clear_logs()

    # execute training
    i = 1
    for key, value in TRAINING_SERVICE_SLICE_PAIRS.items():
        service_count = value[0]
        slice_count = value[1]
        Params.set_params(
            service_count = service_count,
            slice_count = slice_count
        )
        print(f"{i}) Training is starting for Services = {service_count} and Slices = {slice_count}")
        time.sleep(5)
        train()
        i += 1

    # execute service testing
    #test_services()

    # print DONE
    print("DONE")