DOMS --- Distributed Offline Mesh Storage

DOMS (Distributed Offline Mesh Storage) is a Python-based distributed
storage system designed to store and transfer files across nearby
devices without relying on centralized cloud storage.

Project Status

The core backend is implemented. The current development focus is
connecting the Flask web interface to the existing backend and
completing end-to-end multi-device testing.

Features

Distributed file storage

File chunking

Storage quota management

Cryptographic utilities

Device-to-device transport

Local network device discovery

File distribution

File retrieval and reconstruction

File deletion

Flask web interface

Storage and device dashboards

Project Structure

DOMS/
├── Backend/
│   ├── chunker.py
│   ├── config.py
│   ├── crypto.py
│   ├── device.py
│   ├── discovery.py
│   ├── run_device.py
│   ├── storage_manager.py
│   ├── transport.py
│   ├── test_dh.py
│   └── test_transport.py
│
├── webui/
│   ├── app.py
│   ├── static/
│   │   ├── DOMS.png
│   │   └── style.css
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── storage.html
│       ├── transfers.html
│       ├── device.html
│       ├── network.html
│       └── settings.html
│
└── README.md

Backend

chunker.py

Splits files into chunks for distributed storage.

storage_manager.py

Manages local chunk storage, storage usage, quotas, and chunk saving.

crypto.py

Provides cryptographic functionality used by DOMS.

transport.py

Handles communication between DOMS devices.

discovery.py

Discovers DOMS devices on the local network.

device.py

Provides high-level file and device operations, including:

Listing available files

Discovering files across devices

Sending files to the network

Retrieving files

Reconstructing files

Deleting files

config.py

Stores configuration such as known devices, storage directory, and
storage quota.

Web Interface

The Flask web UI provides:

Page        Purpose

Home        Storage and network overview
Files       View and manage files
Transfers   Transfer activity
Devices     View and discover devices
Network     Network information
Settings    Configuration

The pages share base.html and the common stylesheet.

Running DOMS

Use Python 3 and run the Flask application from the DOMS project
root.

cd C:\Users\<your-name>\Desktop\DOMS
python -m webui.app

Then open:

http://127.0.0.1:5000

Running from the project root is important because the application
imports the Backend package.

Device Configuration

An address such as:

127.0.0.1:6001

refers to the current computer.

Therefore:

127.0.0.1:6001
127.0.0.1:6002

are two configured local endpoints, not automatically two physical
devices.

Actual multi-device operation requires DOMS instances running on
reachable devices on the local network.

Current Integration

The web UI is being connected to the existing backend. Backend
functionality should not be duplicated inside the Flask routes.

The UI should call the existing backend for:

Chunking

Storage

Cryptography

Device discovery

Transport

File reconstruction

File deletion

Current UI integration includes real backend information for storage
usage, local files, and configured/discovered devices.

Remaining Work

Connect upload to file distribution

Connect retrieval/download

Connect deletion

Connect the Transfers page to real transfer activity

Improve live device discovery

Connect Network and Settings pages

Test multiple real DOMS nodes

Add error handling and loading states

Perform complete end-to-end testing

Architecture

User
  ↓
Flask Web UI
  ↓
Existing DOMS Backend
  ↓
Chunking / Storage / Crypto
  ↓
Transport
  ↓
DOMS Devices

The web interface is intended to be a management layer around the
backend, not a replacement for backend logic.

Testing

Backend tests currently include:

Backend/test_dh.py
Backend/test_transport.py

End-to-end testing should verify:

Device discovery

File distribution

Chunk storage

File retrieval

File reconstruction

File deletion

Storage quota behavior

Technology Stack

Python

Flask

HTML

CSS

JavaScript

Computer Networking

Cryptography

Distributed Storage

Goal

DOMS aims to let nearby devices store, share, and retrieve files across
a local mesh without depending on centralized cloud storage.

Author

Dakshin Salian