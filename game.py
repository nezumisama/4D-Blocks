# -*- coding: utf-8-*-
"""This module contains the main function of the game."""

import OpenGL, sys, random, numpy, time, pygame, key_num
import logic, input_dev
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.ARB.vertex_buffer_object import *
from ctypes import *
import FTGL, settings
from menu import Menu, _menu, _menu_entry, bool2yn

rotx                    =   0.0             #: rotation around x
roty                    =   0.0             #: rotation around y
panx                    =   0.0             #: panning along x
pany                    =   0.0             #: panning along x
shy_vbo                 =   None            #: vbo for y-shadow
sb_vbo                  =   None            #: vbo for static blocks
og_vbo                  =   None            #: vbo for outer grid
boxes_vbo               =   None            #: vbo for boxes
curr_b_vbo              =   None            #: vbo for current block
next_b_vbo              =   None            #: vbo for next block
boxes_nump              =   0               #: number of points in boxes vbo
og_nump                 =   0               #: number of points in outer grid vbo
shy_nump                =   0               #: number of points in y-shadow vbo
sb_nump                 =   0               #: number of points in static box vbo
curr_b_nump             =   0               #: number of points in current block
next_b_nump             =   0               #: number of points in next block
null                    =   c_void_p(0)     #: null pointer
width                   =   5               #: domain width (x)
depth                   =   5               #: domain depth (z)
height                  =   10              #: domain height (y)
w_depth                 =   2               #: domain size in 4th dimension (w) 
w_spacing               =   4               #: spacing between boxes
mouserot                =   False           #: is mouse rotation active
mousepan                =   False           #: is mouse panning active
mouse_last_x            =   0               #: last mouse click x position
mouse_last_y            =   0               #: last mouse clock y position
zoom                    =   -20             #: zoom
log                     =   None            #: logic instance (:py:class:`logic.logic`)
font                    =   None            #: font object for score
menu_font               =   None            #: font object for menu
win_width               =   640             #: window width
win_height              =   480             #: window height
fps_limit               =   60              #: fps limit
fps                     =   0               #: current fps
clock                   =   None            #: clock instance
xmenu                   =   None            #: in-game menu instance
conf                    =   None            #: settings instance
running                 =   True            #: is game running
turbo                   =   False           #: is turno mode active
menu_mode               =   False           #: are we in menu
bind_mode               =   False           #: are we binding 
game_over_mode          =   False           #: are we showing the game over screen
rot_next_b              =   0.0             #: rotation of next block
sh_stipple              =   (c_uint*32)()   #: polygon stipple pattern for shadows

#: data for one cube (24 points, values mean, in order: x, y, z, r, g, b, a, padding
cube_xyzrgba_data       = numpy.array([[ 0.,  0.,  1.,  0.,  0.,  0.,  0.,  0.],
       [ 0.,  1.,  1.,  0.,  0.,  0.,  0.,  0.],
       [ 1.,  1.,  1.,  0.,  0.,  0.,  0.,  0.],
       [ 1.,  0.,  1.,  0.,  0.,  0.,  0.,  0.],
       [ 1.,  1.,  1.,  0.,  0.,  0.,  0.,  0.],
       [ 1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.],
       [ 1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
       [ 1.,  0.,  1.,  0.,  0.,  0.,  0.,  0.],
       [ 0.,  1.,  0.,  0.,  0.,  0.,  0.,  0.],
       [ 0.,  1.,  1.,  0.,  0.,  0.,  0.,  0.],
       [ 0.,  0.,  1.,  0.,  0.,  0.,  0.,  0.],
       [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
       [ 1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.],
       [ 0.,  1.,  0.,  0.,  0.,  0.,  0.,  0.],
       [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
       [ 1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
       [ 0.,  0.,  1.,  0.,  0.,  0.,  0.,  0.],
       [ 1.,  0.,  1.,  0.,  0.,  0.,  0.,  0.],
       [ 1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
       [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
       [ 0.,  1.,  0.,  0.,  0.,  0.,  0.,  0.],
       [ 1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.],
       [ 1.,  1.,  1.,  0.,  0.,  0.,  0.,  0.],
       [ 0.,  1.,  1.,  0.,  0.,  0.,  0.,  0.]], dtype=numpy.float32)                # data for single cube

colors                  =   [[1,0,0],[0,1,0],[1,1,0],[0,0,1],[1,0,1],[0,1,1]] #: colors for blocks: red green yellow blue magenta cyan
#: maping of GL standard function names to ARB extension ones
gl_func_map_            =   [
    ["glBindBuffer", "glBindBufferARB"],
    ["glBufferData", "glBufferDataARB"],
    ["glBufferSubData", "glBufferSubDataARB"],
    ["glGenBuffers", "glGenBuffersARB"],
    ["glDeleteBuffers", "glDeleteBuffersARB"]
                            ]           
#: mapping of rotation function number to parameters for :py:meth:`logic.logic.Rotate`                           
func2rot = [
                (logic.XY, logic.CW), (logic.XY, logic.CCW),
                (logic.XZ, logic.CW), (logic.XZ, logic.CCW),
                (logic.XW, logic.CW), (logic.XW, logic.CCW),
                (logic.YZ, logic.CW), (logic.YZ, logic.CCW),
                (logic.YW, logic.CW), (logic.YW, logic.CCW),
                (logic.ZW, logic.CW), (logic.ZW, logic.CCW)
]
#: mapping of difficulty level to domain size
difficulty2dim = (
                    (4,14,4,2),
                    (5,10,5,2),
                    (5,10,5,3)
)

def reset_settings():
    """Reset some global variables each this is loaded."""
    global rotx, roty, panx, pany, mouserot, mousepan, xmenu, running
    global shy_vbo, sb_vbo, og_vbo, boxes_vbo, cur_b_vbo, next_b_vbo
    global shy_nump, sb_nump, og_nump, boxes_nump, cur_b_nump, next_b_nump
    global mouse_last_x, mouse_last_y, zoom, log, menu_font, fps, clock, turbo
    global menu_mode, bind_mode, game_over_mode, rot_next_b
    rotx, roty, panx, pany = 0.0, 0.0, 0.0, 0.0
    shy_vbo, sb_vbo, og_vbo = None, None, None
    boxes_vbo, cur_b_vbo, next_b_vbo = None, None, None
    shy_nump, sb_nump, og_nump = 0, 0, 0
    boxes_nump, cur_b_nump, next_b_nump = 0, 0, 0
    mouserot, mousepan, mouse_last_x, mouse_last_y = False, False, 0, 0
    zoom, log, font, menu_font, fps = -20, None, None, None, 0
    clock = pygame.time.Clock()
    xmenu, running, turbo = None, True, False
    menu_mode, bind_mode, game_over_mode = False, False, False
    rot_next_b = 0.0

def gen_stipple():
    """Generate stipple pattern for shadows."""
    global sh_stipple
    for i in xrange(8):
        ii=i*4
        sh_stipple[ii] = sh_stipple[ii+1]   = 0x0C0C0C0C
        sh_stipple[ii+2] = sh_stipple[ii+3] = 0xC0C0C0C0

def gl_func_map():
    """Check if some OpenGL functions are present and if not assign their names to names of functions from ARB extension. This is probably needed on some hardware."""
    global gl_func_map_
    for i in gl_func_map_:
        if not bool(eval(i[0])):
            print "Warning: OpenGL function %s not present, using %s instead." % (i[0], i[1])
            exec("global "+i[0]+"\nglobal "+i[1]+"\n"+i[0]+"="+i[1])

def init_shy():
    """Initialize y-shadow object."""
    global null, width, depth, w_depth, shy_vbo
    shy_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, shy_vbo)
    glBufferData(GL_ARRAY_BUFFER, width*depth*w_depth*128, null, GL_STATIC_DRAW) 
    
def update_shy():
    """Update y-shadow object."""
    global shy_vbo, shy_nump, colors, width, w_spacing, log
    coor = []
    eps = 1e-3
    for i in log.ShadowY():
        col = [j*0.75 for j in colors[i.col]]
        coor.append([i.x+i.w*(width+w_spacing),i.y+eps,i.z,col[0],col[1],col[2],1,0])
        coor.append([i.x+i.w*(width+w_spacing),i.y+eps,i.z+1,col[0],col[1],col[2],1,0])
        coor.append([i.x+i.w*(width+w_spacing)+1,i.y+eps,i.z+1,col[0],col[1],col[2],1,0])
        coor.append([i.x+i.w*(width+w_spacing)+1,i.y+eps,i.z,col[0],col[1],col[2],1,0])
    coords = numpy.array(coor, dtype=numpy.float32)
    glBindBuffer(GL_ARRAY_BUFFER, shy_vbo)
    shy_nump = len(coords)
    glBufferSubData(GL_ARRAY_BUFFER, 0, coords.nbytes, coords)

def draw_shy():
    """Draw y-shadow object."""
    global shy_vbo, shy_nump
    glBindBuffer(GL_ARRAY_BUFFER, shy_vbo)
    glVertexPointer(3, GL_FLOAT, 32, null)
    glColorPointer(4, GL_FLOAT, 32, c_void_p(12))
    glDrawArrays(GL_QUADS, 0, shy_nump)
    
def delete_shy():
    """Destroy y-shadow object."""
    glDeleteBuffers(1,  [shy_vbo])

def init_next_b():
    """Initialize next block object."""
    global null, next_b_vbo, log
    next_b_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, next_b_vbo)
    maxp = max(map(len, log.blocks))
    glBufferData(GL_ARRAY_BUFFER, maxp*768, null, GL_STATIC_DRAW)

def update_next_b():
    """Update next block object."""
    global next_b_vbo, next_b_nump, cube_xyzrgba_data, colors, width, w_spacing, log
    coords = []
    for i in log.GetNextBlock():
        col = colors[i.col]
        coords.append(cube_xyzrgba_data + numpy.array([i.x+i.w*(width+w_spacing),i.y,i.z,col[0],col[1],col[2],1,0], dtype=numpy.float32))
    coords = numpy.array(coords, dtype=numpy.float32)
    delta = numpy.array([numpy.average(coords[...,0]), numpy.average(coords[...,1]), numpy.average(coords[...,2]), 0, 0, 0, 0, 0], dtype=numpy.float32) 
    coords -= delta
    glBindBuffer(GL_ARRAY_BUFFER, next_b_vbo)
    next_b_nump = len(coords)*24
    glBufferSubData(GL_ARRAY_BUFFER, 0, coords.nbytes, coords)
    
def draw_next_b():
    """Draw next block object."""
    global next_b_vbo, next_b_nump
    glBindBuffer(GL_ARRAY_BUFFER, next_b_vbo)
    glVertexPointer(3, GL_FLOAT, 32, null)
    glColorPointer(4, GL_FLOAT, 32, c_void_p(12))
    glDrawArrays(GL_QUADS, 0, next_b_nump)
    
def delete_next_b():
    """Destroy next block object."""
    glDeleteBuffers(1,  [next_b_vbo])

def init_curr_b():
    """Initialize current block object."""
    global null, curr_b_vbo, log
    curr_b_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, curr_b_vbo)
    maxp = max(map(len, log.blocks))
    glBufferData(GL_ARRAY_BUFFER, maxp*768, null, GL_STATIC_DRAW)

def update_curr_b():
    """Update current block object."""
    global curr_b_vbo, curr_b_nump, cube_xyzrgba_data, colors, width, w_spacing, log
    coords = []
    for i in log.GetCurrentBlock():
        col = colors[i.col]
        coords.append(cube_xyzrgba_data + numpy.array([i.x+i.w*(width+w_spacing),i.y,i.z,col[0],col[1],col[2],1,0], dtype=numpy.float32))
    coords = numpy.array(coords, dtype=numpy.float32)
    glBindBuffer(GL_ARRAY_BUFFER, curr_b_vbo)
    curr_b_nump = len(coords)*24
    glBufferSubData(GL_ARRAY_BUFFER, 0, coords.nbytes, coords)
    
def draw_curr_b():
    """Draw current block object."""
    global curr_b_vbo, curr_b_nump
    glBindBuffer(GL_ARRAY_BUFFER, curr_b_vbo)
    glVertexPointer(3, GL_FLOAT, 32, null)
    glColorPointer(4, GL_FLOAT, 32, c_void_p(12))
    glDrawArrays(GL_QUADS, 0, curr_b_nump)
    
def delete_curr_b():
    """Destroy current block object."""
    glDeleteBuffers(1,  [curr_b_vbo])

def init_sblocks():
    """Initialize static blocks object."""
    global null, sb_vbo, width, height, depth, w_depth
    sb_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, sb_vbo)
    glBufferData(GL_ARRAY_BUFFER, width*depth*height*w_depth*768, null, GL_STATIC_DRAW) # 6 faces x 4 verts x (xyzrgba_ = 8) floats x 4 bytes

def update_sblocks():
    """Update static blocks object."""
    global sb_vbo, sb_nump, cube_xyzrgba_data, colors, width, w_spacing, log
    coords = []
    for i in log.GetSpace():
    #for i in log.GetSpaceWithBlock():
        col = colors[i.col]
        coords.append(cube_xyzrgba_data + numpy.array([i.x+i.w*(width+w_spacing),i.y,i.z,col[0],col[1],col[2],1,0],dtype=numpy.float32))
    coords = numpy.array(coords, dtype=numpy.float32)
    glBindBuffer(GL_ARRAY_BUFFER, sb_vbo)
    sb_nump = len(coords)*24
    glBufferSubData(GL_ARRAY_BUFFER, 0, coords.nbytes, coords)
    
def draw_sblocks():
    """Draw static blocks object."""
    global sb_vbo, sb_nump
    glBindBuffer(GL_ARRAY_BUFFER, sb_vbo)
    glVertexPointer(3, GL_FLOAT, 32, null)
    glColorPointer(4, GL_FLOAT, 32, c_void_p(12))
    glDrawArrays(GL_QUADS, 0, sb_nump)

def delete_sblocks():
    """Destroy static blocks object."""
    glDeleteBuffers(1,  [sb_vbo])

def init_outer_grid():
    """Initialize outer grid object."""
    global null, og_vbo, width, height, depth, w_depth, w_spacing, og_nump
    # build coords
    coor = []
    for w in xrange(w_depth):
        x_ = w*(width+w_spacing)
        xx = x_+width
        for x in xrange(x_, xx):
            for y in xrange(0, height):
                coor.append([x,y+1,0])
                coor.append([x+1,y+1,0])
                coor.append([x+1,y,0])
                coor.append([x,y,0])
                coor.append([x,y,depth])
                coor.append([x+1,y,depth])
                coor.append([x+1,y+1,depth])
                coor.append([x,y+1,depth])
        for z in xrange(0, depth):
            for y in xrange(0, height):
                coor.append([x_,y,z])
                coor.append([x_,y,z+1])
                coor.append([x_,y+1,z+1])
                coor.append([x_,y+1,z])
                coor.append([xx,y+1,z])
                coor.append([xx,y+1,z+1])
                coor.append([xx,y,z+1])
                coor.append([xx,y,z])
        for z in xrange(0, depth):
            for x in xrange(x_, xx):
                coor.append([x,0,z])
                coor.append([x+1,0,z])
                coor.append([x+1,0,z+1])
                coor.append([x,0,z+1])
                coor.append([x,height,z+1])
                coor.append([x+1,height,z+1])
                coor.append([x+1,height,z])
                coor.append([x,height,z])

    coords = numpy.array(coor, dtype=numpy.float32)
    og_nump = len(coords)
    og_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, og_vbo)
    glBufferData(GL_ARRAY_BUFFER, og_nump*12, coords, GL_STATIC_DRAW)

def draw_outer_grid():
    """Draw outer grid object."""
    global og_vbo, og_nump
    glBindBuffer(GL_ARRAY_BUFFER, og_vbo)
    glVertexPointer(3, GL_FLOAT, 12, null)
    glDisableClientState(GL_COLOR_ARRAY)
    glDrawArrays(GL_QUADS, 0, og_nump)
    glEnableClientState(GL_COLOR_ARRAY)

def delete_outer_grid():
    """Destroy outer grid object."""
    glDeleteBuffers(1,  [og_vbo])

def set_fonts_sizes():
    """Set sizes of font objects according to current window size."""
    global font, menu_font, win_width, win_height
    font.FaceSize(int(win_height*0.04))
    menu_font.FaceSize(int(win_height*0.04))

def init_font():
    """Initialize fiot objects."""
    global font, menu_font
    font = FTGL.PixmapFont(conf.get("font_filename"))
    menu_font = FTGL.PixmapFont(conf.get("menu_font_filename"))
    set_fonts_sizes()

def set_speed():
    """Set time between block fall steps according to the **speed** setting and **turbo mode**."""
    global conf, turbo
    dt = settings.speed2dt(conf.get("speed"))
    if turbo:
        dt/=4
    pygame.time.set_timer(pygame.USEREVENT, dt)
    
def draw_font():
    """Draw text with score and other info."""
    global font, win_width, win_height, log, null, fps, conf
    line_w = font.line_height*0.5+5
    tmp = font.BBox("Layers cleared: 1000")
    max_w = tmp[3]-tmp[0]
    glColor4f(0.6, 0.6, 1.0, 1.0)
    glWindowPos2f(win_width-max_w, win_height-line_w-10)
    if conf.get("show_fps"):
        font.Render("FPS: %.0f" % fps)
        glBitmap(0, 0, 0, 0, 0, -line_w, null)
    font.Render("Score: %d" % log.score)
    glBitmap(0, 0, 0, 0, 0, -line_w, null)
    font.Render("Layers cleared: %d" % log.layers_cleared)
    glBitmap(0, 0, 0, 0, 0, -line_w, null)
    font.Render("Next: ")

def gl_init():
    """Save OpenGL state (to later restore it) and initialize OpenGL state for this game."""
    global width, height, depth, w_depth
    glPushAttrib(GL_ALL_ATTRIB_BITS)
    glPushClientAttrib(GL_CLIENT_ALL_ATTRIB_BITS)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glEnable(GL_BLEND)
    glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glClearDepth(1.0)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)
    init_outer_grid()
    init_sblocks()
    init_next_b()
    init_curr_b()
    init_shy()
    init_font()
    gen_stipple()
    glPolygonStipple(sh_stipple)

def draw_game_over():
    """Draw game over screen."""
    global menu_font, win_width, win_height, log
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glPushMatrix()
    glLoadIdentity()
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glColor4f(0.0, 0.0, 0.0, 0.7)
    glBegin(GL_QUADS)
    glVertex2f(-1.0, -1.0)
    glVertex2f(1.0, -1.0)
    glVertex2f(1.0, 1.0)
    glVertex2f(-1.0, 1.0)
    glEnd()
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glColor4f(1.0, 1.0, 1.0, 1.0)
    line_w = menu_font.line_height*0.5+5
    x, y = win_width*0.05, win_height*0.5+line_w*2.5
    glWindowPos2f(x, y)
    menu_font.Render("GAME OVER")
    glWindowPos2f(x, y-2*line_w)
    menu_font.Render("Score: %d" % log.score)
    glWindowPos2f(x, y-3*line_w)
    menu_font.Render("Layers cleared: %d" % log.layers_cleared)
    glWindowPos2f(x, y-4*line_w)
    menu_font.Render("Press Esc to continue")

def draw_menu():
    """Draw in-game menu."""
    global menu_font, win_width, win_height, xmenu
    highlighted = xmenu.selected
    text = xmenu.get_options_list()
    text_w = [(menu_font.BBox(i[0]), menu_font.BBox(i[1])) for i in text]
    text_w = [(i[0][3]-i[0][0], i[1][3]-i[1][0]) for i in text_w]
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glPushMatrix()
    glLoadIdentity()
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glColor4f(0.0, 0.0, 0.0, 0.7)
    glBegin(GL_QUADS)
    glVertex2f(-1.0, -1.0)
    glVertex2f(1.0, -1.0)
    glVertex2f(1.0, 1.0)
    glVertex2f(-1.0, 1.0)
    glEnd()
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    line_w = menu_font.line_height*0.5+5
    x = win_width*0.05
    y = win_height*0.5+line_w*(len(text))*0.5
    for i in xrange(len(text)):
        delta = win_width*0.7-text_w[i][1]
        if i == highlighted:
            glColor4f(1.0, 1.0, 1.0, 1.0)
        else:
            glColor4f(1.0, 1.0, 0.5, 1.0)
        glWindowPos2f(x, y-line_w*i)
        menu_font.Render(text[i][0])
        glWindowPos2f(delta, y-line_w*i)
        menu_font.Render(text[i][1])

def draw_curr_b_():
    """Draw current block at the right position."""
    global log, width, w_spacing
    glPushMatrix()
    off = log.cur_block_offset
    glTranslatef(off[0]+off[3]*(width+w_spacing), off[1], off[2])
    draw_curr_b()
    glPopMatrix()

def draw_next_b_():
    """Draw next block at the right position."""
    global win_width, win_height, zoom, rot_next_b 
    aspect = win_width*1.0/win_height
    #scale = win_height*0.0005
    scale = 0.5
    glPushMatrix()
    glLoadIdentity()
    glTranslatef(10*aspect, 6, zoom)
    glRotatef(rot_next_b, 0.0, 1.0, 0.0)
    glScalef(scale, scale, scale)
    draw_next_b()
    glPopMatrix()
    
def display():
    """Main display call, draws everything needed."""
    global rotz, roty, panx, pany, zoom, log, menu_mode, rot_next_b
    update_shy()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0, 0, zoom)
    glRotatef(rotx, 1.0, 0.0, 0.0)
    glRotatef(roty, 0.0, 1.0, 0.0)
    glTranslatef(panx, pany, 0)
    glTranslatef(-0.5*(w_depth*width+(w_depth-1)*w_spacing), height*(-0.5), depth*(-0.5))
    glCullFace(GL_BACK)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    draw_sblocks()
    draw_curr_b_()
    if not (menu_mode or game_over_mode):
        draw_next_b_()
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glLineWidth(3.0)
    glColor3f(1,1,1)
    glDisableClientState(GL_COLOR_ARRAY)
    draw_sblocks()
    draw_curr_b_()
    if not (menu_mode or game_over_mode):
        glLineWidth(1.5)
        draw_next_b_()
    glEnableClientState(GL_COLOR_ARRAY)
    glLineWidth(1.0)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glEnable(GL_POLYGON_STIPPLE)
    draw_shy()
    glDisable(GL_POLYGON_STIPPLE)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glCullFace(GL_FRONT)
    glColor4f(1.0, 1.0, 1.0, 1.0)
    draw_outer_grid()
    glCullFace(GL_BACK)
    glColor4f(1.0, 1.0, 1.0, 0.2)
    draw_outer_grid()    
    if menu_mode: 
        draw_menu()
    else:
        if game_over_mode:
            draw_game_over()
        else:
            draw_font()
            rot_next_b += 1
    pygame.display.flip()

def reshape (w, h):
    """React to window geometry change, *w* is new width, *h* is new height."""
    aspect = w*1.0 / h
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, aspect, 1.0, 1000.0)
    #scale = 10.0
    #glOrtho(-aspect*scale, aspect*scale, -scale, scale, -scale, scale)
    glMatrixMode(GL_MODELVIEW)

def gameover():
    """Callback executed by :py:data:`log` on game over."""
    global game_over_mode
    #pygame.event.post(pygame.event.Event(pygame.QUIT))
    print "game over"
    game_over_mode = True

def block_dropped():
    """Callback executed by :py:data:`log` when block was dropped, updates objects: current block, next block and static blocks."""
    update_curr_b()
    update_next_b()
    update_sblocks()

def block_rotated():
    """Callback executed by :py:data:`log` when block is rotated in 4D, updates current block object."""
    update_curr_b()

def set_mode(w, h):
    """Set display mode with window width *w* and height *h*"""
    pygame.display.set_mode((w, h), pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)

def exit_2_os():
    """Exit to OS."""
    exit(0)

# menu callbacks
def menu_cbck_resume(index, conf):
    """Menu callback executed when menu option **resume** is selected; *index* is index of the current position in current submenu, *conf* is the settings object (instance of :py:class:`settings.Settings`); *conf_* from :py:func:`main` will be given here."""
    global menu_mode
    menu_mode = False
def menu_cbck_exit2os(index, conf):
    """Menu callback executed when menu option **exit to os** is selected. Arguments mean the same as in :py:func:`menu_cbck_resume`."""
    pygame.event.post(pygame.event.Event(pygame.QUIT))
def menu_cbck_exit2menu(index, conf):
    """Menu callback executed when menu option **exit to menu** is selected. Arguments mean the same as in :py:func:`menu_cbck_resume`."""
    global running
    running = False
def menu_cbck_misc_reset(index, conf):
    """Submenu **misc** reset callback. Arguments mean the same as in :py:func:`menu_cbck_resume`."""
    if index == 0:
        return bool2yn(conf.get("show_fps"))
    elif index == 1:
        return str(conf.get("speed"))
def menu_cbck_misc_enter(index, conf):
    """Submenu **misc** enter/selection callback. Arguments mean the same as in :py:func:`menu_cbck_resume`."""
    if index == 0:
        tmp = not conf.get("show_fps")
        conf.set("show_fps", tmp)
        return bool2yn(tmp)
def menu_cbck_misc_inc(index, conf):
    """Submenu **misc** incrementation callback. Arguments mean the same as in :py:func:`menu_cbck_resume`."""
    if index == 0:
        tmp = not conf.get("show_fps")
        conf.set("show_fps", tmp)
        return bool2yn(tmp)
    elif index == 1:
        tmp = conf.get("speed")
        if tmp<9:
            tmp+=1
        conf.set("speed", tmp)
        set_speed()
        return str(tmp)
def menu_cbck_misc_dec(index, conf):
    """Submenu **misc** decrementation callback. Arguments mean the same as in :py:func:`menu_cbck_resume`."""
    if index == 0:
        tmp = not conf.get("show_fps")
        conf.set("show_fps", tmp)
        return bool2yn(tmp)
    elif index == 1:
        tmp = conf.get("speed")
        if tmp>1:
            tmp-=1
        conf.set("speed", tmp)
        set_speed()
        return str(tmp)
def menu_cbck_controls_reset(index, conf):
    """Submenu **controls** reset callback. Arguments mean the same as in :py:func:`menu_cbck_resume`."""
    return conf.get("key_bindings").f_to_str(index)
def menu_cbck_controls_enter(index, conf):
    """Submenu **controls** enter/selection callback. Arguments mean the same as in :py:func:`menu_cbck_resume`."""
    global xmenu
    xmenu.current[index].val = "<press key combo to bind to>"
    bind_mode = True
    conf.get("key_bindings").wait_and_bind(index, timer_evt_id=2, dt=10, timeout=100, loop_callback=display, quit_callback=exit_2_os, neutral_key=pygame.K_ESCAPE)
    return conf.get("key_bindings").f_to_str(index)
def menu_cbck_save(index, conf):
    """Menu callback executed when menu option **save** is selected. Arguments mean the same as in :py:func:`menu_cbck_resume`."""
    conf.save()

def menu_cbck_reset(index, conf):
    """Menu callback executed when menu option **reset** is selected. Arguments mean the same as in :py:func:`menu_cbck_resume`."""
    global xmenu
    conf.reset()
    xmenu.update_values()
    conf.get("key_bindings").input_state.setup_joys()

def execute_triggered(triggered):
    """Execute function numbers from the list *triggered*."""
    global log, menu_mode
    if   key_num.KEY_MENU in triggered: menu_mode = not menu_mode
    elif key_num.KEY_MOV_UP in triggered: log.Translate([0,-1,0])
    elif key_num.KEY_MOV_DOWN in triggered: log.Translate([0,1,0])
    elif key_num.KEY_MOV_LEFT in triggered: log.Translate([-1,0,0])
    elif key_num.KEY_MOV_RIGHT in triggered: log.Translate([1,0,0])
    elif key_num.KEY_MOV_LEFT_W in triggered: log.Translate([0,0,-1])
    elif key_num.KEY_MOV_RIGHT_W in triggered: log.Translate([0,0,1])  
    elif key_num.KEY_FORCE_DROP in triggered:
        log.ForceDrop()
        log.AdvanceFall()
    for i in triggered:
        if i>=key_num.KEY_ROT_XY_CW and i<=key_num.KEY_ROT_ZW_CCW:
            log.Rotate(*func2rot[i-key_num.KEY_ROT_XY_CW])

def remove_list(l1, l2):
    """Remove from list *l1* elements which are in list *l2*."""
    return list(set(l1)-set(l2))

def unload():
    """Uninitialize all objects and restore OpenGL state saved in :py:func:`gl_init`."""
    delete_curr_b()
    delete_next_b()
    delete_outer_grid()
    delete_sblocks()
    delete_shy()
    glPopAttrib(GL_ALL_ATTRIB_BITS)
    glPopClientAttrib(GL_CLIENT_ALL_ATTRIB_BITS)
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    print "UNLOADED"

def main(conf_, difficulty):
    """Main function. This should be called to start the game. Arguments: *conf_* is settings, instance of :py:class:`settings.Settings`; *difficulty* - int between 0 and 2 (inclusive) - difficulty level (0 easy, 1 normal, 2 hard)."""
    global win_width, win_height, width, height, depth, w_depth, fps, fps_limit, log, conf, panx, pany, turbo, running
    global mouserot, mousepan, mouse_last_x, mouse_last_y, rotx, roty, zoom, menu_mode, xmenu, colors
    conf = conf_
    reset_settings()
    # reset input state
    conf.get("key_bindings").input_state.reset()
    width, height, depth, w_depth = difficulty2dim[difficulty]
    gl_func_map()
    #pygame.init()
    pygame.joystick.init()
    conf.get("key_bindings").input_state.setup_joys()
    #set_mode(win_width, win_height)
    #pygame.display.set_caption("Blockout4D test")
    surf = pygame.display.get_surface()
    win_width, win_height = surf.get_size()
    pygame.event.post(pygame.event.Event(pygame.VIDEORESIZE, size=(win_width, win_height), w=win_width, h=win_height))
    log = logic.logic(width, height, depth, w_depth, num_colors=len(colors))
    log.SetGameOverCallback(gameover)
    log.SetBlockDroppedCallback(block_dropped)
    log.SetBlockRotatedCallback(block_rotated)
    gl_init()
    block_dropped()
    set_speed()
    pygame.time.set_timer(pygame.USEREVENT+1, 200)
    menu_layout = _menu("*", [
        _menu_entry("resume", None, menu_cbck_resume, None, None),
        _menu_entry("exit to os", None, menu_cbck_exit2os, None, None),
        _menu_entry("exit to menu", None, menu_cbck_exit2menu, None, None),
        _menu("settings", [
            _menu("misc", [
                _menu_entry("show fps", menu_cbck_misc_reset, menu_cbck_misc_enter, menu_cbck_misc_inc, menu_cbck_misc_dec),
                _menu_entry("speed", menu_cbck_misc_reset, None, menu_cbck_misc_inc, menu_cbck_misc_dec),
            ]),
            _menu("controls", [_menu_entry(i, menu_cbck_controls_reset, menu_cbck_controls_enter, None, None) for i in key_num.labels]),
            _menu_entry("save", None, menu_cbck_save, None, None),
            _menu_entry("reset", None, menu_cbck_reset, None, None)
        ])
    ])
    xmenu = Menu(menu_layout, conf)
    triggered_hold = []
    triggered_once = []
    triggered_timestamp = {}
    triggered_backoff = 300
    triggered_norepeat = [20]
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: 
                exit_2_os()
            elif ev.type == pygame.VIDEORESIZE:
                win_width, win_height = ev.w, ev.h
                print "Resizing to %d x %d" % (win_width, win_height)
                set_mode(win_width, win_height)                
                reshape(win_width, win_height)
                set_fonts_sizes()
            else:
                if game_over_mode:
                    if ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_ESCAPE:
                            running = False
                else:
                    if menu_mode: # we're in menu
                        if ev.type == pygame.KEYDOWN:
                            if ev.key == pygame.K_ESCAPE:
                                if xmenu.path:  
                                    xmenu.escape()
                                else:
                                    menu_mode = False 
                                    conf.get("key_bindings").input_state.reset()                  
                            elif ev.key == pygame.K_UP:
                                xmenu.up()
                            elif ev.key == pygame.K_DOWN:
                                xmenu.down()
                            elif ev.key == pygame.K_LEFT:
                                xmenu.left()
                            elif ev.key == pygame.K_RIGHT:
                                xmenu.right()
                            elif ev.key == pygame.K_RETURN:
                                xmenu.enter()
                    else: # we're not in menu
                        conf.get("key_bindings").input_state.process_event(ev)
                        triggered = conf.get("key_bindings").get_triggered()
                        tmp = turbo
                        turbo = (key_num.KEY_TURBO in triggered)
                        if turbo!=tmp: 
                            set_speed()
                            log.AdvanceFall()
                        triggered_new = remove_list(triggered, triggered_once)
                        for i in triggered_new: triggered_timestamp[i] = pygame.time.get_ticks()
                        execute_triggered(triggered_new)
                        if ev.type == pygame.USEREVENT+1:
                            t=pygame.time.get_ticks()
                            execute_triggered(filter(lambda x: (t-triggered_timestamp[x])>triggered_backoff, triggered_once))
                        triggered_once = remove_list(triggered, triggered_norepeat)
                        if ev.type == pygame.USEREVENT:
                            log.AdvanceFall()
                        """
                        elif ev.type == pygame.KEYDOWN:
                            print "Key press: ", ev
                            if ev.key == pygame.K_ESCAPE:                     
                                menu_mode = True
                        """
                        if ev.type == pygame.MOUSEBUTTONDOWN:
                            if ev.button == 1:
                                mouserot = True
                                mouse_last_x = ev.pos[0]
                                mouse_last_y = ev.pos[1]
                            elif ev.button == 3:
                                mousepan = True
                                mouse_last_x = ev.pos[0]
                                mouse_last_y = ev.pos[1]
                            elif ev.button == 4: # scroll up
                                zoom += 0.5
                            elif ev.button == 5: # scroll down
                                zoom -= 0.5 
                        elif ev.type == pygame.MOUSEBUTTONUP:
                            if ev.button == 1:
                                mouserot = False
                            elif ev.button == 3:
                                mousepan = False
                        elif ev.type == pygame.MOUSEMOTION:
                                x, y = ev.pos
                                if mouserot:
                                    roty += (x-mouse_last_x)*0.3
                                    rotx += (y-mouse_last_y)*0.3
                                    mouse_last_x = x
                                    mouse_last_y = y
                                elif mousepan:
                                    panx -= (x-mouse_last_x)*0.005*zoom
                                    pany += (y-mouse_last_y)*0.005*zoom
                                    mouse_last_x = x
                                    mouse_last_y = y
        display()
        clock.tick(fps_limit)
        fps = clock.get_fps()
    unload()
    return
