import socket
import threading
import time
from cryptography.fernet import Fernet
import errno

# Load shared key
with open("secret.key", "rb") as f:
    fernet = Fernet(f.read())

SERVER_IP = "0.0.0.0"
PORT = 5005

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((SERVER_IP, PORT))

print("Secure UDP Server running on port", PORT)

votes = {"A": 0, "B": 0, "C": 0}
voted_clients = set()
clients = set()

received_packets = 0
lost_packets = 0
expected_seq = {}
lock = threading.Lock()

valid_tokens = {
    "101": "token1",
    "102": "token2",
    "103": "token3"
}


def send_encrypted(message: str, addr):
    encrypted = fernet.encrypt(message.encode())
    server.sendto(encrypted, addr)


def broadcast_results():
    while True:
        time.sleep(10)
        result = f"RESULT|A:{votes['A']}|B:{votes['B']}|C:{votes['C']}"
        for c in list(clients):
            try:
                send_encrypted(result, c)
            except:
                clients.discard(c)
        print("Broadcast:", result)


def show_statistics():
    while True:
        time.sleep(10)
        with lock:
            total = received_packets + lost_packets
            if total == 0:
                continue
            loss_rate = (lost_packets / total) * 100
            print("\n------ Network Statistics ------")
            print("Packets Received:", received_packets)
            print("Packets Lost:", lost_packets)
            print("Packet Loss Rate: %.2f%%" % loss_rate)
            print("--------------------------------\n")


threading.Thread(target=broadcast_results, daemon=True).start()
threading.Thread(target=show_statistics, daemon=True).start()

while True:
    try:
        data, addr = server.recvfrom(4096)
        # Decrypt incoming packet
        try:
            message = fernet.decrypt(data).decode().strip()
        except Exception:
            print(f"Decryption failed from {addr} — packet tampered or invalid")
            server.sendto(fernet.encrypt(b"REJECTED"), addr)
            continue
    except socket.error as e:
        if e.winerror == 10054:  # Windows ICMP port unreachable — safe to ignore
            continue
        print("Receive error:", e)
        continue

    clients.add(addr)
    response = "REJECTED"

    parts = message.split("|")
    if len(parts) == 5 and parts[0] == "VOTE":
        client_id = parts[1]
        token = parts[2]

        try:
            seq = int(parts[3])
        except:
            seq = None

        candidate = parts[4]

        if valid_tokens.get(client_id) != token:
            print(f"Invalid token from client {client_id}")
        elif seq is not None:
            with lock:
                received_packets += 1
                if client_id not in expected_seq:
                    expected_seq[client_id] = seq + 1
                else:
                    if seq > expected_seq[client_id]:
                        lost = seq - expected_seq[client_id]
                        lost_packets += lost
                        print(f"Packet loss detected from {client_id}: {lost} packets")
                    expected_seq[client_id] = seq + 1

            if client_id in voted_clients:
                print(f"Duplicate vote from: {client_id}")
            elif candidate not in votes:
                print(f"Invalid candidate from: {client_id}")
            else:
                voted_clients.add(client_id)
                votes[candidate] += 1
                print(f"Vote accepted from {client_id} -> {candidate}")
                response = "ACCEPTED"
                result = f"RESULT|A:{votes['A']}|B:{votes['B']}|C:{votes['C']}"
                for c in list(clients):
                    try:
                        send_encrypted(result, c)
                    except:
                        clients.discard(c)
    send_encrypted(response, addr)
