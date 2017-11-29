from agent import *
import random,math,sys,collections,pickle


# This is an example of an agent to play the LongLife game.
# It is not very intelligent: it simply avoids crashing onto walls or bodies.

class StudentAgent(Agent):

    def __init__(self, name, body, world):
        super().__init__(name, body, world)
        self.number = 0
        self.sum = 0
        self.walls = list(self.fill_dead_ends()) + list(self.world.walls.keys())
        #print(self.walls)

    def chooseAction(self, vision, msg):
        head = self.body[0]
        validact = self.valid_actions(head, vision)

        food = list(vision.food.keys())
        food.sort(key=lambda x: self.distance(x, head))
        if food != []:
            pos = self.search_astar(head, food[0], vision)
            if pos in validact.keys():
                return validact[pos], b""
        return Stay, b""

    def distance(self, head, pos):
        dx = abs(head.x - pos.x)
        dy = abs(head.y - pos.y)
        if dx > self.world.size.x/2:
            dx = self.world.size.x - dx
        if dy > self.world.size.y/2:
            dy = self.world.size.y - dy
        return math.hypot(dx,dy)

    def search_astar(self, start, goal, vision):
        closedset = [] # coordenadas visitadas
        openset = [start] # coordenadas por visitar
        cameFrom = {} # dicionario/mapa, dada uma posicao retorna a posicao anterior
        Gdict = collections.defaultdict(lambda: math.inf) # dicionario/mapa, dada uma posicao retorna o custo acumulado
        Fdict = collections.defaultdict(lambda: math.inf) # dicionario/mapa, dada uma posicao retorna o custo estimado(heuristica)
        Gdict[start] = 0
        Fdict[start] = self.distance(start, goal)
        while openset != []:
            current = openset[0]
            if current == goal:
                return self.first_action(cameFrom, current)
            openset.remove(current)
            closedset.append(current)
            validact = self.valid_actions(current, vision).keys()
            neighbors = [pos for pos in validact if pos not in closedset]
            neighbors.sort(key=lambda x: self.distance(x, goal))
            for pos in neighbors:
                if pos not in openset:
                    openset.append(pos)
                gscore = Gdict[current] + self.distance(current,pos)
                if gscore < Gdict[pos]:
                    cameFrom[pos] = current
                    Gdict[pos] = gscore
                    Fdict[pos] = Gdict[pos] +self.distance(current,goal)
        return start

    def first_action(self, cameFrom, current):
        first = current
        second = current
        while first in cameFrom.keys() and cameFrom[first] != first:
            second = first
            first = cameFrom[first]
        return second

    def valid_actions(self, head, vision):
        validact = {}
        for act in ACTIONS[1:]:
            newpos = self.world.translate(head, act)
            if newpos not in self.walls and newpos not in vision.bodies:
                validact[newpos] = act
        return validact

    def fill_dead_ends(self):
        dead_ends = list(self.world.walls.keys())
        translate2 = [Point(1,0), Point(0,1), Point(-1,0), Point(0,-1)]
        i = 0
        end_found = True
        pointList= []
        for x in range(self.world.size.x):
            for y in range(self.world.size.y):
                pointList.append(Point(x,y))
        pointList = [i for i in pointList if i not in dead_ends]
        while end_found == True:
            end_found = False
            for pos in pointList:
                for i in range(3):
                    p1 = self.world.translate(pos, translate2[i%4])
                    p2 = self.world.translate(pos, translate2[(i+1)%4])
                    p3 = self.world.translate(pos, translate2[(i+2)%4])
                    if p1 in dead_ends and p2 in dead_ends and p3 in dead_ends:
                        dead_ends.append(pos)
                        end_found = True
            pointList = [i for i in pointList if i not in dead_ends]
        return dead_ends
