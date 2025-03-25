###############################################################################
#                                   IMPORTS                                   #
###############################################################################
#from alive_progress import alive_bar
from logger import get_logger
from raycaster import Map, Player, Renderer
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from multiplayer import ClientNetwork
import time
import threading
from dotenv import load_dotenv
import os


###############################################################################
#                                  CONSTANTS                                  #
###############################################################################

log = get_logger(__name__)

log.info("imports successful")

load_dotenv()

log.info("environment loaded")

def get_env_int(key, default):
    try:
        return int(os.getenv(key, default))
    except ValueError:
        return default

def get_env_str(key, default):
    return os.getenv(key, default) # is str by default

FOV = get_env_int("RAYCASTER_FOV", 80)
NUM_RAYS = get_env_int("RAYCASTER_NUM_RAYS",120)
MAX_DISTANCE = get_env_int("RAYCASTER_MAX_DISTANCE",500)
KEY_FORWARD = get_env_str("KEY_FORWARD",'w')
KEY_LEFT = get_env_str("KEY_LEFT",'a')
KEY_BACKWARD = get_env_str("KEY_BACKWARD",'s')
KEY_RIGHT = get_env_str("KEY_RIGHT",'d')
MAP_MINIMAP_SIZE = get_env_int("MAP_MINIMAP_SIZE",4)
MAP_MINIMAP_OPACITY = get_env_int("MAP_MINIMAP_OPACITY",128)


###############################################################################
#                                INITIALIZATION                               #
###############################################################################

# === NETWORK INITIALIZATION ===
network = ClientNetwork()  # Connects to server at localhost:5555 by default

# === GAME INITIALIZATION ===
# Wait for map data
log.info("Waiting for map...")
while network.map_data is None:
    continue
log.info("Received map")

map_info = network.map_data
map_obj = Map(map_info['grid'], map_info['mapX'], map_info['mapY'], map_info['mapS'], map_info["colorMap"], map_info["spawnpoint"])

# You can adjust keybindings per client instance
key_bindings = {'FORWARD': KEY_FORWARD, 'BACKWARD': KEY_BACKWARD, 'LEFT': KEY_LEFT, 'RIGHT': KEY_RIGHT}
player = Player(map_info["spawnpoint"][0], map_info["spawnpoint"][1], 90, key_bindings, map_obj)

renderer = Renderer(map_obj=map_obj, fov=FOV, num_rays=NUM_RAYS, max_distance=MAX_DISTANCE, minimap_size=MAP_MINIMAP_SIZE, minimap_opacity=MAP_MINIMAP_OPACITY)  # Local player only for now

last_time = time.time()


# === GLUT INITIALIZATION ===
glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(1024, 512)
glutCreateWindow(b"Networked Raycaster Client")

glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

glutReshapeFunc(renderer.reshape) 


# === INPUT HANDLERS ===
def keyboard_down(key, x, y):
    try:
        key_char = key.decode().lower()
        if key_char in player.key_bindings.values():
            player.keys_pressed.add(key_char)
    except UnicodeDecodeError:
        pass

def keyboard_up(key, x, y):
    try:
        key_char = key.decode().lower()
        if key_char in player.keys_pressed:
            player.keys_pressed.remove(key_char)
    except UnicodeDecodeError:
        pass


# === DISPLAY FUNCTION ===
def display():
    if not network.running:
        log.warning("Server disconnected. Exiting client.")
        os._exit(0)  # Force exit immediately (no need to keep GLUT running)
        
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
    for remote_id, remote_data in network.players_state.items():
        # Skip rendering ourself
        if remote_id == str(network.my_id):  # IDs are string keys after JSON
            continue
        px = int(remote_data['px'])
        py = int(remote_data['py'])
        pa = int(remote_data['pa'])
        renderer.draw_minimap_player((px,py,pa))

    glutSwapBuffers()

    log.debug(f"Rendering players_state: {network.players_state}")


# === GLUT INITIALIZATION PART 2 ===

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

# === MAIN LOOP ===
glutMainLoop()
