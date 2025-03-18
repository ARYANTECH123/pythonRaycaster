from math import sin, cos, radians, hypot
from OpenGL.GL import *

class Renderer:
    def __init__(self, map_obj, players):
        self.map = map_obj
        self.players = players
        self.FOV = 60
        self.num_rays = 60

    def draw_scene(self):
        self.map.draw()
        for player in self.players:
            player.draw()
            self.cast_rays(player)

    def cast_rays(self, player):
        ra = player.pa + (self.FOV / 2)
        for r in range(self.num_rays):
            ray_angle = radians(ra)
            dof = 0
            dis = 0
            rx, ry = player.px, player.py
            hit_wall = False  # Track if wall is hit

            while dof < 20:  # Max depth (higher allows longer rays)
                mx = int(rx) // self.map.mapS
                my = int(ry) // self.map.mapS
                if mx < 0 or mx >= self.map.mapX or my < 0 or my >= self.map.mapY:
                    break  # Ray exited map bounds, stop tracing
                if self.map.grid[my * self.map.mapX + mx] == 1:
                    dis = hypot(rx - player.px, ry - player.py)
                    hit_wall = True
                    break
                rx += cos(ray_angle) * 5
                ry -= sin(ray_angle) * 5
                dof += 0.1

            if not hit_wall:
                ra -= (self.FOV / self.num_rays)
                continue  # Skip drawing wall slice

            # Wall hit, draw projection:
            ca = radians(player.pa - ra)
            dis *= cos(ca)  # Fix fisheye
            line_height = (self.map.mapS * 320) / dis
            if line_height > 320:
                line_height = 320
            line_offset = 160 - line_height / 2

            glColor3f(1.0, 0.0, 0.0)
            glLineWidth(8)
            glBegin(GL_LINES)
            glVertex2i(r * 8 + 530, int(line_offset))
            glVertex2i(r * 8 + 530, int(line_offset + line_height))
            glEnd()

            ra -= (self.FOV / self.num_rays)
