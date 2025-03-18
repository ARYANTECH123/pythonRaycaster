from raycaster import Map, Player, Renderer
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import multiprocessing
import time

# The per-player GLUT window runner
def run_player(player_id, world, key_bindings):
    # Create map & player locally
    map_obj = Map(world, 8, 8, 64)
    player = Player(150 if player_id == 1 else 300, 400, 90, key_bindings, map_obj)
    renderer = Renderer(map_obj, [player])  # Only render this player!

    last_time = time.time()

    # Input handlers specific to THIS process
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

    def display():
        nonlocal last_time
        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        player.move(delta_time)
        renderer.draw_scene(player)
        glutSwapBuffers()

    # GLUT setup
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(1024, 512)
    glutCreateWindow(f"Player {player_id}".encode())
    glClearColor(0.3, 0.3, 0.3, 0)
    gluOrtho2D(0, 1024, 512, 0)

    glutKeyboardFunc(keyboard_down)
    glutKeyboardUpFunc(keyboard_up)
    glutDisplayFunc(display)
    glutIdleFunc(display)

    glutMainLoop()

# ==== Shared World Data ====
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

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')  # Safer on Windows

    # Define key bindings per player
    player1_keys = {'FORWARD': 'z', 'BACKWARD': 's', 'LEFT': 'q', 'RIGHT': 'd'}
    player2_keys = {'FORWARD': 'i', 'BACKWARD': 'k', 'LEFT': 'j', 'RIGHT': 'l'}

    # Create processes
    p1 = multiprocessing.Process(target=run_player, args=(1, world, player1_keys))
    p2 = multiprocessing.Process(target=run_player, args=(2, world, player2_keys))

    p1.start()
    p2.start()

    p1.join()
    p2.join()
