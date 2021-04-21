import socket
from sys import platform

def emojis(str=''):
    # Return platform-dependent emoji-safe version of string
    return str.encode().decode('ascii', 'ignore') if platform.system() == 'Windows' else str


def valid_address(netloc):
    try:
        socket.gethostbyname(netloc)
        return True
    except:
        return False
