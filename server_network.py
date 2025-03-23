import socket
import threading
import json
import struct
import sys
import os
import signal
from logger import get_logger
from raycaster import Map

log = get_logger(__name__)

clients = {}  # conn: player_id
players_state = {}  # player_id: {px, py, pa}
shutdown_event = threading.Event()


# === Helper functions ===

def send_message(conn, message_dict):
    message = json.dumps(message_dict).encode()
    length = struct.pack('!I', len(message))
    conn.sendall(length + message)


def recv_exact(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


def broadcast():
    log.debug(f"Broadcasting: {players_state}")
    for conn in list(clients.keys()):
        try:
            send_message(conn, players_state)
        except Exception as e:
            log.error(f"Broadcast error: {e}")
            conn.close()
            clients.pop(conn, None)


def handle_client(conn, addr, player_id, map_data):
    log.info(f"New connection from {addr}")
    clients[conn] = player_id

    try:
        # Send init_id
        send_message(conn, {"init_id": player_id})
        log.info(f"Sent init_id to {addr}")

        # Send map data
        send_message(conn, {"map_data": map_data})
        log.info(f"Sent map_data to {addr}")

        # Wait for ACK before broadcasting
        raw_len = recv_exact(conn, 4)
        if not raw_len:
            log.info(f"No ACK received from {addr}")
            return
        msg_len = struct.unpack('!I', raw_len)[0]
        data = recv_exact(conn, msg_len)
        try:
            ack_msg = json.loads(data.decode())
        except:
            ack_msg = {}
            log.warning(f"No valid ACK from {addr}")
        if 'ack' not in ack_msg:
            log.warning(f"Invalid ACK from {addr}")
            return
        log.info(f"Received ACK from {addr}")

        broadcast()

        # Main receive loop
        while not shutdown_event.is_set():
            raw_len = recv_exact(conn, 4)
            if not raw_len:
                break
            msg_len = struct.unpack('!I', raw_len)[0]
            data = recv_exact(conn, msg_len)
            message = json.loads(data.decode())
            players_state[player_id] = message

            broadcast()

    except ConnectionAbortedError:
        log.info(f"Connection aborted: {addr}")
    except ConnectionResetError:
        log.info(f"Connexion reset by client {addr}")
    except Exception as e:
        log.warning(f"Client error: {e}")
    finally:
        log.info(f"Connection lost: {addr}")
        conn.close()
        clients.pop(conn, None)
        players_state.pop(player_id, None)
        broadcast()


def choose_map():
    log.info("Choosing map...")
    MAPS_DIRECTORY = 'maps/'

    # List all files
    files = [f for f in os.listdir(MAPS_DIRECTORY) if os.path.isfile(os.path.join(MAPS_DIRECTORY, f))]

    if not files:
        print("No map files found!")
        sys.exit(1)

    print("Available maps:")
    for idx, filename in enumerate(files):
        print(f"{idx + 1}. {filename}")

    while True:
        try:
            choice = int(input("Choose a map by number: ")) - 1
            if 0 <= choice < len(files):
                chosen_map = files[choice]
                break
            else:
                print("Invalid choice.")
        except ValueError:
            print("Enter a valid number.")

    log.info(f"Loading map: {chosen_map}")
    return Map.load_from_file(os.path.join(MAPS_DIRECTORY, chosen_map)).map_to_dict()


def start_server(host='127.0.0.1', port=5555):
    log.info("Starting server...")

    map_data = choose_map()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen()
    server.settimeout(0.5)  # Periodically check for shutdown

    log.info(f"Listening on {host}:{port}")

    next_player_id = 1
    threads = []

    # Signal handler to cleanly shutdown
    def signal_handler(sig, frame):
        log.info("Shutdown signal received.")
        shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)

    try:
        while not shutdown_event.is_set():
            try:
                conn, addr = server.accept()
            except socket.timeout:
                continue
            except OSError:
                break  # Socket closed

            log.info(f"Accepted connection from {addr}")
            player_id = next_player_id
            next_player_id += 1

            t = threading.Thread(target=handle_client, args=(conn, addr, player_id, map_data))
            t.start()
            threads.append(t)

    except Exception as e:
        log.error(f"Error in server loop: {e}")

    finally:
        log.info("Closing server socket...")
        server.close()

        log.info("Waiting for client threads to exit...")
        shutdown_event.set()  # Inform all threads to shut down

        for t in threads:
            t.join()

        log.info("Server shutdown complete.")
        sys.exit(0)


if __name__ == "__main__":
    start_server()
