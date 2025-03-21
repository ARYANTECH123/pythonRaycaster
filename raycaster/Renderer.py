from math import sin, cos, radians, hypot
from typing import Union, Tuple
from .Player import Player
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class Renderer:
    def __init__(self, map_obj, fov:int = 80, num_rays = 120, max_distance = 500, minimap_size = 4):
        self.map = map_obj
        self.FOV = fov
        self.num_rays = num_rays # resolution
        self.max_distance = max_distance # shading
        self.minimap_size = minimap_size

    def reshape(self, width, height):
        """Handles window resizing correctly."""
        glViewport(0, 0, width, height)  # Use full window area
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, width, height, 0)  # Top-left origin
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def get_window_size(self):
        """Dynamically get current window size."""
        width = glutGet(GLUT_WINDOW_WIDTH)
        height = glutGet(GLUT_WINDOW_HEIGHT)
        return width, height

    def draw_scene(self, player):
        self.cast_rays(player)
        self.draw_minimap()
        self.draw_minimap_player(player)

    def cast_rays(self, player):

        screen_width, screen_height = self.get_window_size()
        slice_width = screen_width / self.num_rays

        # Draw sky
        sky_color = self.map.get_color("sky")
        glColor3ub(*sky_color)
        glBegin(GL_QUADS)
        glVertex2i(0, 0)
        glVertex2i(screen_width, 0)
        glVertex2i(screen_width, screen_height // 2)
        glVertex2i(0, screen_height // 2)
        glEnd()

        # Draw floor
        ground_color = self.map.get_color("ground")
        glColor3ub(*ground_color)
        glBegin(GL_QUADS)
        glVertex2i(0, screen_height // 2)
        glVertex2i(screen_width, screen_height // 2)
        glVertex2i(screen_width, screen_height)
        glVertex2i(0, screen_height)
        glEnd()

        ra = player.pa + (self.FOV / 2)
        for r in range(self.num_rays):
            ray_angle = radians(ra)
            dof = 0
            dis = 0
            rx, ry = player.px, player.py
            hit_wall = False

            while dof < 20:
                prev_mx = int(rx) // self.map.get_mapS()
                prev_my = int(ry) // self.map.get_mapS()

                rx += cos(ray_angle) * 5
                ry -= sin(ray_angle) * 5
                dof += 0.1

                mx = int(rx) // self.map.get_mapS()
                my = int(ry) // self.map.get_mapS()

                if mx < 0 or mx >= self.map.get_mapX() or my < 0 or my >= self.map.get_mapY():
                    break

                hit_cell_value = self.map.get_grid()[my * self.map.get_mapX() + mx]

                if hit_cell_value != 0:
                    dis = hypot(rx - player.px, ry - player.py)
                    hit_wall = True

                    delta_mx = mx - prev_mx
                    delta_my = my - prev_my

                    if abs(delta_mx) > abs(delta_my):
                        wall_face = "West" if delta_mx > 0 else "East"
                    else:
                        wall_face = "North" if delta_my > 0 else "South"
                    break

            if not hit_wall:
                ra -= (self.FOV / self.num_rays)
                continue

            # Fisheye correction
            ca = radians(player.pa - ra)
            dis *= cos(ca)

            # Wall projection height
            line_height = (self.map.mapS * screen_height) / (dis + 0.0001)
            if line_height > screen_height:
                line_height = screen_height
            line_offset = (screen_height // 2) - line_height / 2

            # Wall color and shading
            base_color = self.map.get_color(str(hit_cell_value))
            distance_factor = max(0.7, 1 - (dis / self.get_max_distance()) ** 0.5)

            shade_factors = {
                "North": 1.0,
                "South": 0.8,
                "East": 0.7,
                "West": 0.6
            }
            face_factor = shade_factors.get(wall_face, 1.0)
            final_factor = face_factor * distance_factor

            shaded_color = tuple(
                max(0, min(255, int(c * final_factor)))
                for c in base_color
            )

            # Draw wall slice:
            if r == self.num_rays - 1:
                # Special case: make sure last ray hits right of the screen
                x = screen_width - 1
                glLineWidth(1)  # Single pixel width
            else:
                x = int(r * slice_width)
                glLineWidth(int(slice_width) + 1)

            glColor3ub(*shaded_color)
            glBegin(GL_LINES)
            glVertex2i(x, int(line_offset))
            glVertex2i(x, int(line_offset + line_height))
            glEnd()

            ra -= (self.FOV / self.num_rays)
   
    def draw_minimap(self):
        minimap_size = self.get_minimap_size()
        for y in range(self.map.get_mapY()):
            for x in range(self.map.get_mapX()):
                cell_value = self.map.get_grid()[y * self.map.get_mapX() + x]

                if cell_value != 0 : # if not void
                    glColor3ub(*self.map.get_color(str(cell_value)))
                else:
                    glColor3ub(*self.map.get_color(str("ground")))

                xo, yo = x * minimap_size, y * minimap_size
                glBegin(GL_QUADS)
                glVertex2i(xo,                yo               )
                glVertex2i(xo,                yo + minimap_size)
                glVertex2i(xo + minimap_size, yo + minimap_size)
                glVertex2i(xo + minimap_size, yo               )
                glEnd()

    def draw_minimap_player(self, player_or_coords: Union[Player, Tuple[float, float, float]]) -> None:

        mapS = self.get_map().get_mapS()
        minimap_size = self.get_minimap_size()
        segment_length = 0.25

        if isinstance(player_or_coords, Player):
            glColor3f(0, 1, 1) # CYAN COLOR FOR PLAYER
            px, py, pdx, pdy = player_or_coords.get_px(), player_or_coords.get_py(), player_or_coords.get_pdx(), player_or_coords.get_pdy()
        else:
            glColor3f(1, 0, 0) # RED COLOR FOR OTHER PLAYERS
            px, py, pa = player_or_coords  # Expecting tuple (px, py, pa)
            # Calculate pdx, pdy based on pa:
            pdx = cos(radians(pa))
            pdy = -sin(radians(pa))
    


        
        map_x = px / mapS * minimap_size
        map_y = py / mapS * minimap_size

        # Dot
        glPointSize(8)
        glLineWidth(3)
        glBegin(GL_POINTS)
        glVertex2i(int(map_x), int(map_y))
        glEnd()
        
        # Forward segment
        glBegin(GL_LINES)
        glVertex2i(int(map_x), int(map_y))
        glVertex2i(int(map_x + 10 * pdx), int(map_y + 10 * pdy))
        glEnd()
    
    # Getters

    def get_map(self):
        return self.map

    def get_FOV(self):
        return self.FOV

    def get_num_rays(self):
        return self.num_rays

    def get_max_distance(self):
        return self.max_distance

    def get_minimap_size(self):
        return self.minimap_size

    

