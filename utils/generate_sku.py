import random
import string


def generate_random_sku(prefix, length=8) -> str:
    """
    Generate a random SKU with the specified prefix and length.
    """
    characters = string.ascii_uppercase + string.digits

    random_part = "".join(random.choices(characters, k=length))

    sku = prefix + random_part

    return sku
