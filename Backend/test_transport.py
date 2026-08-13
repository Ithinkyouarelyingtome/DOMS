import socket
import threading
import time
from transport import send_with_fallback, receive_chunk

def server(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', port))
    s.listen(1)
    conn, addr = s.accept()
    data = receive_chunk(conn)
    print(f"Server on port {port} received:", data)
    conn.close()
    s.close()

# Only start a server on 6002 — leave 6001 with nothing listening
threading.Thread(target=server, args=(6002,)).start()
time.sleep(1)

devices = [("127.0.0.1", 6001), ("127.0.0.1", 6002)]
result = send_with_fallback(devices, b"testing fallback logic")
print("Overall success:", result)