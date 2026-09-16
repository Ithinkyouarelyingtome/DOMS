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
        if not self.can_store(len(data)):
            needed = (self.current_usage() + len(data)) - self.max_bytes
            self.evict_oldest(needed)

        if self.can_store(len(data)):
            full_path = os.path.join(self.storage_dir, chunk_id)
            with open(full_path, 'wb') as f:
                f.write(data)
            return True
        return False
    def evict_oldest(self, needed_bytes):
        files = []
        for filename in os.listdir(self.storage_dir):
            full_path = os.path.join(self.storage_dir, filename)
            files.append((os.path.getmtime(full_path), full_path, os.path.getsize(full_path)))

        files.sort(key=lambda f: f[0])

        freed = 0
        for mtime, path, size in files:
            if freed >= needed_bytes:
                break
            os.remove(path)
            freed += size
            print(f"Evicted {os.path.basename(path)} to free space")

        return freed



manager = Storagemanager("eviction_test", max_bytes=1024)

if __name__ == "__main__":
    manager = Storagemanager("eviction_test", max_bytes=1024)
    print(manager.save_chunk("chunk_a", b"x" * 500))
    print(manager.save_chunk("chunk_b", b"x" * 400))
    print(manager.save_chunk("chunk_c", b"x" * 300))