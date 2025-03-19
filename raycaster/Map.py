from OpenGL.GL import *
import json

class Map:
    def __init__(self, grid, mapX, mapY, mapS):
        self.grid = grid
        self.mapX = mapX # Map width
        self.mapY = mapY # Map height
        self.mapS = mapS # Tile size in pixels. Should be 32 to 128. Ideally 64
    
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

    # TODO look into if i should use static method here and on other classes
    def save_to_file(self, filename):
        map_data = {
            "grid": self.grid,
            "mapX": self.mapX,
            "mapY": self.mapY,
            "mapS": self.mapS
        }
        with open(filename, 'w') as f:
            json.dump(map_data, f)
        print(f"[MAP] Saved map to {filename}")

    @classmethod
    def load_from_file(cls, filename):
        with open(filename, 'r') as f:
            map_data = json.load(f)
        print(f"[MAP] Loaded map from {filename}")
        return cls(map_data["grid"], map_data["mapX"], map_data["mapY"], map_data["mapS"])

    def map_to_dict(self):
        return {
            "grid": self.grid,
            "mapX": self.mapX,
            "mapY": self.mapY,
            "mapS": self.mapS
        }


if __name__ == "__main__":
    """
    Test of the class and its methods
    """

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

    map_info = {
        "grid": world,
        "mapX": 8,
        "mapY": 8,
        "mapS": 64
    }

    map = Map(map_info['grid'], map_info['mapX'], map_info['mapY'], map_info['mapS'])

    map.save_to_file('maps/aryantech123.json')

    # MAP 2

    world = [
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
    ]

    map_info = {
        "grid": world,
        "mapX": 16,
        "mapY": 16,
        "mapS": 64
    }

    map = Map(map_info['grid'], map_info['mapX'], map_info['mapY'], map_info['mapS'])

    map.save_to_file('maps/empty_l.json')

    # MAP 3

    world = [
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,
    0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,
    0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,
    0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,
    0,0,0,1,1,1,1,0,1,1,1,1,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
    ]

    map_info = {
        "grid": world,
        "mapX": 16,
        "mapY": 16,
        "mapS": 64
    }

    map = Map(map_info['grid'], map_info['mapX'], map_info['mapY'], map_info['mapS'])

    map.save_to_file('maps/house_l.json')