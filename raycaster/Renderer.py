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
        
        max_distance = 1000  # For shading according to distance

        # Draws sky
        sky_color = self.map.get_color("sky")
        glColor3ub(*sky_color)
        glBegin(GL_QUADS)
        glVertex(526,  0)
        glVertex(1006,  0)
        glVertex(1006,160)
        glVertex(526,160)
        glEnd()

        #Draws floor
        ground_color = self.map.get_color("ground")
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

            # Get collision data

            while dof < 20:
                # Store previous grid cell BEFORE moving
                prev_mx = int(rx) // self.map.mapS
                prev_my = int(ry) // self.map.mapS

                # Move ray
                rx += cos(ray_angle) * 5
                ry -= sin(ray_angle) * 5
                dof += 0.1

                # Current grid cell
                mx = int(rx) // self.map.mapS
                my = int(ry) // self.map.mapS

                # If outside of map, stop
                if mx < 0 or mx >= self.map.mapX or my < 0 or my >= self.map.mapY:
                    break

                # Get wall hit
                hit_cell_value = self.map.grid[my * self.map.mapX + mx]
                
                # If hit 
                if hit_cell_value != 0:
                    dis = hypot(rx - player.px, ry - player.py)
                    hit_wall = True

                    # Compare previous and current grid cells
                    delta_mx = mx - prev_mx
                    delta_my = my - prev_my

                    if abs(delta_mx) > abs(delta_my):
                        if delta_mx > 0:
                            wall_face = "West"
                        else:
                            wall_face = "East"
                    else:
                        if delta_my > 0:
                            wall_face = "North"
                        else:
                            wall_face = "South"
                            
                    break


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
            base_color = self.map.get_color(str(hit_cell_value)) # Get color of wall

            # Control how fast the damping applies:
            distance_factor = max(0.4, 1 - dis / max_distance)  # Keep at least 40% brightness

            # Shading
            shade_factors = {
                "North": 1.0,
                "South": 0.6,
                "East": 0.8,
                "West": 0.9
            }

            # Wall face factor:
            face_factor = shade_factors.get(wall_face, 1.0)

            # Final factor:
            final_factor = face_factor * distance_factor

            # Apply:
            shaded_color = tuple(
                max(0, min(255, int(c * final_factor)))
                for c in base_color
            )

            # Change color
            glColor3ub(*shaded_color)

            # Draw vertical line according to ray
            glLineWidth(8)
            glBegin(GL_LINES)
            glVertex2i(r * 8 + 530, int(line_offset))
            glVertex2i(r * 8 + 530, int(line_offset + line_height))
            glEnd()

            ra -= (self.FOV / self.num_rays)
