from agent import *
import random,math,sys,collections,pickle,heapq

class StudentAgent(Agent):

    def __init__(self, name, body, world):
        super().__init__(name, body, world)
        self.fill_dead_ends() # busca os dead_ends e armazena-os num set juntamente com os pontos do self.world.walls
        self.path = collections.deque()
        self.waypoints = self.find_waypoints()
        self.debug_dead_ends = [pos for pos in self.dead_ends if pos not in self.world.walls]
        self.pointList= [] # lista de pontos que podem ser percorridos
        for x in range(self.world.size.x):
            for y in range(self.world.size.y):
                self.pointList.append(Point(x,y))
        # self.graph = self.createGraph()
        self.dead_locks = self.dead_locks()
        #print(self.graph.g)

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
                    nextpos = self.path[-1]
                    if nextpos not in validact:
                        goal = self.path[0]
                        self.path = self.search(head, goal, bodies)

                    if new_path:
                        self.path = self.shortest_path(new_path, self.path)
                elif new_path:
                    self.path = new_path
                if self.path:
                    nextpos = self.path.pop()
                    return validact[nextpos], b""

        else:
            if self.path:
                nextpos = self.path[-1]
                if nextpos not in validact:
                    goal = self.path[0]
                    self.path = self.search(head, goal, bodies)

                if self.path:
                    nextpos = self.path.pop()
                    return validact[nextpos], b""

        return Stay, b""

    # verifica se é necessário um path para chegar á posição
    # depth_search
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
        closedset = set() # coordenadas visitadas
        openset = [start] # coordenadas por visitar
        cameFrom = {} # dicionario/mapa, dada uma posicao retorna a posicao anterior
        Gdict = collections.defaultdict(lambda: math.inf) # dicionario/mapa, dada uma posicao retorna o custo acumulado
        Gdict[start] = 0
        while openset != []:
            current = openset[0]
            if current == goal and current != start:
                return self.find_path(cameFrom, current, start)

            openset.remove(current)
            closedset.add(current)
            neighbors = list(self.valid_actions(current, bodies, closedset).keys())
            neighbors.sort(key=lambda x: self.distance(x, goal))

            for pos in neighbors:
                gscore = Gdict[current] + self.distance(current,pos)

                if gscore < Gdict[pos]:
                    cameFrom[pos] = current
                    Gdict[pos] = gscore

            openset += [pos for pos in neighbors if pos not in openset]

        return []

    # devolve uma lifo sendo que o ultimo é na verdade a proxima posicao
    def find_path(self, cameFrom, end, start):
        current = end
        deque = []
        deque.append(current)
        while current in cameFrom and cameFrom[current] != start:
            current = cameFrom[current]
            deque.append(current)

        return deque

    # devolve um dicionário de pontos para ações
    # forbiden é um set de pontos para excluir, reduz os ciclos se for uma lista grande
    def valid_actions(self, head, bodies, forbiden=set()):
        validact = {}
        for act in ACTIONS[1:]:
            newpos = self.world.translate(head, act)
            if newpos not in self.dead_ends and newpos not in bodies and newpos not in forbiden:
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

    def find_waypoints(self):
        result = []
        horizontalList = [Point(1,0), Point(0,1), Point(-1,0), Point(0,-1)]
        diagonalList = [Point(1,1), Point(-1,1), Point(-1,-1), Point(1,-1)]
        for pos in self.world.walls.keys():
            for i in range(4):
                p1 = self.world.translate(pos, horizontalList[i])
                p2 = self.world.translate(pos, horizontalList[(i+1)%4])
                pDiag =  self.world.translate(pos,diagonalList[i])
                if pDiag not in self.dead_ends and p1 not in self.dead_ends and p2 not in self.dead_ends:
                    result.append(pDiag)
        return set(result)

    def createGraph(self):
        g = Graph(self.world)
        wayList = list(self.waypoints)
        while wayList:
            n1 = wayList.pop()
            l = [x for x in wayList if not self.path_needed(n1,x,[])]
            for p in l:
                g.add(n1,p)
        return g

    def dijkstra_search(graph, start, goal):
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        while not frontier.empty():
            current = frontier.get()
            if current == goal:
                break
            for next in graph.neighbors(current):
                new_cost = cost_so_far[current] + graph.cost(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost
                    frontier.put(next, priority)
                    came_from[next] = current

        return self.reverse(came_from,start, goal)

    def reverse(self,came_from,start,goal):
        current = goal
        path = []
        while current != start:
            path.append(current)
            current = came_from[current]
        path.append(start)
        path.reverse()
        return path

    # breadth_search
    def closest_waypoint(self, point):
        openset = set()
        openset.add(point)
        closedset = set()
        while openset:
            waypoints = [pos for pos in openset if pos in self.waypoints]
            # apenas waypoints diretos, sem path
            waypoints = [pos for pos in waypoints if not self.path_needed(point, pos, {})]
            if waypoints:
                return [waypoints[0]]
            else:
                closedset.update(openset)
                for pos in openset.copy():
                    s = self.valid_actions(pos, {})
                    l = {pos for pos in s.keys() if pos not in closedset}
                    openset.update(l)
        return []

    def dead_locks(self):
        go = DIRECTIONS.copy()
        result = {}
        # [(Up, Down), (Right, Left)] 
        tuple_go = [(go[0],go[1]), (go[2], go[3])]
        # retira os dead_ends
        empty_points = [pos for pos in self.pointList if pos not in self.dead_ends]
        # por cada ponto na lista de pontos vazios nao visitados
        for pos in empty_points:
            # i é um tuplo no go
            for i in range(2):
                p = self.world.translate(pos, tuple_go[i][0])
                poposite = self.world.translate(pos, tuple_go[i][1])
                if p in self.dead_ends and poposite in self.dead_ends:
                    # constroi o "path" do deadlock_path, TODO curvas não funcionam por algum motivo
                    dlocks1 = self.dead_lock_list(pos)
                    # reconstroi a lista na mesma referencia
                    empty_points = [pos for pos in empty_points if pos not in dlocks1]
                    # redundancia, dado um ponto como key num dicionario devolve um objeto dead_lock_mutex se existe, O(1)
                    result[dlocks1[0]] = dead_lock_mutex(dlocks1)
                    result[dlocks1[-1]] = dead_lock_mutex(dlocks1)

        return result

    # verifica se um determinado ponto é um entroncamento
    def bissection(self, pos, forbiden):
        bissections = [pos for pos in self.valid_actions(pos, {}, forbiden)]
        # se tem 3 ações então é um entroncamento
        if len(bissections) > 2:
            return True
        else:
            return False

    # dado um ponto entre duas paredes faz uma "Pesquisa Bidirecional em Profundidade"
    def dead_lock_list(self, pos):
        dlocks1 = [pos]
        # pontos visitados no path
        closedset = set()
        closedset.add(pos)
        # search numa direção
        nextpos = list(self.valid_actions(pos, {}, closedset).keys())
        # um dead_lock tem apena uma e uma só saida
        while len(nextpos)==1:
            dlocks1[1:] = dlocks1[:]
            dlocks1[0] = nextpos[0]
            closedset.add(nextpos)
            nextpos = list(self.valid_actions(nextpos, {}, closedset).keys())

        # search na direção oposta
        nextpos = list(self.valid_actions(pos, {}, closedset).keys())
        while len(nextpos)==1:
            dlocks1.append(nextpos)
            closedset.add(nextpos)
            nextpos = list(self.valid_actions(nextpos, {}, closedset).keys())

        return dlocks1
    
class dead_lock_mutex():
    def __init__(self, dlocks):
        self.borders = [dlocks[0], dlocks[-1]]
        self.taken = False
        self.dead_locks = dlocks
    
    # chamada quando o head entra num ponto fronteira do dead_lock
    def lock(self):
        self.taken = True

    # chamada quando o head sai de um ponto fronteira do dead_lock
    def unlock(self):
        self.taken = False


from collections import defaultdict
import world

class Graph():

    def __init__(self, world):
        self.g = defaultdict(set)
        self.world = world

    def add(self, node1, node2):
        if node1 == node2:
            return
        distance = self.world.dist(node1,node2)
        self.g[node1].add((node2,distance))
        self.g[node2].add((node1,distance))

    def remove(self, node1, node2):
        distance = self.world.dist(node1,node2)
        self.g[node1].remove((node2,distance))
        self.g[node2].remove((node1,distance))

    def isConnected(self, node1, node2):
        if node1 in self.g.keys() and [item for item in self.g[node1] if item[0] == node2]:
            return True
        return False

    def neighbors(self,node1):
        return [a for (a,b) in self.g[node1]]

    def cost(self, node1, node2):
        if not self.isConnected(node1,node2):
            return None
        return {b for a,b in self.g[node1] if a == node2}.pop()

import heapq

class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]

if __name__ == "__main__": # DEBUG Graph
    w = World(Point(5,5))
    h = Graph(w)
    h.add(Point(2,2), Point(3,2))
    h.add(Point(2,2), Point(4,4))
    print(h.isConnected(Point(2,2),Point(3,2)))
    print(h.cost(Point(2,2),Point(3,2)))
    print(h.neighbors(Point(2,2)))
    print(h.g)
