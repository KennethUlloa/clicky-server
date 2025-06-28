import random
import os
import socket
import string


def generate_random_string(
    length: int = 12, use_digits=True, use_letters=True, use_punctuation=False
) -> str:
    characters = ""
    if use_letters:
        characters += string.ascii_letters  # A-Z + a-z
    if use_digits:
        characters += string.digits  # 0-9
    if use_punctuation:
        characters += string.punctuation  # !@#$%^&*()_+-=[]{}|;:,.<>?/ etc.

    if not characters:
        raise ValueError("At least one character type must be selected")

    return "".join(random.choices(characters, k=length))


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # False connection to retrieve local IP
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def read_cors():
    origins = os.getenv("FLASK_CORS")
    if origins:
        origins = origins.split(",")
        if len(origins) == 1:
            origins = origins[0]

    return origins
