from flask import Flask, render_template
import sys
import os

# Add the Backend folder to the import path (sibling folder to webui/)
BACKEND_PATH = r'C:\Users\sdaks\Desktop\DOMS\Backend'
sys.path.append(BACKEND_PATH)

from device import list_available_files
from config import STORAGE_DIR, STORAGE_QUOTA, KNOWN_DEVICES
from storage_manager import Storagemanager
from discovery import listen_for_devices

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html", active_page="home")


@app.route("/storage")
def storage():
    storage_dir = "device_storage_6001"

    try:
        manager = Storagemanager(storage_dir, STORAGE_QUOTA)
        used_bytes = manager.current_usage()
        used_mb = round(used_bytes / (1024 * 1024), 1)
        quota_mb = round(STORAGE_QUOTA / (1024 * 1024), 1)
        percent_used = round((used_bytes / STORAGE_QUOTA) * 100) if STORAGE_QUOTA else 0
    except Exception as e:
        print(f"Storage check failed: {e}")
        used_mb = 0
        quota_mb = round(STORAGE_QUOTA / (1024 * 1024), 1)
        percent_used = 0

    try:
        files = list_available_files(storage_dir)
    except Exception as e:
        print(f"Could not list files: {e}")
        files = []

    return render_template(
        "storage.html",
        active_page="storage",
        files=files,
        used_mb=used_mb,
        quota_mb=quota_mb,
        percent_used=percent_used,
    )

@app.route("/devices")
def devices():
    # Real discovery over the local network, falls back to KNOWN_DEVICES
    try:
        found = listen_for_devices([], timeout=5)
        device_list = found if found else KNOWN_DEVICES
    except Exception as e:
        print(f"Discovery failed: {e}")
        device_list = KNOWN_DEVICES

    return render_template(
        "device.html",
        active_page="devices",
        devices=device_list,
    )


@app.route("/transfers")
def transfers():
    return render_template("transfers.html", active_page="transfers")


@app.route("/network")
def network():
    return render_template("network.html", active_page="network")


@app.route("/settings")
def settings():
    return render_template("settings.html", active_page="settings")


if __name__ == "__main__":
    app.run(debug=True)
