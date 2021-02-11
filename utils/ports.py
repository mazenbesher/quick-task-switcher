import socket


def get_open_port() -> int:
    """
    https://stackoverflow.com/a/2838309/1617883
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def is_port_open(port):
    """
    https://stackoverflow.com/a/43271125/1617883
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = False
    try:
        sock.bind(("0.0.0.0", port))
        result = True
    except:
        print("Port is in use")
    sock.close()
    return result
