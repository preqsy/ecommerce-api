import random

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]


def generate_otp() -> str:
    otp = ""
    for i in range(6):
        otp += str(random.choice(numbers))
    return otp
