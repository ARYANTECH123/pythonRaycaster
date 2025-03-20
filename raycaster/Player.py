from OpenGL.GL import *
from math import sin, cos, tan, sqrt, radians

class Player:
    def __init__(self, x, y, angle, key_bindings, map_obj):
        self.px = x
        self.py = y
        self.pa = angle
        self.pdx = cos(radians(self.pa))
        self.pdy = -sin(radians(self.pa))
        self.keys_pressed = set()
        self.key_bindings = key_bindings
        self.map = map_obj

    def update_direction(self):
        self.pdx = cos(radians(self.pa))
        self.pdy = -sin(radians(self.pa))

    def move(self, delta_time):
        speed = 200  # Pixels per second (adjust as needed)

        move_step = speed * delta_time

        # Rotation
        if self.key_bindings['LEFT'] in self.keys_pressed:
            self.pa += 360 * delta_time  # Degrees per second
            self.pa %= 360
            self.update_direction()
        if self.key_bindings['RIGHT'] in self.keys_pressed:
            self.pa -= 360 * delta_time
            self.pa %= 360
            self.update_direction()

        # Movement
        new_x = self.px
        new_y = self.py
        if self.key_bindings['FORWARD'] in self.keys_pressed:
            new_x += self.pdx * move_step
            new_y += self.pdy * move_step
        if self.key_bindings['BACKWARD'] in self.keys_pressed:
            new_x -= self.pdx * move_step
            new_y -= self.pdy * move_step

        # Collision detection
        if not self.map.is_wall(int(new_x) // self.map.mapS, int(new_y) // self.map.mapS):
            self.px = new_x
            self.py = new_y


    def draw(self):

        glColor3f(1, 1, 0)
        
        map_x = self.px / self.map.get_mapS() * self.map.get_minimap_size()
        map_y = self.py / self.map.get_mapS() * self.map.get_minimap_size()

        # Dot
        glPointSize(8)
        glLineWidth(3)
        glBegin(GL_POINTS)
        glVertex2i(int(map_x), int(map_y))
        glEnd()
        
        # Forward segment
        glBegin(GL_LINES)
        glVertex2i(int(map_x), int(map_y))
        glVertex2i(int(map_x + 20 * self.pdx), int(map_y + 20 * self.pdy))
        glEnd()
