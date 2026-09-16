import socket
import os
import json 
from cryptography.fernet import Fernet
from crypto import compute_hash, encrypt_data , decrypt_data

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

def try_send(host, port, data, timeout=3):
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

def quick_send(filepath, host, port):
    session_key = Fernet.generate_key()
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    
    send_chunk(sock, session_key)
    
    with open(filepath, 'rb') as f:
        raw_data = f.read()
    
    filename = os.path.basename(filepath)
    file_hash = compute_hash(raw_data)
    encrypted_data = encrypt_data(raw_data, session_key)
    
    metadata = {"filename": filename, "file_hash": file_hash}
    combined = json.dumps(metadata).encode() + b"||" + encrypted_data
    
    send_chunk(sock, combined)
    sock.close()
    print(f"Quick-sent {filename} to {host}:{port}")

def handle_quick_share(conn, save_dir="quickshare_received"):
    os.makedirs(save_dir, exist_ok=True)
    
    session_key = receive_chunk(conn)
    combined = receive_chunk(conn)
    
    metadata_bytes, encrypted_data = combined.split(b"||", 1)
    metadata = json.loads(metadata_bytes.decode())
    
    data = decrypt_data(encrypted_data, session_key)
    actual_hash = compute_hash(data)
    
    if actual_hash == metadata["file_hash"]:
        save_path = os.path.join(save_dir, metadata["filename"])
        with open(save_path, 'wb') as f:
            f.write(data)
        print(f"Quick-received: {save_path}")
        return True
    else:
        print("Quick Share integrity check failed — rejected")
        return False