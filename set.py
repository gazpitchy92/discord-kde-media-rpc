import os, socket, struct, json, time, signal, sys

def send(client, op, payload):
    data = json.dumps(payload).encode("utf-8")
    header = struct.pack("<II", op, len(data))
    client.sendall(header + data)

def recv(client):
    header = client.recv(8)
    if len(header) < 8:
        return None
    op, length = struct.unpack("<II", header)
    data = client.recv(length).decode("utf-8")
    return op, json.loads(data)

def main():
    uid = os.getuid()
    path = f"/run/user/{uid}/discord-ipc-0"
    
    while True:
        if os.path.exists(path):
            try:
                client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                client.connect(path)
                break
            except ConnectionRefusedError:
                client.close()
                print("Discord not launched yet, waiting...")
        else:
            print("Discord not launched yet, waiting...")
        time.sleep(5)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    appid_file = os.path.join(base_dir, "discord.appid")
    playing_file = os.path.join(base_dir, "playing.txt")

    with open(appid_file, "r") as f:
        client_id = f.read().strip()

    send(client, 0, {"v": 1, "client_id": client_id})
    print("Handshake:", recv(client))

    def check_existing_activity():
        payload = {"cmd": "GET_ACTIVITY", "args": {}, "nonce": str(time.time())}
        send(client, 1, payload)
        response = recv(client)
        return response[1].get('data', {}).get('activity') is not None

    def set_activity(text):
        text = text.strip()
        activity = None
        if text:
            state_text = text if len(text) <= 120 else text[:120] + "..."
            activity = {"state": state_text, "assets": {}}
        payload = {"cmd": "SET_ACTIVITY", "args": {"pid": os.getpid(), "activity": activity}, "nonce": str(time.time())}
        send(client, 1, payload)
        print("Set activity:", recv(client))

    def cleanup(sig, frame):
        payload = {"cmd": "SET_ACTIVITY", "args": {"pid": os.getpid(), "activity": None}, "nonce": str(time.time())}
        send(client, 1, payload)
        print("Cleared:", recv(client))
        client.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    print("Presence active. Press CTRL+C to exit.")
    last_text = ""
    while True:
        try:
            with open(playing_file, "r") as f:
                text = f.read()
        except FileNotFoundError:
            text = ""
        if text != last_text:
            if not check_existing_activity():
                set_activity(text)
            last_text = text
        time.sleep(5)

if __name__ == "__main__":
    main()