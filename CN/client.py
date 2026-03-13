import socket
import threading

SERVER_IP = "127.0.0.1"
PORT = 5005

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

seq = 1


def listen_server():
    while True:
        try:
            data, _ = client.recvfrom(1024)
            msg = data.decode()

            if msg.startswith("RESULT"):

                parts = msg.split("|")

                print("\n===== LIVE RESULTS =====")
                for p in parts[1:]:
                    print(p)
                print("========================\n")

            else:
                print("Server:", msg)

        except:
            break


threading.Thread(target=listen_server, daemon=True).start()

client_id = input("Enter Client ID: ")

while True:

    vote = input("Enter vote A/B/C or Q: ").upper()

    if vote == "Q":
        break

    if vote not in ["A","B","C"]:
        print("Invalid vote")
        continue

    message = f"VOTE|{client_id}|{seq}|{vote}"

    client.sendto(message.encode(), (SERVER_IP, PORT))

    seq += 1