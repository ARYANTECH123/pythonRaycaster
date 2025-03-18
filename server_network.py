import socket
import threading
import json

clients = {}  # key: conn, value: player_id
players_state = {}  # key: player_id, value: {px, py, pa}

def handle_client(conn, addr, player_id):
    print(f"[SERVER] New connection from {addr}")
    clients[conn] = player_id
    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            # Update player state
            message = json.loads(data)
            players_state[player_id] = message

            # Broadcast to all clients
            broadcast()
    except Exception as e:
        print(f"[SERVER] Error: {e}")
    finally:
        print(f"[SERVER] Connection lost: {addr}")
        conn.close()
        clients.pop(conn, None)
        players_state.pop(player_id, None)

def broadcast():
    for conn in clients:
        try:
            # Send full game state
            state_json = json.dumps(players_state)
            conn.sendall(state_json.encode())
        except:
            pass  # Ignore send errors for now

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

        # Init player
        players_state[player_id] = {"px": 150, "py": 400, "pa": 90}
        thread = threading.Thread(target=handle_client, args=(conn, addr, player_id))
        thread.start()

if __name__ == "__main__":
    start_server()
