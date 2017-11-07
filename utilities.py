import random

UNAMBIGUOUS_CHARACTERS = "234679ACDEFGHJKMNRTWXYZ"

def create_random_string(length):
    """
    Create random string from a character set.

    """
    string = ''.join(random.choice(UNAMBIGUOUS_CHARACTERS) for _ in range(length))
    return string

