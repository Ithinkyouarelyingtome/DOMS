import socket

def send_chunk(sock, data):
    size = len(data)
    sock.sendall(str(size).encode().ljust(16))
    sock.sendall(data)

def receive_chunk(sock):
    size_header = sock.recv(16).decode().strip()
    size = int(size_header)
    received = b""
    while len(received) < size:
        chunk = sock.recv(4096)
        if not chunk:
            break
        received += chunk
    return received

def try_send(host, port, data, timeout):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.settimeout(timeout)
        sock.connect((host, port))
        send_chunk(sock, data)
        return True
    except (ConnectionRefusedError, socket.timeout, OSError) as e:
        print(f"Failed to reach {host}:{port} — {e}")
        return False
    finally:
        sock.close()

def send_with_fallback(devices, data, timeout=3):
    for host, port in devices:
        if try_send(host, port, data, timeout):
            return True
    return False