from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import base64
import hashlib


# --- Original functions (still needed) ---
def compute_hash(data):
    return hashlib.sha256(data).hexdigest()

def encrypt_data(data, key):
    f = Fernet(key)
    return f.encrypt(data)

def decrypt_data(encrypted_data, key):
    f = Fernet(key)
    return f.decrypt(encrypted_data)

# Fixed, shared parameters — must be IDENTICAL on both sides. 
# Since generating them fresh each time is slow and they don't need to be secret,
# we generate them ONCE and hardcode the output (not a secret, just shared math).
def generate_dh_parameters():
    return dh.generate_parameters(generator=2, key_size=2048)

def generate_keypair(parameters):
    private_key = parameters.generate_private_key()
    public_key = private_key.public_key()
    return private_key, public_key

def serialize_public_key(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def deserialize_public_key(pem_bytes):
    return serialization.load_pem_public_key(pem_bytes)

def derive_shared_key(private_key, peer_public_key):
    shared_secret = private_key.exchange(peer_public_key)
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'doms_shared_key',
    ).derive(shared_secret)
    # Fernet needs a base64-encoded 32-byte key, so we convert it to match
    return base64.urlsafe_b64encode(derived_key)

def load_dh_parameters(pem_bytes):
    return serialization.load_pem_parameters(pem_bytes)


