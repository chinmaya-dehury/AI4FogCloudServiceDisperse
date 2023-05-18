import time
from drl_training import train_main
from c_service_testing import test_services
from h_utils import clear_logs
from h_configs import TRAINING_SERVICE_SLICE_PAIRS, Params

if __name__ == '__main__':
    # clear logs
    clear_logs()

    # execute training
    train_main()

    # execute service testing
    #test_services()

    # print DONE
    print("DONE")