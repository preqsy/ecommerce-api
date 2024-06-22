import string
import random


def generate_random_id(length: int = 10, prefix="TKN"):
    characters = string.ascii_letters + string.digits
    tracking_number = prefix[0:3]
    for _ in range(length):
        tracking_number += "".join(random.choice(characters))

    return tracking_number
