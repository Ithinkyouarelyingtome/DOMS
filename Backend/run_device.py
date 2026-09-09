import socket
import sys 
import os
from device import handle_incoming_chunk, send_file_to_network
from storage_manager import Storagemanager
from config import STORAGE_DIR, STORAGE_QUOTA
from cryptography.fernet import Fernet

KEY = b'aPwcPKU4KLJjqFS8tUEsOLETv0sYruEyRg3VSg7kL4E='  

def start_listening(port, key):
    storage = Storagemanager(STORAGE_DIR, STORAGE_QUOTA)
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen(5)
    print(f"Device listening on port {port}...")

    while True:
        conn, addr = server_socket.accept()
        print(f"Incoming connection from {addr}")
        handle_incoming_chunk(conn, storage, key)
        conn.close()
        
if __name__ == "__main__":
    mode = sys.argv[1]  # "listen" or "send"  
    if mode == "listen":
        start_listening(6001, KEY)
    elif mode == "send":
        devices = [("127.0.0.1", 6001)]
        filepath = input("Enter file to send: ").strip()
        send_file_to_network(filepath, devices, KEY)
    
