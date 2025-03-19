from raycaster import Map, Player, Renderer
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from multiplayer import ClientNetwork
import time
import threading

# === NETWORK INITIALIZATION ===
network = ClientNetwork()  # Connects to server at localhost:5555 by default

# === GAME INITIALIZATION ===
# Wait for map data
while network.map_data is None:
    print("[CLIENT] Waiting for map...")

map_info = network.map_data
map_obj = Map(map_info['grid'], map_info['mapX'], map_info['mapY'], map_info['mapS'], map_info["colorMap"])

# You can adjust keybindings per client instance
key_bindings = {'FORWARD': 'z', 'BACKWARD': 's', 'LEFT': 'q', 'RIGHT': 'd'}
player = Player(150, 400, 90, key_bindings, map_obj)

renderer = Renderer(map_obj, [player])  # Local player only for now

last_time = time.time()

# === INPUT HANDLERS ===
def keyboard_down(key, x, y):
    try:
        key_char = key.decode()
        if key_char in player.key_bindings.values():
            player.keys_pressed.add(key_char)
    except UnicodeDecodeError:
        pass

def keyboard_up(key, x, y):
    try:
        key_char = key.decode()
        if key_char in player.keys_pressed:
            player.keys_pressed.remove(key_char)
    except UnicodeDecodeError:
        pass

# === DISPLAY FUNCTION ===
def display():
    global last_time
    current_time = time.time()
    delta_time = current_time - last_time
    last_time = current_time

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Move local player
    player.move(delta_time)

    # Send local player update to server
    network.send_player_update(player.px, player.py, player.pa)

    # Draw local scene
    renderer.draw_scene(player)

    # Draw remote players (optional, if desired)
    glColor3f(0.0, 1.0, 0.0)  # Different color for remote
    for remote_id, remote_data in network.players_state.items():
        # Skip rendering ourself
        if remote_id == str(network.my_id):  # IDs are string keys after JSON
            continue
        glPointSize(6)
        glBegin(GL_POINTS)
        glVertex2i(int(remote_data['px']), int(remote_data['py']))
        glEnd()

    glutSwapBuffers()
    # print(f"[CLIENT] Rendering players_state: {network.players_state}") # DEBUG


# === GLUT INITIALIZATION ===
glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(1024, 512)
glutCreateWindow(b"Networked Raycaster Client")

glClearColor(0.3, 0.3, 0.3, 0)
gluOrtho2D(0, 1024, 512, 0)

glutKeyboardFunc(keyboard_down)
glutKeyboardUpFunc(keyboard_up)
glutDisplayFunc(display)
glutIdleFunc(display)

# === CLEANUP ===
def on_close():
    network.close()

import atexit
atexit.register(on_close)

glutMainLoop()
