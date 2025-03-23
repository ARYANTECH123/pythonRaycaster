import socket
import threading
import json
import struct
from logger import get_logger

log = get_logger(__name__)

class ClientNetwork:
    def __init__(self, host='127.0.0.1', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((host, port))
        self.players_state = {}
        self.my_id = None
        self.running = True
        self.map_data = None


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
                raw_len = self.recv_exact(self.server, 4)
                if not raw_len:
                    log.warning("Server disconnected (length header missing). Closing client.")
                    break  # Stop loop

                msg_len = struct.unpack('!I', raw_len)[0]
                data = self.recv_exact(self.server, msg_len)
                if not data:
                    log.warning("Server disconnected (message body missing). Closing client.")
                    break

                message = json.loads(data.decode())

                # Handle messages:
                if 'init_id' in message:
                    self.my_id = message['init_id']
                    log.info(f"Assigned Player ID: {self.my_id}")

                    # Send ACK
                    try:
                        ack = json.dumps({"ack": True}).encode()
                        length = struct.pack('!I', len(ack))
                        self.server.sendall(length + ack)
                        log.info("Sent ACK to server")
                    except Exception as e:
                        log.error(f"Error sending ACK: {e}")
                        break  # Connection issue, break out

                elif 'map_data' in message:
                    self.map_data = message['map_data']
                    log.info(f"Received map data")

                else:
                    self.players_state = message
                    log.debug(f"Updated players_state: {self.players_state}")

        except Exception as e:
            log.critical(f"Listen error: {e}")
        finally:
            log.warning("Shutting down client listener.")
            self.running = False
            try:
                self.server.close()
            except:
                pass

    def send_player_update(self, px, py, pa):
        if not self.running:
            return  # Don't attempt to send if disconnected
        try:
            message = {"px": px, "py": py, "pa": pa}
            message_bytes = json.dumps(message).encode()
            length = struct.pack('!I', len(message_bytes))
            self.server.sendall(length + message_bytes)
        except Exception as e:
            log.critical(f"Send failed (server down?): {e}")
            self.running = False


    def close(self):
        self.running = False
        self.server.close()
