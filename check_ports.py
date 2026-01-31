import socket
import sys

def check_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('127.0.0.1', port))
        print(f"Port {port} is FREE")
        sock.close()
        return True
    except OSError as e:
        print(f"Port {port} is BUSY: {e}")
        return False

check_port(8000)
check_port(8001)
check_port(8002)
check_port(8003)
check_port(3000)
