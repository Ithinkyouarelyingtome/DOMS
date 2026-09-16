from chunker import split_file, calculate_chunk_size,rejoin_chunks
from crypto import compute_hash, encrypt_data, decrypt_data
import json 
from cryptography.fernet import Fernet
import os
import socket
import time
from config import STORAGE_DIR, STORAGE_QUOTA
from transport import send_with_fallback, receive_chunk,try_send,send_chunk,receive_chunk

def send_file_to_network(filepath, devices, chunk_folder="chunks", replication=2):
    session_key = Fernet.generate_key()
    for host, port in devices[:replication]:
        try_send(host, port, b"KEY||" + session_key, timeout=3)

    with open(filepath, 'rb') as f:
        whole_file_data = f.read()
    content_hash = compute_hash(whole_file_data)[:8]
    original_name = os.path.basename(filepath)
    file_id = f"{original_name}_{content_hash}"

    chunk_size = calculate_chunk_size(filepath)
    chunk_paths = split_file(filepath, chunk_size, chunk_folder)
    total_chunks = len(chunk_paths)

    for index, chunk_path in enumerate(chunk_paths):
        with open(chunk_path, 'rb') as f:
            raw_data = f.read()

        chunk_hash = compute_hash(raw_data)
        encrypted_data = encrypt_data(raw_data, session_key)

        metadata = {
            "file_id": file_id,
            "chunk_index": index,
            "total_chunks": total_chunks,
            "chunk_hash": chunk_hash
        }
        combined = json.dumps(metadata).encode() + b"||" + encrypted_data
        successes = send_to_multiple(devices, combined, replication)

        if successes > 0:
            print(f"Sent chunk {index+1}/{total_chunks} to {successes}/{replication} targets")
        else:
            print(f"FAILED to send chunk {index} to any device")

    print(f"File sent as: {file_id}")
    return file_id

def handle_incoming_chunk(conn, storage_manager, session_keys):
    combined = receive_chunk(conn)
    if combined.startswith(b"KEY||"):
        key = combined[5:]
        session_keys['current'] = key
        print("Received session key")
        return True

    key = session_keys.get('current')
    if key is None:
        print("No session key received yet — rejecting chunk")
        return False
    metadata_bytes, encrypted_data = combined.split(b"||", 1)
    metadata = json.loads(metadata_bytes.decode())


    
    data = decrypt_data(encrypted_data, key)
    actual_hash = compute_hash(data)
    
    if actual_hash == metadata["chunk_hash"]:
        chunk_id = f"{metadata['file_id']}_chunk_{metadata['chunk_index']}"
        return storage_manager.save_chunk(chunk_id, data)
    else:
        print("Integrity check failed — chunk rejected")
        return False


def reconstruct_file(file_id, storage_dir, output_path, cache_seconds=3600):
    if os.path.exists(output_path):
        age = time.time() - os.path.getmtime(output_path)
        if age < cache_seconds:
            print(f"Using cached copy of {output_path} (age: {int(age)}s)")
            return output_path

    matching_files = []
    for filename in os.listdir(storage_dir):
        if filename.startswith(f"{file_id}_chunk_"):
            matching_files.append(filename)

    def get_index(filename):
        return int(filename.split("_chunk_")[1])

    matching_files.sort(key=get_index)
    full_paths = [os.path.join(storage_dir, f) for f in matching_files]
    rejoin_chunks(full_paths, output_path)
    print(f"Reconstructed fresh copy: {output_path}")
    return output_path

def send_to_multiple(devices, data, replication_count, timeout=3):
    successes = 0
    for host, port in devices:
        if successes >= replication_count:
            break
        if try_send(host, port, data, timeout):
            successes += 1
    return successes
def handle_chunk_request(conn, storage_dir, file_id):
    # find all chunks matching this file_id in local storage
    matching_files = []
    for filename in os.listdir(storage_dir):
        if filename.startswith(f"{file_id}_chunk_"):
            matching_files.append(filename)
    
    matching_files.sort(key=lambda f: int(f.split("_chunk_")[1]))
    
    # send back how many chunks are coming, then each chunk's raw bytes
    send_chunk(conn, str(len(matching_files)).encode())
    for filename in matching_files:
        with open(os.path.join(storage_dir, filename), 'rb') as f:
            data = f.read()
        send_chunk(conn, data)
def handle_stored_chunk(combined, storage_manager, session_keys):
    key = session_keys.get('current')
    if key is None:
        print("No session key received yet — rejecting chunk")
        return False

    metadata_bytes, encrypted_data = combined.split(b"||", 1)
    metadata = json.loads(metadata_bytes.decode())

    data = decrypt_data(encrypted_data, key)
    actual_hash = compute_hash(data)

    if actual_hash == metadata["chunk_hash"]:
        chunk_id = f"{metadata['file_id']}_chunk_{metadata['chunk_index']}"
        return storage_manager.save_chunk(chunk_id, data)
    else:
        print("Integrity check failed — chunk rejected")
        return False
def retrieve_file_from_network(file_id, devices, output_path, chunk_folder="retrieved_chunks"):
    os.makedirs(chunk_folder, exist_ok=True)
    for host, port in devices:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((host, port))
            send_chunk(sock, b"REQUEST||" + file_id.encode())
            count = int(receive_chunk(sock).decode())
            
            if count == 0:
                print(f"No chunks found for {file_id} on {host}:{port}")
                sock.close()
                continue  # try the next device instead of "succeeding" with nothing

            chunk_paths = []
            for i in range(count):
                data = receive_chunk(sock)
                path = os.path.join(chunk_folder, f"{file_id}_chunk_{i}")
                with open(path, 'wb') as f:
                    f.write(data)
                chunk_paths.append(path)

            sock.close()
            rejoin_chunks(chunk_paths, output_path)
            print(f"Retrieved and reconstructed: {output_path}")
            return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            continue

    print("Could not retrieve file from any device")
    return False
def discover_available_files(devices, timeout=3):
    all_files = set()
    for host, port in devices:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(timeout)
            sock.connect((host, port))
            send_chunk(sock, b"LIST_FILES")
            response = receive_chunk(sock)
            files = json.loads(response.decode())
            all_files.update(files)
        except (ConnectionRefusedError, socket.timeout, OSError) as e:
            print(f"Could not reach {host}:{port} — {e}")
        finally:
            sock.close()
    return list(all_files)
def list_available_files(storage_dir):
    file_ids = set()
    for filename in os.listdir(storage_dir):
        if "_chunk_" in filename:
            file_id = filename.split("_chunk_")[0]
            file_ids.add(file_id)
    return list(file_ids)
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
if __name__ == "__main__":
    file_id = input("Enter the file name to reconstruct (e.g. paper1.pdf): ").strip()
    output_path = input("Enter output filename (e.g. reconstructed.pdf): ").strip()
    reconstruct_file(file_id, "device_storage_6001", output_path)

def delete_file(file_id, storage_dir):
    prefix = f"{file_id}_chunk_"
    matching_files = []
    for filename in os.listdir(storage_dir):
        if filename.startswith(prefix):
            matching_files.append(filename)
    
    if not matching_files:
        print(f"No chunks found for {file_id}")
        return False
    
    freed = 0
    for filename in matching_files:
        full_path = os.path.join(storage_dir, filename)
        freed += os.path.getsize(full_path)
        os.remove(full_path)
    
    print(f"Deleted {len(matching_files)} chunks for {file_id}, freed {freed} bytes")
    return True

def retrieve_and_play(file_id, devices, output_path):
    success = retrieve_file_from_network(file_id, devices, output_path)
    if success:
        print(f"Opening {output_path}...")
        os.startfile(output_path)
        return True
    else:
        print("Could not retrieve file — nothing to play")
        return False