from chunker import split_file, calculate_chunk_size
from crypto import compute_hash, encrypt_data
from transport import send_with_fallback

def send_file_to_network(filepath, devices, key, chunk_folder="chunks"):
    chunk_size = calculate_chunk_size(filepath)
    chunk_paths = split_file(filepath, chunk_size, chunk_folder)

    for chunk_path in chunk_paths:
        with open(chunk_path, 'rb') as f:
            raw_data = f.read()

        chunk_hash = compute_hash(raw_data)
        encrypted_data = encrypt_data(raw_data, key)

        success = send_with_fallback(devices, chunk_hash.encode())
        if success:
            success = send_with_fallback(devices, encrypted_data)

        if success:
            print(f"Sent {chunk_path} successfully")
        else:
            print(f"FAILED to send {chunk_path} to any device")

def handle_incoming_chunk(conn, storage_manager, key):
    expected_hash = receive_chunk(conn).decode()
    encrypted_data = receive_chunk(conn)
    
    data = decrypt_data(encrypted_data, key)
    actual_hash = compute_hash(data)
    
    if actual_hash == expected_hash:
        chunk_id = f"chunk_{actual_hash[:8]}"  # short id based on hash
        return storage_manager.save_chunk(chunk_id, data)
    else:
        print("Integrity check failed — chunk rejected")
        return False