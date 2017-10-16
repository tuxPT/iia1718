

from collections import namedtuple
from collections import ChainMap
import random
import logging

from constants import *

# Point is a tuple for coordinates inside a 2D world
class Point(namedtuple("Point", ['x', 'y'])):
    __slots__ = ()

    def __add__(self, other):
        return Point(self.x+other[0], self.y+other[1])
    
    def __sub__(self, other):
        return Point(self.x-other[0], self.y-other[1])
    
    def __abs__(self):
        return abs(self.x) + abs(self.y)


# A World object contains a view of the world.
# This includes:
# size,
# walls, bodies, food
    
class World:
    
    def __init__(self, size):
        self.size = size
        self.walls = {}
        self.food = {}
        self.bodies = {}
        self.cells = ChainMap(self.bodies, self.food, self.walls)
        
        self.foodfield = []
        self.playerfield = []
        
    
    def put(self, pos, cell):
        assert isinstance(pos, Point)
        pos = self.normalize(pos)
        if cell in WALL:
            self.walls[pos] = cell
        elif cell in FOODTYPES:
            self.food[pos] = cell
        else:
            self.bodies[pos] = cell
    
    def get(self, pos):
        return self.cells[pos]
    
    # Functions to manipulate points and coords in the world
    def normalize(self, p):
        """Return a normalized point. (Wrap coords inside world.)"""
        return Point(p[0]%self.size.x, p[1]%self.size.y)
    
    def point(self, x, y):
        p = (x, y)
        return self.normalize(p)
    
    def dist(self, p1, p2):
        """Distance between points in this world."""
        d = p2-p1
        return min(d.x, self.size.x-d.x) + min(d.y, self.size.y-d.y)
    
    def translate(self, p, d):
        """Point obtained by adding vector d to point p."""
        p = self.normalize(p)   # may be removed if isinstance(p, Point)
        return self.normalize(p+d)

    def randPoint(self):
        """Return a random point in this world."""
        return Point(random.randrange(0,self.size.x), random.randrange(0,self.size.y))

    def generatePos(self, forbiden={}, preferred={}):
        """Generate a position guaranteed not to be in forbiden.
        Chosen randomly from the preferred positions, or from the full range.
        """
        preflist = [p for p in preferred if p not in forbiden]
        if len(preflist) > 0:
            pos = random.choice(preflist)
        else:
            while True:
                pos = self.randPoint()
                if pos not in forbiden: break
        assert pos not in forbiden
        return pos

    def generatePlayerBody(self, t):
        body = []
        while True: ## TODO: possibility of infinite loop?
            body.append(self.generatePos(forbiden=self.cells, preferred=self.playerfield))
            neighboors = [self.translate(body[0],d) for d in DIRECTIONS[:-1]]
            body.append(self.generatePos(forbiden=self.cells, preferred=neighboors))
            if len(body)==2: break
        for p in body: self.put(p, t)
        #pos = self.generatePos(forbiden=self.cells, preferred=self.playerfield)
        #self.bodies[pos] = t
        return body

    def generateFood(self, t):
        pos = self.generatePos(forbiden=self.cells, preferred=self.foodfield)
        self.food[pos] = t
        return pos
    
    def moveFood(self):
        currentpos = self.food.keys()
        for f in currentpos:
            if self.food[f] == 'M':
                neighbours = [self.translate(f, d) for d in DIRECTIONS]
                t = self.food.pop(f)
                pos = self.generatePos(forbiden=self.cells, preferred=neighbours)
                self.food[pos] = t
    
    def loadField(self, pxarray):
        for x in range(len(pxarray)):
            for y in range(len(pxarray[x])):
                p = pxarray[x][y] & 0xFFFFFFFF #fix signed/unsigned
                if p == 0xFF000000:
                    p = 0xAA7942
                if p == 0:
                    p = 0xFFFFFF
                p = p & 0xFFFFFF
                if not p in [0x00F900, 0xFF2600, 0xAA7942, 0x000000, 0xFFFFFF, 0]: #food, player, wall, oldwall, empty, oldempty 
                    logging.error("UNKNOWN: {:02X}".format(p))
                if p == 0x00F900:
                    self.foodfield.append(Point(x,y))
                elif p == 0xFF2600:
                    self.playerfield.append(Point(x,y))
                elif p == 0xAA7942: 
                    self.walls[Point(x, y)] = WALL

    def generateWalls(self, level):
        for i in range(1,level+1):
            lo = self.randPoint() #last wall
            self.walls[lo] = WALL
            for j in range(1,random.randint(1,level)):
                d = random.choice(DIRECTIONS[1:3])
                lo = self.translate(lo, d)
                self.walls[lo] = WALL

## Testing the module:
if __name__ == "__main__":
    w = World(Point(10,10))
    p = w.point(1,2)
    q = w.point(13, 14)
    print(p, q, w.translate(p, (+1,-1)), w.dist(p, q))
