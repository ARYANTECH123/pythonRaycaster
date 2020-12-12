# A Python raycasting engine made in openGL
This ia a simple python raycasting engine made in python.
To run it, you must have Python3 and PyOpenGL.

Python can be installed from the [website](python.org)

To install PyOpenGL, you can go to the [documentaion](http://pyopengl.sourceforge.net/documentation/index.html)

Once both are ready and configured, download or clone `ray.py` and use `python ray.py` to run it.

## Running the code
Once the program starts, you'll  see 2 views : A 2D map with the player and all the rays, and a 3d, raycasted projection. Use WASD to move, and Q to teleport.

## Playing with the code

The algorithm, though it may appear complex, is actually really simple and fast, and hence was used on many classic games like Wolfenstien 3D, to great effect on the limited hardware of the time. If you want to learn more about the algorithm, [this guide is a excellant starting point](https://permadi.com/1996/05/ray-casting-tutorial-1/#INTRODUCTION).

In order to change the map, simploy edit the 64 element long `world` list. it is formatted so thet a `0` is a space and a `1` is a block.

## Screenshots
[img](https://github.com/ARYANTECH123/pythonRaycaster/blob/main/image.png)
