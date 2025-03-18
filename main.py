from raycaster import Map, Player, Renderer
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import time

last_time = time.time()

def keyboard_down(key, x, y):
    try:
        key_char = key.decode()
        for player in players:
            if key_char in player.key_bindings.values():
                player.keys_pressed.add(key_char)
    except UnicodeDecodeError:
        print(f"Ignored non-decodable key: {key}")


def keyboard_up(key, x, y):
    try:
        key_char = key.decode()
        for player in players:
            if key_char in player.keys_pressed:
                player.keys_pressed.remove(key_char)
    except UnicodeDecodeError:
        print(f"Ignored non-decodable key: {key}")


            
def display():
    global last_time
    current_time = time.time()
    delta_time = current_time - last_time
    last_time = current_time

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    for player in players:
        player.move(delta_time)  # Pass delta_time

    renderer.draw_scene()
    glutSwapBuffers()


# ====== Map and Players setup ======
world = [
    1,1,1,1,1,1,1,1,
    1,1,0,1,0,0,0,1,
    1,0,0,0,0,1,0,1,
    1,1,1,0,0,0,0,1,
    1,0,0,0,0,0,0,1,
    1,0,0,0,0,0,0,1,
    1,0,0,0,0,0,0,1,
    1,0,0,0,0,0,0,1
]

map_obj = Map(world, 8, 8, 64)

player1 = Player(150, 400, 90, {'FORWARD': 'z', 'BACKWARD': 's', 'LEFT': 'q', 'RIGHT': 'd'}, map_obj)
player2 = Player(300, 400, 90, {'FORWARD': 'i', 'BACKWARD': 'k', 'LEFT': 'j', 'RIGHT': 'l'}, map_obj)

players = [player1, player2]
renderer = Renderer(map_obj, players)


# ====== GLUT Initialization ======

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(1024, 512)
glutCreateWindow(b"Raycasting Engine")

# Set up 2D orthographic projection
glClearColor(0.3, 0.3, 0.3, 0)
gluOrtho2D(0, 1024, 512, 0)

# Register Callbacks AFTER glutInit()
glutKeyboardFunc(keyboard_down)
glutKeyboardUpFunc(keyboard_up)
glutDisplayFunc(display)
glutIdleFunc(display)

glutMainLoop()
