import socket
import sys
import json
import threading
import os
from discovery import broadcast_presence, listen_for_devices
from chunker import rejoin_chunks
from config import STORAGE_DIR, STORAGE_QUOTA, KNOWN_DEVICES
from storage_manager import Storagemanager
from cryptography.fernet import Fernet
from transport import send_with_fallback, receive_chunk, try_send, send_chunk
from device import (
    send_file_to_network, handle_chunk_request, handle_stored_chunk,
    retrieve_file_from_network, list_available_files, discover_available_files,
    handle_quick_share, quick_send,delete_file,retrieve_and_play
)
import subprocess


QUICKSHARE_PORT = 7000


def start_listening(port):
    storage_dir = f"device_storage_{port}"
    storage = Storagemanager(storage_dir, STORAGE_QUOTA)
    session_keys = {}

    broadcast_thread = threading.Thread(target=broadcast_presence, args=(port,), daemon=True)
    broadcast_thread.start()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    print(f"Device listening on port {port}...")

    while True:
        conn, addr = server_socket.accept()
        print(f"Incoming connection from {addr}")

        first_message = receive_chunk(conn)

        if first_message == b"LIST_FILES":
            files = list_available_files(storage_dir)
            response = json.dumps(files).encode()
            send_chunk(conn, response)
        elif first_message.startswith(b"REQUEST||"):
            file_id = first_message[9:].decode()
            print(f"Chunk request for: {file_id}")
            handle_chunk_request(conn, storage_dir, file_id)
        elif first_message.startswith(b"KEY||"):
            session_keys['current'] = first_message[5:]
            print("Received session key")
        else:
            handle_stored_chunk(first_message, storage, session_keys)
        conn.close()

def start_quickshare_listening():
    broadcast_thread = threading.Thread(target=broadcast_presence, args=(QUICKSHARE_PORT,), daemon=True)
    broadcast_thread.start()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', QUICKSHARE_PORT))
    server_socket.listen(5)
    print(f"Quick Share listening on port {QUICKSHARE_PORT}...")

    while True:
        conn, addr = server_socket.accept()
        print(f"Quick Share connection from {addr}")
        handle_quick_share(conn)
        conn.close()


if __name__ == "__main__":
    mode = sys.argv[1]

    if mode == "listen":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 6001
        start_listening(port)

    elif mode == "send":
        print("Discovering devices...")
        devices = listen_for_devices([], timeout=5)
        if not devices:
            print("No devices found, falling back to known list")
            devices = KNOWN_DEVICES

        filepath = input("Enter file to send: ").strip()
        file_id = send_file_to_network(filepath, devices)
        print(f"Remember this ID to retrieve it later: {file_id}")

    elif mode == "list":
        print("Discovering devices...")
        devices = listen_for_devices([], timeout=5)
        if not devices:
            devices = KNOWN_DEVICES
        files = discover_available_files(devices)
        print("Files available across the mesh:", files)

    elif mode == "retrieve":
        print("Discovering devices...")
        devices = listen_for_devices([], timeout=5)
        if not devices:
            devices = KNOWN_DEVICES

        file_id = input("Enter file_id to retrieve (e.g. paper1.pdf): ").strip()
        output_path = input("Enter output filename: ").strip()
        retrieve_file_from_network(file_id, devices, output_path)

    elif mode == "quickshare-listen":
        start_quickshare_listening()

    elif mode == "quickshare-send":
        print("Discovering nearby devices...")
        devices = listen_for_devices([], timeout=5)
        
        if not devices:
            print("No devices found.")
        else:
            print("Available devices:")
            for i, (host, port) in enumerate(devices):
                print(f"  {i+1}. {host}:{port}")
            
            choice = int(input("Choose a device number: ")) - 1
            host, _ = devices[choice]
            
            filepath = input("Enter file to send: ").strip()
            quick_send(filepath, host, QUICKSHARE_PORT)
    elif mode == "play":
        print("Discovering devices...")
        devices = listen_for_devices([], timeout=5)
        if not devices:
            devices = KNOWN_DEVICES

        file_id = input("Enter file_id to play (e.g. paper1.pdf_02d5a3af): ").strip()
        output_path = input("Enter temp filename to save as: ").strip()
        retrieve_and_play(file_id, devices, output_path)
    elif mode == "delete":
        file_id = input("Enter file_id to delete from THIS device's local storage: ").strip()
        port = int(input("Enter this device's port (e.g. 6001): ").strip())
        storage_dir = f"device_storage_{port}"
        delete_file(file_id, storage_dir)