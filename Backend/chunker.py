import os
import math

         # 200KB per chunk (adjust as you like)
CHUNK_FOLDER = "chunks"  


def split_file(filepath, chunk_size, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    chunk_paths = []
    with open(filepath, 'rb') as f:
        index = 0
        while True:
            data = f.read(chunk_size)   # f.read() remembers position automatically
            if not data:
                break                    # end of file reached
            chunk_path = os.path.join(output_folder, f"chunk_{index}.bin")
            with open(chunk_path, 'wb') as c:
                c.write(data)
            chunk_paths.append(chunk_path)
            index += 1
    return chunk_paths


def choose_file():
    filepath = input("Enter the path of the file you want to split: ").strip()
    while not os.path.exists(filepath):
        print("File not found, try again.")
        filepath = input("Enter the path of the file you want to split: ").strip()
    return filepath




def rejoin_chunks(chunk_paths, output_path):
    with open(output_path, 'wb') as out:
        for chunk_path in chunk_paths:     # ORDER MATTERS
            with open(chunk_path, 'rb') as c:
                out.write(c.read())
                


def calculate_chunk_size(filepath):
    file_size = os.path.getsize(filepath)
    
    tiers = [
        (500 * 1024,          64 * 1024),        # up to 500KB   -> 64KB chunks
        (5 * 1024 * 1024,     200 * 1024),        # up to 5MB     -> 200KB chunks
        (20 * 1024 * 1024,    1 * 1024 * 1024),   # up to 20MB    -> 1MB chunks
        (50 * 1024 * 1024,    2 * 1024 * 1024),   # up to 50MB    -> 2MB chunks
        (100 * 1024 * 1024,   4 * 1024 * 1024),   # up to 100MB   -> 4MB chunks
        (200 * 1024 * 1024,   5 * 1024 * 1024),   # up to 200MB   -> 5MB chunks
        (500 * 1024 * 1024,   10 * 1024 * 1024),  # up to 500MB   -> 10MB chunks
        (1024 * 1024 * 1024,  20 * 1024 * 1024),  # up to 1GB     -> 20MB chunks
    ]
    
    for size_limit, chunk_size in tiers:
        if file_size <= size_limit:
            return chunk_size
    
    return 20 * 1024 * 1024  # fallback for anything bigger than 1GB

if __name__ == "__main__":
    filepath = choose_file()
    chunk_paths = split_file(filepath, calculate_chunk_size(filepath), CHUNK_FOLDER)
    rejoin_chunks(chunk_paths, "rejoined_test.pdf")

