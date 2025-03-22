from OpenGL.GL import *
import json
from logger import get_logger

log = get_logger(__name__)

class Map:
    def __init__(self, grid, mapX, mapY, mapS, colorMap, spawnpoint):
        self.grid = grid
        self.mapX = mapX # Map width
        self.mapY = mapY # Map height
        self.mapS = mapS # Tile size in pixels. Should be 32 to 128. Ideally 64
        self.colorMap = colorMap
        self.spawnpoint = spawnpoint
    
    def is_wall(self, mx, my):
        if 0 <= mx < self.mapX and 0 <= my < self.mapY:
            return self.grid[my * self.mapX + mx] != 0
        return True  # Out of bounds = wall

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
        load.info(f"Saved map to {filename}")

    @classmethod
    def load_from_file(cls, filename):
        with open(filename, 'r') as f:
            map_data = json.load(f)
        log.info(f"Loaded map from {filename}")
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
            color = (255,0,255) # MAGENTA FOR ERROR
            log.error(f"TEXTURE {texture} DOES NOT EXIST")
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
    
    