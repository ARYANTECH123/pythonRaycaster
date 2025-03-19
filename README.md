# Raycaster2

This is a python raycasting game based on 8KSpaceInvader's  [pythonRaycaster](https://github.com/ARYANTECH123/pythonRaycaster)

I've transformed it using OOP to make a multiplayer server/client based game.

I'm not yet sure what to do as game content, anything is possible from there, i'm thinking of a co-op maze game.

# Installation

To run it, you must have Python3 and PyOpenGL.

Python can be installed from the [website](python.org)

To install PyOpenGL, you can go to the [documentaion](http://pyopengl.sourceforge.net/documentation/index.html)


# Running the game

Once both are ready and configured, download or clone the project and run the server (`python3 server_network.py`) and then a client (`python3 main.py`).

Once the program starts, you'll  see 2 views : A 2D map with the player, and a 3d, raycasted projection.

Use ZQSD to move (I'm using a french azerty keyboard, sorry, I'll later use automatic detection of key layout and/or easy keybindings ui).

You can run as many clients as you wish. Other clients will render on the minimap as a green dot.

## About Raycasting

The algorithm, though it may appear complex, is actually really simple and fast, and hence was used on many classic games like Wolfenstien 3D, to great effect on the limited hardware of the time.

It consists of shooting rays from the camera until they intersect an object; and then draw a vertical line on the screen depending on the distance reached by the ray. This results

If you want to learn more about the algorithm, [this guide is a excellent starting point](https://permadi.com/1996/05/ray-casting-tutorial-1/#INTRODUCTION).

## Future additions

You can see planned additions in the [TODO](./TODO) file.
Currently I plan on making
- UI for map management/edition and key bindings
- Map generation (maybe mazelik/terrainlike)
- Game mechanics (not yet determined)
- Improve graphics
  - Directional light source (N/S/W/E)
  - Lighting depends on distance

## Screenshots
![8kSpaceInvader's old version](https://github.com/ARYANTECH123/pythonRaycaster/blob/main/image.png)

![My version (IMAGE TO COME)]()
