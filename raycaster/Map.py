from OpenGL.GL import *
import json

class Map:
    def __init__(self, grid, mapX, mapY, mapS, colorMap, spawnpoint):
        self.grid = grid
        self.mapX = mapX # Map width
        self.mapY = mapY # Map height
        self.mapS = mapS # Tile size in pixels. Should be 32 to 128. Ideally 64
        self.colorMap = colorMap
        self.spawnpoint = spawnpoint
        self.minimap_size = 16
    
    def is_wall(self, mx, my):
        if 0 <= mx < self.mapX and 0 <= my < self.mapY:
            return self.grid[my * self.mapX + mx] != 0
        return True  # Out of bounds = wall

    def draw(self):
        for y in range(self.mapY):
            for x in range(self.mapX):
                cell_value = self.grid[y * self.mapX + x]
                if cell_value != 0 : # if not void
                    glColor3ub(*self.get_color(str(cell_value)))
                else:
                    glColor3ub(*self.get_color(str("ground")))

                minimap_size = self.get_minimap_size()
                xo, yo = x * minimap_size, y * minimap_size
                glBegin(GL_QUADS)
                glVertex2i(xo,             yo                  )
                glVertex2i(xo,             yo + minimap_size   )
                glVertex2i(xo + minimap_size, yo + minimap_size)
                glVertex2i(xo + minimap_size, yo               )
                glEnd()

    # TODO look into if i should use static method here and on other classes
    def save_to_file(self, filename):
        map_data = {
            "grid": self.grid,
            "mapX": self.mapX,
            "mapY": self.mapY,
            "mapS": self.mapS,
            "colorMap": self.colorMap,
            "spawnpoint": self.spawnpoint
        }
        with open(filename, 'w') as f:
            json.dump(map_data, f)
        print(f"[MAP] Saved map to {filename}")

    @classmethod
    def load_from_file(cls, filename):
        with open(filename, 'r') as f:
            map_data = json.load(f)
        print(f"[MAP] Loaded map from {filename}")
        return cls(map_data["grid"], map_data["mapX"], map_data["mapY"], map_data["mapS"], map_data["colorMap"], map_data["spawnpoint"])

    def map_to_dict(self):
        return {
            "grid": self.grid,
            "mapX": self.mapX,
            "mapY": self.mapY,
            "mapS": self.mapS,
            "colorMap": self.colorMap,
            "spawnpoint": self.spawnpoint
        }
    
    # GETTERS
    def get_color(self, texture):
        try: 
            color = self.colorMap[texture]
        except:
            color = (1,0,1) # MAGENTA FOR ERROR
            print(f"[MAP] TEXTURE {texture} DOES NOT EXIST")
        return color

    def get_spawnpoint(self):
        return self.spawnpoint

    def get_grid(self):
        return self.grid

    def get_mapX(self):
        return self.mapX
    
    def get_mapY(self):
        return self.mapY

    def get_mapS(self):
        return self.mapS
    
    def get_colorMap(self):
        return self.colorMap
    
    def get_spawnpoint(self):
        return self.spawnpoint
    
    def get_minimap_size(self):
        return self.minimap_size
    


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

    colorMap = {
        "ground":(74,194,44),
        "sky":(235,255,254),
        "wall":(100,100,100)
    }

    map_info = {
        "grid": world,
        "mapX": 8,
        "mapY": 8,
        "mapS": 64,
        "colorMap":colorMap
    }

    map = Map(map_info['grid'], map_info['mapX'], map_info['mapY'], map_info['mapS'], map_info['colorMap'])

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
        "mapS": 64,
        "colorMap":colorMap
    }

    map = Map(map_info['grid'], map_info['mapX'], map_info['mapY'], map_info['mapS'], map_info['colorMap'])

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
        "mapS": 32,
        "colorMap":colorMap
    }

    map = Map(map_info['grid'], map_info['mapX'], map_info['mapY'], map_info['mapS'], map_info['colorMap'])

    map.save_to_file('maps/house_l.json')