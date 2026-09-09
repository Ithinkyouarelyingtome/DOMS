from flask import Flask, jsonify
from Backend.storage_manager import Storagemanager
from Backend.config import STORAGE_DIR, STORAGE_QUOTA

app = Flask(__name__)

@app.route('/')
def home():
    return 'DOMS Web UI is running'