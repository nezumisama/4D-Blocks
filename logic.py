# -*- coding: utf-8-*-
"""This module provides game logic for 4D tetris-like game, with the \"Y\" dimension being the one in which blocks fall."""

import random, copy, operator

class p4d:
    """This class represents a point in 4-dimensional space with color index assigned."""
    def __init__(self, x, y, z, w, col=0):
        """*x*, *y*, *z*, *w* - int - 4D coordinates; *col* - int - color number"""
        self.x = x #: x coordinate
        self.y = y #: y coordinate
        self.z = z #: z coordinate
        self.w = w #: w coordinate
        self.col = col #: color index
    def __iadd__(self, list_):
        """Operator += working with a list of coords [x, y, z, w] on the right hand side."""
        if isinstance(list_, list):
            self.x += list_[0]
            self.y += list_[1]
            self.z += list_[2]
            self.w += list_[3]
        return self
    def __isub__(self, list_):
        """Operator -= working with a list of coords [x, y, z, w] on the right hand side."""
        if isinstance(list_, list):
            self.x -= list_[0]
            self.y -= list_[1]
            self.z -= list_[2]
            self.w -= list_[3]
        return self
    def __sub__(self, list_):
        """Operator - working with a list of coords [x, y, z, w] on the right hand side."""
        if isinstance(list_, list):
            return p4d(self.x-list_[0], self.y-list_[1], self.z-list_[2], self.w-list_[3], self.col)
        return copy.deepcopy(self)
    def __eq__(self, p):
        """Operator == working with a list of coords [x, y, z, w] or another p4d on the right hand side."""
        if isinstance(p, p4d):
            return ((self.x==p.x) and (self.y==p.y) and (self.z==p.z) and (self.w==p.w))
        elif isinstance(p, list):
            return ((self.x==p[0]) and (self.y==p[1]) and (self.z==p[2]) and (self.w==p[3]))
        else: 
            return False
    def __imul__(self, m):
        """Operator *= working with a mat4x4 on the right hand side, sets self = m*self where "*" denotes matrix-vector multiplication.""" 
        if isinstance(m, mat4x4):
            x = self.x
            y = self.y
            z = self.z
            w = self.w
            self.x = m.dat[0][0]*x+m.dat[0][1]*y+m.dat[0][2]*z+m.dat[0][3]*w
            self.y = m.dat[1][0]*x+m.dat[1][1]*y+m.dat[1][2]*z+m.dat[1][3]*w
            self.z = m.dat[2][0]*x+m.dat[2][1]*y+m.dat[2][2]*z+m.dat[2][3]*w
            self.w = m.dat[3][0]*x+m.dat[3][1]*y+m.dat[3][2]*z+m.dat[3][3]*w
        return self
    def __str__(self):
        """Convert to human-readable string."""
        return "[%d, %d, %d, %d]" % (self.x, self.y, self.z, self.w)
class mat4x4:
    """4x4 matrix class"""
    def __init__(self, l):
        """*l* - list of lists; *l[0][0]* is the first element of the first row, *l[2][3]* is the third element of the fourth row etc."""
        self.dat = l
    def __str__(self):
        """Convert to human-readable string."""
        return str(self.dat[0])+"\n"+str(self.dat[1])+"\n"+str(self.dat[2])+"\n"+str(self.dat[3])+"\n"

# rotation direction
CW = 0 #: Clockwise rotation.
CCW = 1 #: Counterclockwise rotation.
# rotation plane
XY = 0 #: Rotation in X-Y plane.
XZ = 1 #: Rotation in X-Z plane.
XW = 2 #: Rotation in X-W plane.
YZ = 3 #: Rotation in Y-Z plane.
YW = 4 #: Rotation in Y-W plane.
ZW = 5 #: Rotation in Z-W plane.

#exceptions
BlkNotFit = Exception("Block does not fit in the domain.") #: Exception thrown when a block doesn't fit the domain in it's initial position.

# Coordinates are defined relative to some point of the block (the one with (0,0,0,0) ).
#
# y
# 
# ^    z
# |  ^
# | / 
# |/
# +----------> x
#  \
#   \
#    +
#      w
#
#: Default blocks set.
defaulf_blocks = [ 
    [p4d(0,0,0,0), p4d(1,0,0,0), p4d(-1,0,0,0), p4d(0,1,0,0)], # T-tetromino
    [p4d(0,0,0,0), p4d(-1,0,0,0), p4d(1,0,0,0), p4d(2,0,0,0)], # I-tetromino
    [p4d(-1,1,0,0), p4d(0,1,0,0), p4d(0,0,0,0), p4d(1,0,0,0)], # Z-tetromino
    [p4d(-1,0,0,0), p4d(0,0,0,0), p4d(0,1,0,0), p4d(1,1,0,0)], # S-tetromino
    [p4d(0,2,0,0), p4d(0,1,0,0), p4d(0,0,0,0), p4d(-1,0,0,0)], # L-tetromino
    #[p4d(0,0,0,0), p4d(0,1,0,0), p4d(0,1,1,0), p4d(0,0,1,0), p4d(0,0,0,1), p4d(0,1,0,1), p4d(0,1,1,1), p4d(0,0,1,1)]
] 

#: 4D rotation matrices for all available 90° rotations in both directions.
rot_mat = [
    mat4x4([[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]), # XY CW
    mat4x4([[0, 1, 0, 0], [-1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]), # XY CCW
    mat4x4([[0, 0, -1, 0], [0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]]), # XZ CW
    mat4x4([[0, 0, 1, 0], [0, 1, 0, 0], [-1, 0, 0, 0], [0, 0, 0, 1]]), # XZ CCW
    mat4x4([[0, 0, 0, -1], [0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0]]), # XW CW
    mat4x4([[0, 0, 0, 1], [0, 1, 0, 0], [0, 0, 1, 0], [-1, 0, 0, 0]]), # XW CCW
    mat4x4([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]]), # YZ CW
    mat4x4([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]]), # YZ CCW
    mat4x4([[1, 0, 0, 0], [0, 0, 0, -1], [0, 0, 1, 0], [0, 1, 0, 0]]), # YW CW
    mat4x4([[1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [0, -1, 0, 0]]), # YW CCW
    mat4x4([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, -1], [0, 0, 1, 0]]), # ZW CW
    mat4x4([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, -1, 0]]), # ZW CCW
]

class logic:
    """This class contains game logic, that is the current game state, 
methods to change this state and state-change rules. It abstracts from the
presentation of the game state."""
    def __init__(self, width, height, depth, w_depth, blocks=defaulf_blocks, num_colors=8):
        """*width*, *height*, *depth*, *w_depth* - int - sizes of the space in 4 dimensions; *blocks* - optional - list of lists of p4d - list of blocks to choose from; *num_colors* - optional - int - number of color indexes to cycle through"""
        self.w, self.h, self.d, self.wd = width, height, depth, w_depth 
        self.space=[]
        self.blocks=blocks #: list of blocks available
        self.num_colors = num_colors
        self.next_col = 0
        self.CheckBlocks()
        self.next_block = copy.deepcopy(random.choice(self.blocks))
        self.blocks_dropped = 0 #: number of blocks dropped
        self.layers_cleared = 0 #: number of layers cleared
        self.score = 0 #: current score
        self.cur_block_offset = [0, 0, 0, 0] #: offset of current block from initial position
        self.NewBlocks()
        self.MovementImpossibleCallback = None
        self.BlockDropedCallback = None
        self.LayersClearedCallback = None
        self.GameOverCallback = None
        self.ScoreFunction = None
    def CheckBlocks(self):
        """Check if all blocks in set fit the domain in their initial position. Throw :py:data:`BlkNotFit` if they don't."""
        for bl in self.blocks:
            xs = [i.x for i in bl]
            ys = [i.y for i in bl]
            zs = [i.z for i in bl]
            ws = [i.w for i in bl]
            if ((max(xs)-min(xs)) >= self.w) or ((max(ys)-min(ys)) >= self.h) or ((max(zs)-min(zs)) >= self.d) or ((max(ws)-min(ws)) >= self.wd):
                raise BlkNotFit
    def ResetBlock(self, block):
        """Move the block *block* to top of the top of the domain. Returns the offset *[x, y, z, w]* from initial block's position to the one it was moved to."""
        xs = [i.x for i in block]
        ys = [i.y for i in block]
        zs = [i.z for i in block]
        ws = [i.w for i in block]
        v = [-min(xs), self.h-max(ys)-1, -min(zs), -min(ws)]
        for i in block: i+=v
        return v 
    def NewBlocks(self):
        """Make next block current and generate a new next one. Execute the **game over callback** if the next block can't be added to the space."""
        self.cur_block_offset = self.ResetBlock(self.next_block)
        self.cur_block = self.next_block
        if self.CheckCollision():
            self.cur_block = [] 
            self.GameOver()
        self.cur_col = self.next_col
        for i in self.cur_block: i.col = self.cur_col
        self.next_block = copy.deepcopy(random.choice(self.blocks)) 
        self.next_col = (self.next_col+1) % self.num_colors
        for i in self.next_block: i.col = self.next_col
    def CheckCollision(self):
        """Check if the current block in current position collides with something. If it collides with the fallen cells, returns True. If it collides with borders, try to move it so it doesn't. If that's successful, return the translation vector *[x, 0, z, w]* (the second element is always 0). If it's not, return True. Finally if no collision is detected, return False."""
        # is the block interfering with the space
        for i in self.cur_block:
            for j in self.space:
                if i==j:
                    return True
        # is the block to high/to low
        ys = [i.y for i in self.cur_block]
        if (min(ys)<0) or (max(ys)>=self.h): return True
        # is the block's position along x, z, w to far/near
        # also see if the block can be moved along these directions
        # to remove the boundary collision
        v=[0,0,0,0]
        # x
        xs = [i.x for i in self.cur_block]
        mi = min(xs)
        ma = max(xs)
        if ma-mi > self.w: return True
        if mi<0: v[0] = -mi
        if ma>=self.w: v[0] = self.w-ma-1
        # z
        zs = [i.z for i in self.cur_block]
        mi = min(zs)
        ma = max(zs)
        if ma-mi > self.d: return True
        if mi<0: v[2] = -mi
        if ma>=self.d: v[2] = self.d-ma-1
        # w
        ws = [i.w for i in self.cur_block]
        mi = min(ws)
        ma = max(ws)
        if ma-mi > self.wd: return True
        if mi<0: v[3] = -mi
        if ma>=self.wd: v[3] = self.wd-ma-1
        if any(v) != 0: return v
        return False
    def GetSpace(self):
        """Return a list of instances of *p4d* representing the parts of space already filled."""
        return self.space
    def GetSpaceWithBlock(self):
        """Return a list of instances of *p4d* representing the parts of space already filled and the elements of the currently falling block."""
        return self.space+self.cur_block
    def GetCurrentBlock(self):
        """Return a list of instances of *p4d* representing elements of the currently falling block."""
        return map(lambda p:p-self.cur_block_offset, self.cur_block)
    def ShadowY(self):
        """Calculate the shadow of the currently falling block and return it as a list of p4ds."""
        if not self.cur_block:
            return []
        tmp = copy.deepcopy(self.cur_block)
        for i in tmp:
            i.y = 0
        tmp.sort()
        last = tmp[-1]
        for i in range(len(tmp)-2, -1, -1):
            if last == tmp[i]:
                del tmp[i]
            else:
                last = tmp[i]
        for i in tmp:
            ys = map(lambda p: p.y, filter(lambda p: p.x==i.x and p.z==i.z and p.w==i.w,self.space)) 
            if ys:
                i.y = max(ys)+1
        return tmp
    def GetNextBlock(self):
        """Return a list of instances of *p4d* representing elements of the next block."""
        return self.next_block
    def Rotate(self, plane, direction):
        """Rotate the current 90° block in the plane of rotation *plane* with direction, if it's possible. If successful, execute the **block rotated callback**. If not, execute the **movement rotated callback**.
        
        Possible values for *plane*: *logic.XY*, *logic.XZ*, *logic.XW*, *logic.YZ*, *logic.YW*, *logic.ZW*
        
        Possible values for *direction*: *logic.CW*, *logic.CCW*"""
        mat = rot_mat[plane*2+direction]
        tmp = copy.deepcopy(self.cur_block)
        for i in self.cur_block:
            i -= self.cur_block_offset
            i *= mat
            i += self.cur_block_offset
        col = self.CheckCollision()
        if type(col)==list:
            col = self.Translate_(col) 
        if col is not False:
            self.cur_block = tmp
            self.MovementImpossible()
        self.BlockRotated()
    def Translate_(self, vector):
        tmp = copy.deepcopy(self.cur_block)
        for i in self.cur_block: i+=vector
        if self.CheckCollision():
            self.cur_block = tmp
            return True
        else:
            self.cur_block_offset = map(operator.add, self.cur_block_offset, vector)
            return False
    def Translate(self, v3d):
        """Translate the current block by the vector *[v3d[0], 0, v3d[1], v3d[2]]* if possible. If not, execute the **movement impossible callback**"""
        v3d.insert(1,0)
        if self.Translate_(v3d):
            self.MovementImpossible()
    def ForceDrop(self):
        """Force the current block to drop immediately to the bottom."""
        while not self.Translate_([0,-1,0,0]):
            pass
    def CheckLayers(self):
        """Check if any 3d layers are cleared, return a list of y-coordinates of such layers."""
        cleared = []
        for i in xrange(self.h):
            clear = True
            layer = filter(lambda p: p.y==i, self.space)
            for x in xrange(self.w):
                for z in xrange(self.d):
                    for w in xrange(self.wd):
                        if p4d(x, i, z, w) not in layer:
                            clear = False
                            break
            if clear: cleared.append(i)
        return cleared
    def AdvanceFall(self):
        """Advance the fall of the current block by one step. If impossible, due to collision with fallen cells, check if any layers were cleared. If some are, execute the **layers cleared callback**. Then recalculate score using the **score function**, call :py:meth:`NewBlocks` and execute the **blocks dropped callback**. Return True if fall was advanced, False if not."""
        if self.Translate_([0,-1,0,0]):
            self.space+=self.cur_block
            cleared = self.CheckLayers()
            num_cleared = len(cleared)
            if num_cleared:
                self.LayersCleared(cleared)
                self.layers_cleared += num_cleared
                self.score += self.ScoreFunc(0, num_cleared)
                self.space = filter(lambda p:p.y not in cleared, self.space)
                while cleared:
                    l = cleared[0]
                    cleared = cleared[1:]
                    cleared = map(lambda x:x-1, cleared)
                    for i in self.space: 
                        if i.y > l: i += [0,-1,0,0]
            self.blocks_dropped += 1
            self.score += self.ScoreFunc(1, 0)
            self.NewBlocks()
            self.BlockDropped() 
            return False
        return True
    def MovementImpossible(self):
        if self.MovementImpossibleCallback: self.MovementImpossibleCallback()
    def SetMovementImpossibleCallback(self, callback):
        """Set *callback* as the **movement impossible callback**; *callback* should take no required arguments and it's return value is ignored."""
        self.MovementImpossibleCallback = callback
    def BlockRotated(self):
        if self.BlockRotatedCallback: self.BlockRotatedCallback()
    def SetBlockRotatedCallback(self, callback):
        """Set *callback* as the **block rotated callback**; *callback* should take no required arguments and it's return value is ignored."""
        self.BlockRotatedCallback = callback        
    def BlockDropped(self):
        if self.BlockDroppedCallback: self.BlockDroppedCallback()
    def SetBlockDroppedCallback(self, callback):
        """Set *callback* as the **block dropped callback**; *callback* should take no required arguments and it's return value is ignored."""
        self.BlockDroppedCallback = callback
    def LayersCleared(self, c):
        if self.LayersClearedCallback: self.LayersClearedCallback(c, self)
    def SetLayersClearedCallback(self, callback):
        """Set *callback* as the **layers cleared callback**; *callback* should take two required arguments. The first one is a list of y-coordinates of cleared layers, the second one is this object. It's return value is ignored."""
        self.LayersClearedCallback = callback
    def GameOver(self):
        if self.GameOverCallback: self.GameOverCallback()
    def SetGameOverCallback(self, callback):
        """Set *callback* as the **game over callback**; *callback* should take no required arguments and it's return value is ignored."""
        self.GameOverCallback = callback
    def ScoreFunc(self, blocks, layers):
        if self.ScoreFunction: 
            score = self.ScoreFunction(blocks, layers)
        else:
            score = blocks*10 + (layers**2)*20
        return score
    def SetScoreFunction(self, f):
        """Set *f* as the **score function**; *f* should take two required arguments. The first one is the blocks dropped increment, the second is the layers cleared increment. It should return score increment according to those two arguments. If no such function is provided, the default score formula will be used: 
        
        score_increment = blocks*10 + (layers**2)*20"""
        self.ScoreFunction = f
