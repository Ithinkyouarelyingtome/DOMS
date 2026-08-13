import hashlib
from cryptography.fernet import Fernet

def compute_hash(data):
    return hashlib.sha256(data).hexdigest()

def encrypt_data(data, key):
    f = Fernet(key)
    return f.encrypt(data)

def decrypt_data(encrypted_data, key):
    f = Fernet(key)
    return f.decrypt(encrypted_data)




