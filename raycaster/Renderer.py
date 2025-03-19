from math import sin, cos, radians, hypot
from OpenGL.GL import *

class Renderer:
    def __init__(self, map_obj, players):
        self.map = map_obj
        self.players = players
        self.FOV = 60
        self.num_rays = 60

    def draw_scene(self, player):
        self.map.draw()
        player.draw()
        self.cast_rays(player)  # Raycasting specific to this player


    def cast_rays(self, player):

        # Draws sky
        sky_color = self.map.get_color("sky")
        print(f"--- SKY COLOR {sky_color} ---")
        glColor3ub(*sky_color)
        glBegin(GL_QUADS)
        glVertex(526,  0)
        glVertex(1006,  0)
        glVertex(1006,160)
        glVertex(526,160)
        glEnd()

        #Draws floor
        ground_color = self.map.get_color("ground")
        print(f"--- GROUND COLOR {ground_color} ---")
        glColor3ub(*ground_color)
        glBegin(GL_QUADS)
        glVertex2i(526,160)
        glVertex2i(1006,160)
        glVertex2i(1006,320)
        glVertex2i(526,320)
        glEnd()

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
            line_height = (self.map.mapS * 320) / dis # [ ] FIXME Potential division by 0
            if line_height > 320:
                line_height = 320
            line_offset = 160 - line_height / 2

            glColor3ub(*self.map.get_color("wall"))
            glLineWidth(8)
            glBegin(GL_LINES)
            glVertex2i(r * 8 + 530, int(line_offset))
            glVertex2i(r * 8 + 530, int(line_offset + line_height))
            glEnd()

            ra -= (self.FOV / self.num_rays)
