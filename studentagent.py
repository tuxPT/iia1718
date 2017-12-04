from agent import *
import random,math,sys,collections,pickle

class StudentAgent(Agent):

    def __init__(self, name, body, world):
        super().__init__(name, body, world)
        self.fill_dead_ends() # busca os dead_ends e armazena-os num set juntamente com os pontos do self.world.walls
        self.a = agent()

    def chooseAction(self, vision, msg):
        head = self.body[0]
        validact = self.valid_actions(head, vision)
        food = list(vision.food.keys())
        food.sort(key=lambda x: self.distance(x, head))
        # retorna a ação
        return self.select_search(food, head, vision, validact)
        
    def select_search(self, food, head, vision, validact):
        if food != []:
            parray = [pos for pos in validact if self.distance(pos, food[0]) < self.distance(head, food[0])]
            # vai direto à posição mais próxima do destino
            if parray != [] and not self.a.path_found:
                self.a.path.clear()
                return validact[parray[0]], b""

            # algoritmo de pesquisa a_star
            if not self.a.path_found:
                self.a.path.clear()
                self.a.path_found = self.search(self.a.path, head, food[0], vision)

            if self.a.path_found:
                # evita a utilização de uma deque vazia
                if len(self.a.path) == 1:
                    self.a.path_found = False
                
                pos = self.a.path.popleft()
                if pos in validact.keys():
                    return validact[pos], b""
                else:
                    return Stay, b""

        return Stay, b""

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
                self.find_path(deque, cameFrom, current, start)
                return True
                
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

        return False

    # devolve uma lifo sendo que o ultimo é na verdade a proxima posicao
    def find_path(self, deque,cameFrom, end, start):
        current = end
        while cameFrom[current] != start:
            deque.appendleft(current)
            current = cameFrom[current]

        deque.appendleft(current)

    # devolve um dicionário de pontos para ações
    def valid_actions(self, head, vision):
        validact = {}
        for act in ACTIONS[1:]:
            newpos = self.world.translate(head, act)
            if newpos not in self.dead_ends and newpos not in vision.bodies:
                validact[newpos] = act
        return validact

    def fill_dead_ends(self):
        self.dead_ends = set(self.world.walls.keys())
        pointList= [] # lista de pontos que podem ser percorridos
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
            # porque um dead_end tem sempre 3 paredes e 1 bloco livre
            while len(empty) == 1:
                self.dead_ends.add(nextpos)
                pointList = [i for i in pointList if i not in self.dead_ends]
                nextpos = empty[0]
                neighbors = self.valid_actions(nextpos, vision)
                empty = [i for i in neighbors if i not in self.dead_ends]

class agent:
    def __init__(self):
        self.path = collections.deque()
        self.path_found = False