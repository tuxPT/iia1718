from agent import *
import random,math,sys,collections,pickle

class StudentAgent(Agent):

    def __init__(self, name, body, world):
        super().__init__(name, body, world)
        self.fill_dead_ends()
        self.world.deadZone = self.dead_ends
        self.path_found1 = [False]
        self.path_found2 = [False]
        self.path1 = collections.deque()
        self.path2 = collections.deque()
        self.path = self.path1
        self.path_found = self.path_found1
        self.swap = True

    def chooseAction(self, vision, msg):
        self.switch_agent() 
        print(self.swap)
        print(self.path_found)
        print(self.path)
        head = self.body[0]
        validact = self.valid_actions(head, vision)
        validact[head] = Stay
        food = list(vision.food.keys())
        food.sort(key=lambda x: self.distance(x, head))
        return self.select_search(food, head, vision, validact)
        
    def select_search(self, food, head, vision, validact):
        if food != []:
            parray = [pos for pos in validact if self.distance(pos, food[0]) < self.distance(head, food[0])]
            if parray != []:
                self.path_found[0] = False
                self.path.clear()
                return validact[parray[0]], b""

            if self.path_found[0] == False:
                self.search(self.path, head, food[0], vision)
                self.path_found[0] = True

            if len(self.path) > 0 or self.path_found[0]:
                return validact[self.path.popleft()], b""
            
        self.path_found[0] = False
        return Stay, b""

    def switch_agent(self):
        if self.swap:
            self.path_found = self.path_found1
            self.path = self.path1
            self.swap = False
        else:
            self.path_found = self.path_found2
            self.path = self.path2
            self.swap = True

    def distance(self, head, pos):
        dx = abs(head.x - pos.x)
        dy = abs(head.y - pos.y)
        if dx > self.world.size.x/2:
            dx = self.world.size.x - dx
        if dy > self.world.size.y/2:
            dy = self.world.size.y - dy
        return math.hypot(dx,dy)

    def search(self, deque, start, goal, vision):
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
                return self.find_path(deque, cameFrom, current, start)
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

        deque.clear()
        deque.appendleft(start)

    def find_path(self, deque,cameFrom, end, start):
        deque.clear()
        current = end
        deque.appendleft(current)
        while cameFrom[current] != start:
            current = cameFrom[current]
            deque.appendleft(current)

    def valid_actions(self, head, vision):
        validact = {}
        for act in ACTIONS[1:]:
            newpos = self.world.translate(head, act)
            if newpos not in self.dead_ends and newpos not in vision.bodies:
                validact[newpos] = act
        return validact

    def fill_dead_ends(self):
        self.dead_ends = set(self.world.walls.keys())
        pointList= []
        for x in range(self.world.size.x):
            for y in range(self.world.size.y):
                pointList.append(Point(x,y))
        pointList = [i for i in pointList if i not in self.dead_ends]
        vision = namedtuple('Vision', ['bodies', 'food'])
        vision.bodies = {}
        for pos in pointList:
            neighbors = self.valid_actions(pos, vision)
            empty = [i for i in neighbors if i not in self.dead_ends]
            nextpos = pos
            while len(empty) == 1:
                self.dead_ends.add(nextpos)
                pointList = [i for i in pointList if i not in self.dead_ends]
                nextpos = empty[0]
                neighbors = self.valid_actions(nextpos, vision)
                empty = [i for i in neighbors if i not in self.dead_ends]

