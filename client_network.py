import socket
import threading
import json
import struct

class ClientNetwork:
    def __init__(self, host='127.0.0.1', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((host, port))
        self.players_state = {}
        self.my_id = None
        self.running = True

        # Start listening
        thread = threading.Thread(target=self.listen, daemon=True)
        thread.start()

    def recv_exact(self, sock, n):
        data = b''
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def listen(self):
        try:
            while self.running:
                # Step 1: Read length
                raw_len = self.recv_exact(self.server, 4)
                if not raw_len:
                    break
                msg_len = struct.unpack('!I', raw_len)[0]

                # Step 2: Read full message
                data = self.recv_exact(self.server, msg_len)
                if not data:
                    break

                message = json.loads(data.decode())

                # Handle message
                if 'init_id' in message:
                    self.my_id = message['init_id']
                    print(f"[CLIENT] Assigned Player ID: {self.my_id}")

                    # Send ACK
                    ack = json.dumps({"ack": True}).encode()
                    length = struct.pack('!I', len(ack))
                    self.server.sendall(length + ack)
                    print("[CLIENT] Sent ACK to server")

                else:
                    self.players_state = message
                    print(f"[CLIENT] Updated players_state: {self.players_state}")
        except Exception as e:
            print(f"[CLIENT] Listen error: {e}")
            self.running = False

    def send_player_update(self, px, py, pa):
        try:
            message = {"px": px, "py": py, "pa": pa}
            message_bytes = json.dumps(message).encode()
            length = struct.pack('!I', len(message_bytes))
            self.server.sendall(length + message_bytes)
        except Exception as e:
            print(f"[CLIENT] Send error: {e}")

    def close(self):
        self.running = False
        self.server.close()
