import socket
import threading
import json

class ClientNetwork:
    def __init__(self, host='127.0.0.1', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((host, port))
        self.players_state = {}
        self.running = True
        # Start listening thread
        thread = threading.Thread(target=self.listen)
        thread.start()

    def listen(self):
        try:
            while self.running:
                data = self.server.recv(4096).decode()
                if data:
                    self.players_state = json.loads(data)
        except:
            print("[CLIENT] Server disconnected.")
            self.running = False

    def send_player_update(self, px, py, pa):
        try:
            message = {"px": px, "py": py, "pa": pa}
            self.server.sendall(json.dumps(message).encode())
        except:
            pass

    def close(self):
        self.running = False
        self.server.close()
