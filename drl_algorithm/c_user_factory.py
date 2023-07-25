import random
from c_user import User
from h_configs import USERS_LOCATIONS

def generate_users(n):
    users = []

    for i in range(n):
        id = (i+1)
        location = random.choice(USERS_LOCATIONS)
        user = User(id = id, latitude = location[0], longitude = location[1])
        users.append(user)

    return users