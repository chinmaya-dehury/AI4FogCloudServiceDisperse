from c_user_factory import generate_users
from c_service_factory import generate_service
from h_configs import Params

def test_services():
    Params.set_params(
        service_count = 3,
        slice_count = 3
    )

    users = generate_users(n=1)
    user1 = users[0]

    # generate services for each users
    generate_service(user = user1, service_type=1, service_id=1)
    generate_service(user = user1, service_type=2, service_id=2)
    generate_service(user = user1, service_type=3, service_id=3)

    for service in user1.services:
        _assign_slice(service)

def _assign_slice(service):
    for slice_index in range(3):
        assigned_to_fog = slice_index % 2
        output   = service.do_action_with_metrics(slice_index, assigned_to_fog)

        # logging
        env = "fog" if assigned_to_fog == 1 else "cloud"
        print(f"Service{service.id} slice{slice_index} assigned to {env}. Output = {output}")
    
    service.merge_slices()