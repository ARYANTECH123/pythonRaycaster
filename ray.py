import tkinter
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from math import radians, sin, cos, tan, sqrt

'''

Raycasting engine, written in python using OpenGl, GLU, and GLUT


'''

# Accesory function
def FixAng(angle):
    a = angle
    if(angle>359):
        a -= 360
    elif(angle<0):
        a += 360
    return a

# The map that player exists in
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

# Map variables
mapS = 64
mapX = 8
mapY = 8

# Draws 2D map
def drawMap2d():

    for y in range(0, mapY):
        for x in range(0 , mapX):
            if(world[y*mapY+x] == 1):
                glColor(1, 1, 1)
            else:
                glColor(0, 0, 0)
            xo, yo = x*mapS, y*mapS
            glBegin(GL_QUADS)
            glVertex(xo+1, yo+1)
            glVertex(xo+1, mapS+yo+1)
            glVertex(mapS+xo-1, mapS+yo-1)
            glVertex(mapS+xo-1, yo+1)
            glEnd()

# Player position variables
px, py, pa, pdx, pdy = 0,0,0,0,0

# Draws 2D player
def drawPlayer2d(px, py, pa, pdx, pdy):
    glColor(1, 1, 0)
    glPointSize(8)
    glLineWidth(4)

    glBegin(GL_POINTS)
    glVertex(px, py)
    glEnd()

    glBegin(GL_LINES)
    glVertex(px, py)
    glVertex(px+20*pdx, py+20*pdy)
    glEnd()

# Handles keyboard input callbacks
def buttons(key, x, y):
    global px, py, pa, pdx, pdy
    if(ord(key) == ord('w')):
        px += pdx*5
        py += pdy*5
    elif(ord(key) == ord('a')):
        pa += 5
        pa = FixAng(pa)
        pdx=cos(radians(pa))
        pdy=-sin(radians(pa))
    elif(ord(key) == ord('d')):
        pa -= 5
        pa = FixAng(pa)
        pdx=cos(radians(pa))
        pdy=-sin(radians(pa))
    elif(ord(key) == ord('s')):
        px -= pdx*5
        py -= pdy*5
    elif(ord(key) == ord('q')):
        px = x
        py = y
    glutPostRedisplay()

# Drawing all the rays
def drawRays2d():
    # Draws sky
    glColor3f(0,1,1)
    glBegin(GL_QUADS)
    glVertex(526,  0)
    glVertex(1006,  0)
    glVertex(1006,160)
    glVertex(526,160)
    glEnd()

    #Draws floor
    glColor3f(0,0,1)
    glBegin(GL_QUADS)
    glVertex2i(526,160)
    glVertex2i(1006,160)
    glVertex2i(1006,320)
    glVertex2i(526,320)
    glEnd()

    #ra is the ray angle
    ra = FixAng(pa + 30)

    for r in range(1, 60): # We are drawing total 60 rays, for a 60 degree field of view

        # Checking vertical wall intercept
        dof, side, disV = 0, 0, 10000

        Tan = tan(radians(ra))
        if(cos(radians(ra)) > 0.001): # Looking leftwards
            rx = ((int(px) >> 6) << 6) + 64 # First x-intercept
            ry = (px - rx)*Tan+py
            xo = 64
            yo = -xo * Tan
        elif(cos(radians(ra)) < -0.001): # Looking rightwards
            rx = ((int(px) >> 6) << 6) - 0.001
            ry = (px - rx)*Tan+py
            xo = -64
            yo = -xo * Tan
        else: # No vertical hit
            rx=px 
            ry=py
            dof=8
        while(dof < 8):
            mx = int(rx) >> 6
            my = int(ry) >> 6
            mp = my*mapX + mx
            if(mp > 0 and mp < mapX*mapY and world[mp] == 1): # Is the intercept a wall?
                dof = 8
                # disV = cos(radians(ra))*(rx-px)-sin(radians(ra))*(ry-py)
                disV = sqrt((px-rx)**2 + (py-ry)**2) # Finding vertical distance
            else: # Else, check next intercept
                rx += xo
                ry += yo
                dof += 1
        vx = rx
        vy = ry

        # Checking Horizontal wall intercept
        dof, disH, Tan = 0, 10000, 1/Tan
        if(sin(radians(ra)) > 0.001): # Looking up
            ry = ((int(py) >> 6) << 6) - 0.0001
            rx = (py-ry)*Tan+px
            yo = -64
            xo = -yo*Tan
        elif(sin(radians(ra)) < -0.001): # Looking down
            ry = ((int(py) >> 6) << 6) + 64
            rx = (py-ry)*Tan+px
            yo = 64
            xo = -yo*Tan
        
        while(dof < 8):
            mx = int(rx) >> 6
            my = int(ry) >> 6
            mp = my*mapX + mx
            if(mp > 0 and mp < mapX*mapY and world[mp] == 1): # Is intercept a wall?
                dof = 8
                # disH = cos(radians(ra)) * (rx-px) - sin(radians(ra))*(ry-py)
                disH = sqrt((px-rx)**2 + (py-ry)**2)
            else: # Now check next intercept
                rx += xo
                ry += yo
                dof += 1
        hx, hy = rx, ry

        if(disV < disH): # If a Vertical wall is hit first
            # print("yes")
            rx, ry = vx, vy
            disH = disV
        else:
            # print("no")
            rx, ry = hx, hy
        
        # Drawing 2D rays
        glColor(0, 0.6, 0)
        glLineWidth(2)
        glBegin(GL_LINES)
        glVertex(px, py)
        glVertex(rx, ry)
        glEnd()

        # Drawing 3D scene
        ca = FixAng(pa - ra) # This is to correct for Fisheye effect, which looks unnatural
        disH = disH*cos(radians(ca))
        lineH = mapS*320/disH
        if(lineH > 320):
            lineH = 320
        lineOff = 160-(lineH // 2)

        glLineWidth(9)
        glBegin(GL_LINES)
        glVertex(r*8+530,lineOff)
        glVertex(r*8+530,lineOff+lineH)
        glEnd()
        # Looping to next ray
        ra = FixAng(ra -1)

# Initializing basic window parameters
def init():
    global px, py, pa, pdx, pdy
    glClearColor(0.3,0.3,0.3,0)
    gluOrtho2D(0,1024,510,0)
    px=150; py=400; pa=90.1
    pdx=cos(radians(pa))
    pdy=-sin(radians(pa))

# Display callback function
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    drawMap2d()
    drawPlayer2d(px, py, pa, pdx, pdy)
    drawRays2d()
    glutSwapBuffers()

# Defining all callbacks and windows.
glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(1024, 510)
glutCreateWindow("pyopengl raycater")
init()
glutDisplayFunc(display)
glutIdleFunc(display)
glutKeyboardFunc(buttons)

glutMainLoop()

