from agent import *
import random,math,sys,collections,pickle


# This is an example of an agent to play the LongLife game.
# It is not very intelligent: it simply avoids crashing onto walls or bodies.

class StudentAgent(Agent):
    def __init__(self, name, body, world):
        super().__init__(name, body, world)
        self.number = 0
        self.sum = 0

    def chooseAction(self, vision, msg):
        """Analyse input vision and msg, and choose an action to do and msg to post."""
        # This is the brain of the agent. It should be reimplemented on any subclass.
        # It may use the fields (.name, .world, .body, .nutrients, .age, .timespent)
        # and the parameters (vision and msg) to decide what to do.
        # It must return an action (one of the ACTIONS),
        # and a message (a possibly empty bytes object) to send to the other agent.
        # (You may want to use pickle.dumps / pickle.loads to convert
        # objects to bytes and back.)

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
        closedset = list() # coordenadas visitadas
        openset = [start] # coordenadas por visitar
        cameFrom = dict() # dicionario/mapa, dada uma posicao retorna a posicao anterior
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
            neighbors = list(pos for pos in validact if pos not in closedset) 
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
        validact = dict()
        for act in ACTIONS[1:]:
            newpos = self.world.translate(head, act)
            if newpos not in self.world.walls and newpos not in vision.bodies:
                validact[newpos] = act
        return validact