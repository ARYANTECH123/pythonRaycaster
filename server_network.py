import socket
import threading
import json
import struct
from raycaster import Map

clients = {}  # conn: player_id
players_state = {}  # player_id: {px, py, pa}

# Server Map Definition

map_data = Map.load_from_file('maps/house_l.json').map_to_dict()

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
    # print(f"[SERVER] Broadcasting: {players_state}") # DEBUG
    for conn in list(clients.keys()):
        try:
            send_message(conn, players_state)
        except Exception as e:
            print(f"[SERVER] Broadcast error: {e}")
            conn.close()
            clients.pop(conn, None)

def handle_client(conn, addr, player_id):
    print(f"[SERVER] New connection from {addr}")
    clients[conn] = player_id

    # Step 1: Send init_id
    send_message(conn, {"init_id": player_id})
    print(f"[SERVER] Sent init_id to {addr}")

    # Send map data
    send_message(conn, {"map_data": map_data})
    print(f"[SERVER] Sent map_data to {addr}")

    # Step 2: Wait for ACK before broadcasting
    raw_len = recv_exact(conn, 4)
    if not raw_len:
        print(f"[SERVER] No ACK received from {addr}")
        return
    msg_len = struct.unpack('!I', raw_len)[0]
    data = recv_exact(conn, msg_len)
    #[ ] FIXME: make sure to only broadcast to those with ack recieved / close connexion when invalid ack. 
    # Otherwise you can join from browser, close the page, connexion is never closed and it keeps broadcasting to you.
    # Check with chatgpt if this might cause issues with normal clients
    try: 
        ack_msg = json.loads(data.decode())
    except: 
        ack_msg = {}
        print(f"[SERVER] No ACK from {addr}")
    if 'ack' not in ack_msg:
        print(f"[SERVER] Invalid ACK from {addr}")
        return
    print(f"[SERVER] Received ACK from {addr}")

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
        print(f"[SERVER] Error: {e}")
    finally:
        print(f"[SERVER] Connection lost: {addr}")
        conn.close()
        if conn in clients:
            clients.pop(conn)
        if player_id in players_state:
            players_state.pop(player_id)
        broadcast()

def start_server(host='127.0.0.1', port=5555):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"[SERVER] Listening on {host}:{port}")

    next_player_id = 1

    while True:
        conn, addr = server.accept()
        player_id = next_player_id
        next_player_id += 1

        # Initialize player's state
        players_state[player_id] = {"px": 150, "py": 400, "pa": 90}

        # Start handler
        thread = threading.Thread(target=handle_client, args=(conn, addr, player_id), daemon=True)
        thread.start()

if __name__ == "__main__":
    start_server()
