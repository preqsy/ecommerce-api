import string
import random


def generate_tracking_number(length: int = 10, pre="JS"):
    characters = string.ascii_letters + string.digits
    tracking_number = pre
    for _ in range(length):
        tracking_number += "".join(random.choice(characters))

    return tracking_number
