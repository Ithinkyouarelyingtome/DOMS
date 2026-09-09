from chunker import split_file, calculate_chunk_size,rejoin_chunks
from crypto import compute_hash, encrypt_data, decrypt_data
import json 
import os
from config import STORAGE_DIR, STORAGE_QUOTA
from transport import send_with_fallback, receive_chunk

def send_file_to_network(filepath, devices, key, chunk_folder="chunks"):
    chunk_size = calculate_chunk_size(filepath)
    chunk_paths = split_file(filepath, chunk_size, chunk_folder)
    total_chunks = len(chunk_paths)
    file_id = os.path.basename(filepath)

    for index, chunk_path in enumerate(chunk_paths):
        with open(chunk_path, 'rb') as f:
            raw_data = f.read()

        chunk_hash = compute_hash(raw_data)
        encrypted_data = encrypt_data(raw_data, key)

        metadata = {
            "file_id": file_id,
            "chunk_index": index,
            "total_chunks": total_chunks,
            "chunk_hash": chunk_hash
        }
        metadata_bytes = json.dumps(metadata).encode()

        combined = metadata_bytes + b"||" + encrypted_data
        success = send_with_fallback(devices, combined)

        if success:
            print(f"Sent chunk {index+1}/{total_chunks} successfully")
        else:
            print(f"FAILED to send chunk {index} to any device")

def handle_incoming_chunk(conn, storage_manager, key):
    combined = receive_chunk(conn)
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

def reconstruct_file(file_id, storage_dir, output_path):
    matching_files = []
    for filename in os.listdir(storage_dir):
        if filename.startswith(f"{file_id}_chunk_"):
            matching_files.append(filename)

    def get_index(filename):
        return int(filename.split("_chunk_")[1])

    matching_files.sort(key=get_index)

    full_paths = [os.path.join(storage_dir, f) for f in matching_files]
    rejoin_chunks(full_paths, output_path)

    
if __name__ == "__main__":
    file_id = input("Enter the file name to reconstruct (e.g. paper1.pdf): ").strip()
    output_path = input("Enter output filename (e.g. reconstructed.pdf): ").strip()
    reconstruct_file(file_id, STORAGE_DIR, output_path)