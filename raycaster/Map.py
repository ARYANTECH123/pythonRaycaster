from OpenGL.GL import *

class Map:
    def __init__(self, grid, mapX, mapY, mapS):
        self.grid = grid
        self.mapX = mapX
        self.mapY = mapY
        self.mapS = mapS
    
    def is_wall(self, mx, my):
        if 0 <= mx < self.mapX and 0 <= my < self.mapY:
            return self.grid[my * self.mapX + mx] == 1
        return True  # Out of bounds = wall

    def draw(self):
        for y in range(self.mapY):
            for x in range(self.mapX):
                if self.grid[y * self.mapX + x] == 1:
                    glColor3f(1, 1, 1)
                else:
                    glColor3f(0, 0, 0)
                xo, yo = x * self.mapS, y * self.mapS
                glBegin(GL_QUADS)
                glVertex2i(xo + 1, yo + 1)
                glVertex2i(xo + 1, yo + self.mapS - 1)
                glVertex2i(xo + self.mapS - 1, yo + self.mapS - 1)
                glVertex2i(xo + self.mapS - 1, yo + 1)
                glEnd()
