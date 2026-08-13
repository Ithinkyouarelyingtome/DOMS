import os

class Storagemanager:
    def __init__(self, storage_dir, max_bytes):
        self.storage_dir = storage_dir
        self.max_bytes = max_bytes
        os.makedirs(storage_dir, exist_ok=True)


    def current_usage(self):
        total = 0
        for filename in os.listdir(self.storage_dir):
            full_path = os.path.join(self.storage_dir, filename)
            total += os.path.getsize(full_path)
        return total


    def can_store(self, chunk_size):
        return self.current_usage() + chunk_size <= self.max_bytes
    
    def save_chunk(self, chunk_id, data):
        if self.can_store(len(data)):
            full_path = os.path.join(self.storage_dir, chunk_id)
            with open(full_path, 'wb') as f:
                f.write(data)
                return True
        return False
