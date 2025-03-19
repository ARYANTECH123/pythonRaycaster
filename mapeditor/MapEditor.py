import tkinter as tk
from tkinter import filedialog, messagebox
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

        # Available textures and their display colors.
        # For now, "0" is void and "1" is wall.
        # When loading a file, if a colormap "wall" is found it will be used for texture "1".
        self.textures = ["0", "1"]
        self.texture_colors = {"0": "black", "1": "#db4900"}

        self.current_texture = "1"  # Default painting texture

        self.create_widgets()

    def create_widgets(self):
        # --- Left frame: Folder selection and file list ---
        self.left_frame = tk.Frame(self.master)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.btn_select_folder = tk.Button(self.left_frame, text="Select Folder", command=self.select_folder)
        self.btn_select_folder.pack(pady=5)

        self.listbox_files = tk.Listbox(self.left_frame, width=30)
        self.listbox_files.pack(fill=tk.BOTH, expand=True)
        self.listbox_files.bind("<<ListboxSelect>>", self.on_file_select)

        # --- Right frame: Canvas and controls ---
        self.right_frame = tk.Frame(self.master)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Canvas for drawing the grid
        self.canvas = tk.Canvas(self.right_frame, bg="gray")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind("<B1-Motion>", self.canvas_drag)

        # Control panel at the bottom
        self.control_frame = tk.Frame(self.right_frame)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        # Slider for map width
        self.width_slider = tk.Scale(self.control_frame, from_=4, to=50, orient=tk.HORIZONTAL,
                                     label="Width", command=self.on_width_change)
        self.width_slider.pack(side=tk.LEFT, padx=5)

        # Slider for map height
        self.height_slider = tk.Scale(self.control_frame, from_=4, to=50, orient=tk.HORIZONTAL,
                                      label="Height", command=self.on_height_change)
        self.height_slider.pack(side=tk.LEFT, padx=5)

        # Slider for tile size (mapS)
        self.tile_size_slider = tk.Scale(self.control_frame, from_=8, to=64, orient=tk.HORIZONTAL,
                                         label="Tile Size", command=self.on_tile_size_change)
        self.tile_size_slider.set(self.tile_size)
        self.tile_size_slider.pack(side=tk.LEFT, padx=5)

        # Texture selection (radio buttons)
        self.texture_var = tk.StringVar(value=self.current_texture)
        for tex in self.textures:
            rb = tk.Radiobutton(self.control_frame, text=f"Texture {tex}",
                                variable=self.texture_var, value=tex, command=self.on_texture_change)
            rb.pack(side=tk.LEFT, padx=5)

        # Save button
        self.btn_save = tk.Button(self.control_frame, text="Save", command=self.save_file)
        self.btn_save.pack(side=tk.LEFT, padx=5)

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

            # Read map dimensions and grid; convert flat grid list to 2D list (row-major)
            mapX = data.get("mapX", 0)
            mapY = data.get("mapY", 0)
            grid = data.get("grid", [])
            self.grid_data = [grid[i * mapX:(i + 1) * mapX] for i in range(mapY)]
            self.tile_size = data.get("mapS", 32)
            self.tile_size_slider.set(self.tile_size)
            self.width_slider.set(mapX)
            self.height_slider.set(mapY)

            # Update texture colors from the colormap if available
            colorMap = data.get("colorMap", {})
            if "wall" in colorMap:
                # Replace the "wall" texture with "1"
                self.texture_colors["1"] = rgb_to_hex(colorMap["wall"])
            self.draw_grid()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def draw_grid(self):
        self.canvas.delete("all")
        if not self.grid_data:
            return
        rows = len(self.grid_data)
        cols = len(self.grid_data[0])
        # Optionally, update the canvas scroll region
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

    def get_cell_from_coords(self, event):
        col = event.x // self.tile_size
        row = event.y // self.tile_size
        if row < 0 or row >= len(self.grid_data) or col < 0 or col >= len(self.grid_data[0]):
            return None, None
        return row, col

    def canvas_click(self, event):
        self.paint_at(event)

    def canvas_drag(self, event):
        self.paint_at(event)

    def paint_at(self, event):
        row, col = self.get_cell_from_coords(event)
        if row is not None and col is not None:
            new_val = int(self.texture_var.get())
            if self.grid_data[row][col] != new_val:
                self.grid_data[row][col] = new_val
                # Redraw just this cell
                x1 = col * self.tile_size
                y1 = row * self.tile_size
                x2 = x1 + self.tile_size
                y2 = y1 + self.tile_size
                color = self.texture_colors.get(str(new_val), "gray")
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color,
                                             outline="black", tags=f"cell_{row}_{col}")

    def on_texture_change(self):
        self.current_texture = self.texture_var.get()

    def on_width_change(self, value):
        if not self.grid_data:
            return
        new_width = int(value)
        old_width = len(self.grid_data[0])
        rows = len(self.grid_data)
        for i in range(rows):
            if new_width > old_width:
                # Increase width by appending zeros to each row.
                # This is equivalent to inserting a new column of 0s at the right edge.
                self.grid_data[i].extend([0] * (new_width - old_width))
            elif new_width < old_width:
                # Reduce width by slicing off extra cells from each row.
                self.grid_data[i] = self.grid_data[i][:new_width]
        self.map_data["mapX"] = new_width
        self.draw_grid()

    def on_height_change(self, value):
        if not self.grid_data:
            return
        new_height = int(value)
        old_height = len(self.grid_data)
        cols = len(self.grid_data[0])
        if new_height > old_height:
            # Add new rows (each row is a list of zeros)
            for _ in range(new_height - old_height):
                self.grid_data.append([0] * cols)
        elif new_height < old_height:
            # Remove rows from the bottom
            self.grid_data = self.grid_data[:new_height]
        self.map_data["mapY"] = new_height
        self.draw_grid()

    def on_tile_size_change(self, value):
        self.tile_size = int(value)
        self.map_data["mapS"] = self.tile_size
        self.draw_grid()

    def save_file(self):
        if not self.current_file or not self.map_data:
            return
        # Flatten the 2D grid back to a flat list
        flat_grid = [cell for row in self.grid_data for cell in row]
        self.map_data["grid"] = flat_grid
        # Update dimensions
        self.map_data["mapX"] = len(self.grid_data[0])
        self.map_data["mapY"] = len(self.grid_data)
        self.map_data["mapS"] = self.tile_size

        # Update the colormap: rename "wall" key to "1" if it exists.
        if "colorMap" in self.map_data and "wall" in self.map_data["colorMap"]:
            self.map_data["colorMap"]["1"] = self.map_data["colorMap"].pop("wall")
        try:
            with open(self.current_file, "w") as f:
                json.dump(self.map_data, f, indent=4)
            messagebox.showinfo("Saved", "Map saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

def main():
    root = tk.Tk()
    editor = MapEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
