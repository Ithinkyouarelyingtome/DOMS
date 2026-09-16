import socket
import time
BROADCAST_PORT = 9999
BROADCAST_INTERVAL = 3  # seconds between announcements

def broadcast_presence(my_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    message = f"DOMS_DEVICE:{my_port}".encode()

    while True:
        sock.sendto(message, ('255.255.255.255', BROADCAST_PORT))
        time.sleep(BROADCAST_INTERVAL)

def listen_for_devices(known_devices, timeout=10):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', BROADCAST_PORT))
    sock.settimeout(1)  # check every 1 second, so we can respect the overall timeout

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            data, addr = sock.recvfrom(1024)
            message = data.decode()

            if message.startswith("DOMS_DEVICE:"):
                port = int(message.split(":")[1])
                host = addr[0]
                device = (host, port)

                if device not in known_devices:
                    known_devices.append(device)
                    print(f"Discovered new device: {device}")

        except socket.timeout:
            continue

    sock.close()
    return known_devices

if __name__ == "__main__":
    import sys
    mode = sys.argv[1]

    if mode == "broadcast":
        my_port = int(sys.argv[2])
        print(f"Broadcasting presence as port {my_port}...")
        broadcast_presence(my_port)
    elif mode == "listen":
        found = listen_for_devices([], timeout=15)
        print("Final discovered devices:", found)
