import socket
import threading
import json
import struct
import sys
import os
from logger import get_logger
from raycaster import Map

log = get_logger(__name__)

clients = {}  # conn: player_id
players_state = {}  # player_id: {px, py, pa}

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

    # Step 1: Send init_id
    send_message(conn, {"init_id": player_id})
    log.info(f"Sent init_id to {addr}")

    # Send map data
    send_message(conn, {"map_data": map_data})
    log.info(f"Sent map_data to {addr}")

    # Step 2: Wait for ACK before broadcasting
    raw_len = recv_exact(conn, 4)
    if not raw_len:
        log.info(f"No ACK received from {addr}")
        return
    msg_len = struct.unpack('!I', raw_len)[0]
    data = recv_exact(conn, msg_len)
    #[ ] FIXME: make sure to only broadcast to those with ack recieved / close connection when invalid ack. 
    # Otherwise you can join from browser, close the page, connection is never closed and it keeps broadcasting to you.
    # Check with chatgpt if this might cause issues with normal clients
    try: 
        ack_msg = json.loads(data.decode())
    except: 
        ack_msg = {}
        log.warning(f"No ACK from {addr}")
    if 'ack' not in ack_msg:
        log.warning(f"Invalid ACK from {addr}")
        return
    log.info(f"Received ACK from {addr}")

    # Now safe to broadcast
    broadcast()

    try:
        while True:
            raw_len = recv_exact(conn, 4)
            if not raw_len:
                break
            msg_len = struct.unpack('!I', raw_len)[0]
            data = recv_exact(conn, msg_len)
            message = json.loads(data.decode())
            players_state[player_id] = message

            broadcast()
    except Exception as e:
        log.warning(f"{e}")
    finally:
        log.info(f"Connection lost: {addr}")
        conn.close()
        if conn in clients:
            clients.pop(conn)
        if player_id in players_state:
            players_state.pop(player_id)
        broadcast()


def choose_map():
    log.info("Choosing map...")
    MAPS_DIRECTORY = 'maps/'

    # List all files in the maps directory
    files = [f for f in os.listdir(MAPS_DIRECTORY) if os.path.isfile(os.path.join(MAPS_DIRECTORY, f))]
    
    if not files:
        print("No map files found in the directory!")
        return None

    # Display files
    print("Available maps:")
    for idx, filename in enumerate(files):
        print(f"{idx + 1}. {filename}")

    # Ask user to choose
    while True:
        try:
            choice = int(input("Choose a map by number: ")) - 1
            if 0 <= choice < len(files):
                choosen_map = files[choice]
                break
            else:
                print("Invalid choice. Please choose a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Load and return map
    log.info(f"Loading map: {choosen_map}")
    return Map.load_from_file(os.path.join(MAPS_DIRECTORY, choosen_map)).map_to_dict()


def start_server(host='127.0.0.1', port=5555):
    
    log.info("Starting server...")

    # Map
    map_data = choose_map()

    log.info("Binding server to port...")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()

    log.info(f"Listening on {host}:{port}")

    next_player_id = 1
    
    log.info("Starting accepting connection loop")
    while True:
        conn, addr = server.accept()
        player_id = next_player_id
        next_player_id += 1
        
        # Start handler
        thread = threading.Thread(target=handle_client, args=(conn, addr, player_id, map_data), daemon=True)
        thread.start()

if __name__ == "__main__":
    start_server()
