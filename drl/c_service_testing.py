from c_user_factory import generate_users
from c_service_factory import generate_services_for_users
from h_configs import DynamicParams, TRAINING_SERVICE_SLICE_PAIRS

def test_services():
    for _, value in TRAINING_SERVICE_SLICE_PAIRS.items():
        service_type = value[0]
        service_count = value[1]
        slice_count = value[2]
        DynamicParams.set_params(
            service_type = service_type,
            service_count = service_count,
            slice_count = slice_count
        )
        users = generate_users(n=1)
        generate_services_for_users(users)
        
        for user in users:
            for service in user.services:
                total_size = service.get_input_size()
                sum_of_slices = sum(service.slices_size_map.values())
                if (sum_of_slices > total_size):
                    print(f"ERROR: Service{service.id} -> {service.slices_size_map}")
                else:
                    print(f"Service{service.id} -> {service.slices_size_map}")

test_services()