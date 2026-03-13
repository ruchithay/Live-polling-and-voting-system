import socket
import threading
import time

SERVER_IP = "0.0.0.0"
PORT = 5005

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((SERVER_IP, PORT))

print("Server running on port", PORT)

votes = {"A":0, "B":0, "C":0}

# store clients who already voted
voted_clients = set()

# store client addresses for broadcasting
clients = set()

# statistics
received_packets = 0
lost_packets = 0
expected_seq = {}

lock = threading.Lock()


def broadcast_results():
    while True:
        time.sleep(10)

        result = f"RESULT|A:{votes['A']}|B:{votes['B']}|C:{votes['C']}"

        for c in clients:
            server.sendto(result.encode(), c)

        print("Broadcast:", result)


def show_statistics():
    while True:
        time.sleep(10)

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

    data, addr = server.recvfrom(1024)
    message = data.decode()

    clients.add(addr)

    parts = message.split("|")

    if parts[0] == "VOTE":

        client_id = parts[1]
        seq = int(parts[2])
        candidate = parts[3]

        with lock:
            received_packets += 1
            if client_id not in expected_seq:
                expected_seq[client_id] = seq

            if seq > expected_seq[client_id]:
                lost_packets += (seq - expected_seq[client_id])

            expected_seq[client_id] = seq + 1

        # 🔴 DUPLICATE VOTE CHECK
        if client_id in voted_clients:

            print("Duplicate vote from client:", client_id)

            server.sendto("REJECTED".encode(), addr)
            continue

        # invalid candidate check
        if candidate not in votes:
            server.sendto("INVALID".encode(), addr)
            continue

        # accept vote
        voted_clients.add(client_id)
        votes[candidate] += 1

        print("Vote accepted from", client_id, "->", candidate)

        server.sendto("ACCEPTED".encode(), addr)