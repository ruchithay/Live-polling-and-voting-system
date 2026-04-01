import socket
import threading
from cryptography.fernet import Fernet

# Load shared key
with open("secret.key", "rb") as f:
    fernet = Fernet(f.read())

SERVER_IP = "127.0.0.1"
PORT = 5005

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(5)

seq = 1


def send_encrypted(message: str):
    encrypted = fernet.encrypt(message.encode())
    client.sendto(encrypted, (SERVER_IP, PORT))


def listen_server():
    while True:
        try:
            data, _ = client.recvfrom(4096)
            msg = fernet.decrypt(data).decode().strip()

            if msg.startswith("RESULT"):
                parts = msg.split("|")
                print("\n===== LIVE RESULTS =====")
                for p in parts[1:]:
                    print(p)
                print("========================\n")

        except socket.timeout:
            continue  # 👈 timeout is fine, just keep listening
        except Exception as e:
            print("Listener error:", e)
            break  # only break on real errors


threading.Thread(target=listen_server, daemon=True).start()

client_id = input("Enter Client ID: ")
token = input("Enter Token: ")

while True:
    vote = input("Enter vote (A/B/C) or Q to quit: ").upper()

    if vote == "Q":
        print("Exiting...")
        break

    if vote not in ["A", "B", "C"]:
        print("Invalid. Choose A, B, or C.")
        continue

    message = f"VOTE|{client_id}|{token}|{seq}|{vote}"
    send_encrypted(message)

    try:
        response = None
        for _ in range(3):  # retry up to 3 times
            try:
                data, _ = client.recvfrom(4096)
                decoded = fernet.decrypt(data).decode().strip()
                if not decoded.startswith("RESULT"):
                    response = decoded
                    break
            except socket.timeout:
                continue

        if response:
            print(f"Server response: {response}")
        else:
            print("No response from server.")
    except Exception as e:
        print("Error:", e)

    seq += 1
