from agent import *
import random,math,sys,collections,pickle,heapq

class StudentAgent(Agent):

    def __init__(self, name, body, world):
        super().__init__(name, body, world)
        self.fill_dead_ends() # busca os dead_ends e armazena-os num set juntamente com os pontos do self.world.walls
        self.path = collections.deque()

    def chooseAction(self, vision, msg):
        head = self.body[0]
        bodies = vision.bodies
        validact = self.valid_actions(head, bodies)
        food = list(vision.food.keys())
        food.sort(key=lambda x: self.distance(x, head))
        if food:
            direct_food = [pos for pos in food if not self.path_needed(head, pos, bodies)]
            if direct_food:
                nextpos = [pos for pos in validact if self.distance(pos, direct_food[0]) < self.distance(head, direct_food[0])]
                return validact[nextpos[0]], b""

            else:
                new_path = self.search(head, food[0], bodies)
                if self.path:
                    nextpos = self.path.pop()
                    self.path.append(nextpos)
                    if nextpos not in validact:
                        goal = self.path.popleft()
                        self.path.appendleft(goal)
                        self.path = self.search(head, goal, bodies)
                    
                    if new_path:
                        self.path = self.shortest_path(new_path, self.path)
                elif new_path:
                        self.path = new_path
                else:
                    return Stay, b""
                if self.path:
                    nextpos = self.path.pop()
                    return validact[nextpos], b""
                
                return Stay, b""
        else:
            if self.path:
                nextpos = self.path.pop()
                self.path.append(nextpos)
                if nextpos not in validact:
                    goal = self.path.popleft()
                    self.path.appendleft(goal)
                    self.path = self.search(head, goal, bodies)

                if self.path:
                    nextpos = self.path.pop()
                    return validact[nextpos], b""
                
            return Stay, b""
        
    # verifica se é necessário um path para chegar á posição
    def path_needed(self, start, goal, bodies):
        head = start
        distance = self.distance(head, goal)
        while head != goal:
            validact = self.valid_actions(head, bodies)
            nextpos = [pos for pos in validact if self.distance(pos, goal) < distance]
            if nextpos:
                head = nextpos[0]
                distance = self.distance(head, goal)
            else:
                return True
        
        return False

    # retorna o path mais curto
    def shortest_path(self, path1, path2):
        if len(path1) < len(path2):
            return path1
        else:
            return path2


    # menor distância entre dois pontos num plano toroidal
    def distance(self, head, pos):
        dx = abs(head.x - pos.x)
        dy = abs(head.y - pos.y)
        if dx > self.world.size.x/2:
            dx = self.world.size.x - dx
        if dy > self.world.size.y/2:
            dy = self.world.size.y - dy
        return math.hypot(dx,dy)

    # Search A_Star com dicionários
    def search(self, start, goal, bodies):
        closedset = [] # coordenadas visitadas
        openset = [start] # coordenadas por visitar
        cameFrom = {} # dicionario/mapa, dada uma posicao retorna a posicao anterior
        Gdict = collections.defaultdict(lambda: math.inf) # dicionario/mapa, dada uma posicao retorna o custo acumulado
        Fdict = collections.defaultdict(lambda: math.inf) # dicionario/mapa, dada uma posicao retorna o custo estimado(heuristica)
        Gdict[start] = 0
        Fdict[start] = self.distance(start, goal)
        while openset != []:
            current = openset[0]
            if current == goal and current != start:
                return self.find_path(cameFrom, current, start)
                
            openset.remove(current)
            closedset.append(current)
            validact = self.valid_actions(current, bodies).keys()
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

        return collections.deque()

    # devolve uma lifo sendo que o ultimo é na verdade a proxima posicao
    def find_path(self, cameFrom, end, start):
        current = end
        deque = collections.deque()
        deque.append(current)
        while current in cameFrom and cameFrom[current] != start:
            current = cameFrom[current]
            deque.append(current)

        return deque

    # devolve um dicionário de pontos para ações
    def valid_actions(self, head, bodies):
        validact = {}
        for act in ACTIONS[1:]:
            newpos = self.world.translate(head, act)
            if newpos not in self.dead_ends and newpos not in bodies:
                validact[newpos] = act
        return validact

    def fill_dead_ends(self):
        self.dead_ends = set(self.world.walls.keys())
        pointList= [] # lista de pontos que podem ser percorridos
        for x in range(self.world.size.x):
            for y in range(self.world.size.y):
                pointList.append(Point(x,y))
        pointList = [i for i in pointList if i not in self.dead_ends]
        bodies = {}
        for pos in pointList:
            neighbors = self.valid_actions(pos, bodies)
            empty = [i for i in neighbors if i not in self.dead_ends]
            nextpos = pos
            # porque um dead_end tem sempre 3 paredes e 1 bloco livre
            while len(empty) == 1:
                self.dead_ends.add(nextpos)
                pointList = [i for i in pointList if i not in self.dead_ends]
                nextpos = empty[0]
                neighbors = self.valid_actions(nextpos, bodies)
                empty = [i for i in neighbors if i not in self.dead_ends]