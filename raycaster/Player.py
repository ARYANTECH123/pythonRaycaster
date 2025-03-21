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

    # Getters
    def get_px(self):
        return self.px

    def get_py(self):
        return self.py

    def get_pa(self):
        return self.pa

    def get_pdx(self):
        return self.pdx

    def get_pdy(self):
        return self.pdy

    def get_keys_pressed(self):
        return self.keys_pressed

    def get_key_bindings(self):
        return self.key_bindings

    def get_map(self):
        return self.map

    