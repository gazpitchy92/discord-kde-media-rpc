import os, socket, struct, json, time, signal, sys

def send(client, op, payload):
    data = json.dumps(payload).encode("utf-8")
    header = struct.pack("<II", op, len(data))
    client.sendall(header + data)

def recv(client):
    header = client.recv(8)
    if not header or len(header) < 8:
        raise ConnectionResetError("Discord IPC closed")
    op, length = struct.unpack("<II", header)
    data = client.recv(length)
    if not data:
        raise ConnectionResetError("Discord IPC closed")
    return op, json.loads(data.decode("utf-8"))

def connect_discord(client_id):
    uid = os.getuid()
    path = f"/run/user/{uid}/discord-ipc-0"
    while True:
        print("Checking for Discord...")
        if os.path.exists(path):
            try:
                client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                client.connect(path)
                send(client, 0, {"v": 1, "client_id": client_id})
                recv(client)
                print("Connected to Discord")
                return client
            except (ConnectionRefusedError, FileNotFoundError, BrokenPipeError, OSError):
                pass
        time.sleep(5)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    appid_file = os.path.join(base_dir, "discord.appid")
    playing_file = os.path.join(base_dir, "playing.txt")

    with open(appid_file, "r") as f:
        client_id = f.read().strip()

    def set_activity(client, text):
        text = text.strip()
        activity = None
        if text:
            state_text = text if len(text) <= 120 else text[:120] + "..."
            activity = {"state": state_text, "assets": {}}
        payload = {"cmd": "SET_ACTIVITY", "args": {"pid": os.getpid(), "activity": activity}, "nonce": str(time.time())}
        send(client, 1, payload)
        recv(client)
        print(f"Updated activity: {state_text if text else 'cleared'}")

    last_text = ""

    while True:
        client = connect_discord(client_id)
        try:
            while True:

                try:
                    send(client, 1, {"cmd": "PING", "args": {}, "nonce": str(time.time())})
                    recv(client)
                except (BrokenPipeError, ConnectionResetError, OSError):
                    raise

                try:
                    with open(playing_file, "r") as f:
                        text = f.read()
                except FileNotFoundError:
                    text = ""

                if text != last_text:
                    set_activity(client, text)
                    last_text = text

                time.sleep(5)

        except (BrokenPipeError, ConnectionResetError, OSError):
            print("Lost connection to Discord")
            try:
                client.close()
            except:
                pass
            time.sleep(5)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda sig, frame: sys.exit(0))
    main()
