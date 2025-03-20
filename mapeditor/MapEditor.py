import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, colorchooser
import json
import os

def rgb_to_hex(rgb):
    """Convert an [R, G, B] list to a hex color."""
    return "#%02x%02x%02x" % tuple(rgb)

class MapEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Map Editor")
        
        # Folder and file info
        self.current_folder = None
        self.current_file = None
        self.map_data = None  # Will hold JSON data
        self.grid_data = []   # 2D list representation of grid
        self.tile_size = 32   # Default tile size
        
        # Spawnpoint (pixel coordinates) and dragging flag
        self.spawnpoint = None
        self.dragging_spawnpoint = False

        # Define textures:
        # Non-paintable textures (only color adjustable, not used for painting)
        self.non_paintable_textures = ["ground", "sky"]
        # Paintable textures (appear as selectable radio buttons)
        # Now include "0" as the erase texture and "1" as the first painting texture.
        self.paintable_textures = ["0", "1"]
        self.all_textures = self.non_paintable_textures + self.paintable_textures

        # Default colors.
        # "0" (erase) is white, "ground" and "sky" come from your sample, "1" is wall.
        self.texture_colors = {
            "0": "#ffffff",     # erase/void (white)
            "ground": "#4ac22c", # from [74, 194, 44]
            "sky": "#ebfffe",    # from [235, 255, 254]
            "1": "#db4900"      # default wall
        }
        
        # Selected painting texture (only among the paintable ones)
        self.texture_var = tk.StringVar(value="1")
        
        # Layout: left (file management), center (canvas/controls), right (texture editor)
        self.left_frame = tk.Frame(self.master)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.center_frame = tk.Frame(self.master)
        self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.texture_frame = tk.Frame(self.master)
        self.texture_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        self.create_widgets()
        self.create_texture_sidebar()

    def create_widgets(self):
        # --- Left frame: Folder selection, file list, and add new map ---
        self.btn_select_folder = tk.Button(self.left_frame, text="Select Folder", command=self.select_folder)
        self.btn_select_folder.pack(pady=5)
        
        self.btn_add_map = tk.Button(self.left_frame, text="Add Map", command=self.add_map)
        self.btn_add_map.pack(pady=5)
        
        self.listbox_files = tk.Listbox(self.left_frame, width=30)
        self.listbox_files.pack(fill=tk.BOTH, expand=True)
        self.listbox_files.bind("<<ListboxSelect>>", self.on_file_select)
        
        # --- Center frame: Canvas and controls ---
        self.canvas = tk.Canvas(self.center_frame, bg="gray")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind("<B1-Motion>", self.canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_release)
        
        self.control_frame = tk.Frame(self.center_frame)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        # Sliders for map width, height, and tile size.
        self.width_slider = tk.Scale(self.control_frame, from_=4, to=50, orient=tk.HORIZONTAL,
                                     label="Width", command=self.on_width_change)
        self.width_slider.pack(side=tk.LEFT, padx=5)
        
        self.height_slider = tk.Scale(self.control_frame, from_=4, to=50, orient=tk.HORIZONTAL,
                                      label="Height", command=self.on_height_change)
        self.height_slider.pack(side=tk.LEFT, padx=5)
        
        self.tile_size_slider = tk.Scale(self.control_frame, from_=8, to=64, orient=tk.HORIZONTAL,
                                         label="Tile Size", command=self.on_tile_size_change)
        self.tile_size_slider.set(self.tile_size)
        self.tile_size_slider.pack(side=tk.LEFT, padx=5)
        
        # Save button.
        self.btn_save = tk.Button(self.control_frame, text="Save", command=self.save_file)
        self.btn_save.pack(side=tk.LEFT, padx=5)
        
    def create_texture_sidebar(self):
        """Creates the texture sidebar with color pickers and, for paintable textures, radio buttons."""
        # Clear the texture frame.
        for widget in self.texture_frame.winfo_children():
            widget.destroy()
            
        tk.Label(self.texture_frame, text="Textures", font=("Arial", 12, "bold")).pack(pady=5)
        
        # For each texture in all_textures, create a row.
        for tex in self.all_textures:
            frame = tk.Frame(self.texture_frame)
            frame.pack(pady=2, padx=5, fill=tk.X)
            # For paintable textures (not ground or sky), add a radio button.
            if tex not in self.non_paintable_textures:
                rb = tk.Radiobutton(frame, text=tex, variable=self.texture_var, value=tex)
                rb.pack(side=tk.LEFT)
            else:
                tk.Label(frame, text=tex).pack(side=tk.LEFT)
            # Add a color picker button.
            btn = tk.Button(frame, bg=self.texture_colors.get(tex, "gray"), width=6,
                            command=lambda t=tex: self.choose_color(t))
            btn.pack(side=tk.RIGHT)
            
        # Button to add a new texture.
        add_btn = tk.Button(self.texture_frame, text="Add Texture", command=self.add_texture)
        add_btn.pack(pady=10)
        
    def choose_color(self, tex):
        """Let the user choose a new color for the given texture."""
        color = colorchooser.askcolor()[1]
        if color:
            self.texture_colors[tex] = color
            self.draw_grid()
            self.create_texture_sidebar()
            
    def add_texture(self):
        """Adds a new paintable texture with the next available number and default gray color."""
        digit_keys = [int(t) for t in self.paintable_textures if t.isdigit()]
        next_num = max(digit_keys) + 1 if digit_keys else 1
        next_texture = str(next_num)
        self.paintable_textures.append(next_texture)
        self.all_textures = self.non_paintable_textures + self.paintable_textures
        self.texture_colors[next_texture] = "#808080"  # default gray
        self.create_texture_sidebar()
        
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.current_folder = folder
            self.populate_file_list()
            
    def populate_file_list(self):
        self.listbox_files.delete(0, tk.END)
        for filename in os.listdir(self.current_folder):
            if filename.endswith(".json"):
                self.listbox_files.insert(tk.END, filename)
                
    def on_file_select(self, event):
        if not self.listbox_files.curselection():
            return
        index = self.listbox_files.curselection()[0]
        filename = self.listbox_files.get(index)
        file_path = os.path.join(self.current_folder, filename)
        self.load_file(file_path)
        
    def load_file(self, file_path):
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            self.current_file = file_path
            self.map_data = data
            
            # Read map dimensions and grid; convert flat list to 2D list.
            mapX = data.get("mapX", 0)
            mapY = data.get("mapY", 0)
            grid = data.get("grid", [])
            self.grid_data = [grid[i * mapX:(i + 1) * mapX] for i in range(mapY)]
            self.tile_size = data.get("mapS", 32)
            self.tile_size_slider.set(self.tile_size)
            self.width_slider.set(mapX)
            self.height_slider.set(mapY)
            
            # Update texture colors from the file's colormap.
            # Remap keys: "wall" -> "1"; "void"/"erase" -> "0".
            if "colorMap" in data:
                file_colormap = data["colorMap"]
                for key, rgb in file_colormap.items():
                    key_str = str(key)
                    if key_str.lower() == "wall":
                        key_str = "1"
                    elif key_str.lower() in ["void", "erase"]:
                        key_str = "0"
                    self.texture_colors[key_str] = rgb_to_hex(rgb)
            
            # Ensure non-paintable textures exist.
            defaults = {"ground": "#4ac22c", "sky": "#ebfffe", "1": "#db4900", "0": "#ffffff"}
            for tex in self.non_paintable_textures:
                if tex not in self.texture_colors:
                    self.texture_colors[tex] = defaults.get(tex, "#000000")
            for tex in ["0", "1"]:
                if tex not in self.texture_colors:
                    self.texture_colors[tex] = defaults.get(tex, "#000000")
                    
            # Determine painting textures: keys that are digits.
            self.paintable_textures = sorted(
                [key for key in self.texture_colors.keys() 
                 if key not in self.non_paintable_textures and key.isdigit()],
                key=lambda x: int(x)
            )
            # Make sure "0" and "1" exist.
            if "0" not in self.paintable_textures:
                self.texture_colors["0"] = self.texture_colors.get("0", "#ffffff")
                self.paintable_textures.insert(0, "0")
            if "1" not in self.paintable_textures:
                self.texture_colors["1"] = self.texture_colors.get("1", "#db4900")
                self.paintable_textures.append("1")
                
            self.all_textures = self.non_paintable_textures + self.paintable_textures
            
            # Ensure a valid painting texture is selected.
            if self.texture_var.get() not in self.paintable_textures:
                self.texture_var.set(self.paintable_textures[0])
            
            # Set the spawnpoint: if not in file, default to center of the map.
            if "spawnpoint" in data:
                self.spawnpoint = data["spawnpoint"]
            else:
                # Default to center: (mapX/2 * tile_size, mapY/2 * tile_size)
                self.spawnpoint = [(mapX / 2) * self.tile_size, (mapY / 2) * self.tile_size]
            
            self.create_texture_sidebar()
            self.draw_grid()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")
            
    def draw_grid(self):
        self.canvas.delete("all")
        if not self.grid_data:
            return
        rows = len(self.grid_data)
        cols = len(self.grid_data[0])
        self.canvas.config(scrollregion=(0, 0, cols * self.tile_size, rows * self.tile_size))
        for i in range(rows):
            for j in range(cols):
                x1 = j * self.tile_size
                y1 = i * self.tile_size
                x2 = x1 + self.tile_size
                y2 = y1 + self.tile_size
                val = str(self.grid_data[i][j])
                color = self.texture_colors.get(val, "gray")
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color,
                                             outline="black", tags=f"cell_{i}_{j}")
        # Draw the spawnpoint on top.
        self.draw_spawnpoint()
        
    def draw_spawnpoint(self):
        if self.spawnpoint is None:
            return
        # Remove any old spawnpoint drawing.
        self.canvas.delete("spawnpoint")
        x, y = self.spawnpoint
        cross_size = 5
        self.canvas.create_line(x - cross_size, y, x + cross_size, y, fill="red", width=2, tags="spawnpoint")
        self.canvas.create_line(x, y - cross_size, x, y + cross_size, fill="red", width=2, tags="spawnpoint")
        
    def is_near_spawn(self, event, tol=8):
        """Return True if event is within tol pixels of the spawnpoint."""
        if self.spawnpoint is None:
            return False
        x, y = self.spawnpoint
        dx = event.x - x
        dy = event.y - y
        return (dx * dx + dy * dy) <= (tol * tol)
        
    def update_spawnpoint(self, event):
        """Update spawnpoint to event coordinates and redraw."""
        self.spawnpoint = [event.x, event.y]
        self.draw_grid()
        
    def canvas_click(self, event):
        # If click is near the spawnpoint, start dragging it.
        if self.is_near_spawn(event):
            self.dragging_spawnpoint = True
            self.update_spawnpoint(event)
        else:
            self.paint_at(event)
        
    def canvas_drag(self, event):
        if self.dragging_spawnpoint:
            self.update_spawnpoint(event)
        else:
            self.paint_at(event)
        
    def canvas_release(self, event):
        self.dragging_spawnpoint = False
        
    def get_cell_from_coords(self, event):
        col = event.x // self.tile_size
        row = event.y // self.tile_size
        if row < 0 or row >= len(self.grid_data) or col < 0 or col >= len(self.grid_data[0]):
            return None, None
        return row, col
        
    def paint_at(self, event):
        row, col = self.get_cell_from_coords(event)
        if row is not None and col is not None and self.texture_var.get():
            new_val = int(self.texture_var.get())
            if self.grid_data[row][col] != new_val:
                self.grid_data[row][col] = new_val
                x1 = col * self.tile_size
                y1 = row * self.tile_size
                x2 = x1 + self.tile_size
                y2 = y1 + self.tile_size
                color = self.texture_colors.get(str(new_val), "gray")
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color,
                                             outline="black", tags=f"cell_{row}_{col}")
        
    def on_width_change(self, value):
        if not self.grid_data:
            return
        new_width = int(value)
        old_width = len(self.grid_data[0])
        rows = len(self.grid_data)
        for i in range(rows):
            if new_width > old_width:
                self.grid_data[i].extend([0] * (new_width - old_width))
            elif new_width < old_width:
                self.grid_data[i] = self.grid_data[i][:new_width]
        if self.map_data is not None:
            self.map_data["mapX"] = new_width
        self.draw_grid()
        
    def on_height_change(self, value):
        if not self.grid_data:
            return
        new_height = int(value)
        old_height = len(self.grid_data)
        cols = len(self.grid_data[0])
        if new_height > old_height:
            for _ in range(new_height - old_height):
                self.grid_data.append([0] * cols)
        elif new_height < old_height:
            self.grid_data = self.grid_data[:new_height]
        if self.map_data is not None:
            self.map_data["mapY"] = new_height
        self.draw_grid()
        
    def on_tile_size_change(self, value):
        self.tile_size = int(value)
        if self.map_data is not None:
            self.map_data["mapS"] = self.tile_size
        self.draw_grid()
        
    def color_to_hex(self, color):
        """Convert a color name or hex string to a hex string."""
        if color.startswith("#"):
            return color
        else:
            r, g, b = self.master.winfo_rgb(color)
            r = int(r / 256)
            g = int(g / 256)
            b = int(b / 256)
            return "#{:02x}{:02x}{:02x}".format(r, g, b)
        
    def save_file(self):
        if not self.current_file or not self.map_data:
            return
        # Flatten the 2D grid back to a flat list.
        flat_grid = [cell for row in self.grid_data for cell in row]
        self.map_data["grid"] = flat_grid
        self.map_data["mapX"] = len(self.grid_data[0])
        self.map_data["mapY"] = len(self.grid_data)
        self.map_data["mapS"] = self.tile_size
        # Save the spawnpoint.
        if self.spawnpoint is not None:
            self.map_data["spawnpoint"] = self.spawnpoint
        
        # Update the colormap for all textures.
        new_colorMap = {}
        for tex in self.all_textures:
            hex_color = self.texture_colors.get(tex, "#000000")
            hex_color = self.color_to_hex(hex_color)
            hex_color = hex_color.lstrip("#")
            rgb = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
            new_colorMap[tex] = rgb
        self.map_data["colorMap"] = new_colorMap
        
        try:
            with open(self.current_file, "w") as f:
                json.dump(self.map_data, f, indent=4)
            messagebox.showinfo("Saved", "Map saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")
            
    def add_map(self):
        if not self.current_folder:
            messagebox.showwarning("No Folder Selected", "Please select a folder first.")
            return
        filename = simpledialog.askstring("New Map", "Enter new map filename (with .json extension):")
        if not filename:
            return
        if not filename.endswith(".json"):
            filename += ".json"
        file_path = os.path.join(self.current_folder, filename)
        if os.path.exists(file_path):
            messagebox.showwarning("File Exists", "File already exists!")
            return
        # Default map: 16x16 grid, tile size 32, default colormap, and spawnpoint at center.
        default_map = {
            "grid": [0] * (16 * 16),
            "mapX": 16,
            "mapY": 16,
            "mapS": 32,
            "spawnpoint": [(16 / 2) * 32, (16 / 2) * 32],
            "colorMap": {
                "ground": [74, 194, 44],
                "sky": [235, 255, 254],
                "1": [219, 73, 0],
                "0": [255, 255, 255]
            }
        }
        try:
            with open(file_path, "w") as f:
                json.dump(default_map, f, indent=4)
            messagebox.showinfo("Map Created", f"Created new map: {filename}")
            self.populate_file_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create file: {e}")

def main():
    root = tk.Tk()
    editor = MapEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
