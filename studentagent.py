from agent import *
import random,math,sys,collections,pickle


# This is an example of an agent to play the LongLife game.
# It is not very intelligent: it simply avoids crashing onto walls or bodies.

class StudentAgent(Agent):

    noFoodNear = False
    waitForResponse = False
    otherAgentAlive = True
    sendingTarget = False
    appendingTarget = False
    tToAppend = ()

    init = True

    def __init__(self, name, body, world):
        super().__init__(name, body, world)

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
        msgToSend = b""
        targets = []
        msgReceived = ()
        self.sendingTarget = False

        if self.init == True:
            self.fill_dead_ends(head, vision)
            self.init = False

        head = self.body[0] 

        validact = self.valid_actions(head, vision)

        food = list(vision.food.items())
        #Check msg
        if msg:
            if(self.waitForResponse):
                self.waitForResponse = False
                self.noFoodNear = False
                msgReceived = pickle.loads(msg)
                if msg[0] == 2:
                    self.tToAppend = msg[1]
                    self.appendingTarget = True
                else: #Still To DO
                    self.tToAppend = (self.calculateInverse(head),'S')
                    self.appendingTarget = True
            else:
                self.sendingTarget = True
        else:
            if(self.waitForResponse):
                self.waitForResponse = False
                self.otherAgentAlive = False

        #Sort food
        food.sort(key=lambda x: self.world.dist(head, x[0]))

        #Sending Target
        if self.sendingTarget:
            if len(food) > 1:
                toSend = (2,food[1])
                msgToSend = pickle.dumps(toSend)
                #print(self.name + ': Sending Target: '+ str(msgToSend))
            else:
                toSend = (3,)
                msgToSend = pickle.dumps(toSend)
                #print(self.name + ': Sending No Target Available')

        #Appending Target
        if self.appendingTarget:
            #print(self.name + ': appending Target: ' + str(self.tToAppend))
            goToInverse = False
            food.append(self.tToAppend)
            if len(food) > 1 or head == self.tToAppend[0]:
                self.appendingTarget = False

        if food != []:
            pos = self.search_astar(head, food[0][0], vision)
            if pos in validact.keys():
                #print(self.name + ' - ' + str(validact[pos]))
                return validact[pos], msgToSend

            return Stay,msgToSend

        else: #Send message requiring food coordinates
            if(self.otherAgentAlive and not self.sendingTarget):
                toSend = (1,)
                msgToSend = pickle.dumps(toSend)
                #print(self.name + ': Request target: ' + str(msgToSend))
                self.noFoodNear = True
                self.waitForResponse = True
                return Stay,msgToSend
            else: #Go to Inverse TO DO
                self.tToAppend = (self.calculateInverse(head),'S')
                self.appendingTarget = True
                return Stay,msgToSend

    def calculateInverse(self,pos):
        resX = pos.x - self.world.size.x/2
        resY = pos.y - self.world.size.y/2
        return self.world.normalize(Point(resX,resY))

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
            if goal in cameFrom.keys():
                return self.first_action(cameFrom, current, start)
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

        return Point(-1, -1)

    def first_action(self, cameFrom, current, start):
        while cameFrom[current] != start:
            current = cameFrom[current]
        return current


    def valid_actions(self, head, vision):
        validact = dict()
        for act in ACTIONS[1:]:
            newpos = self.world.translate(head, act)
            if newpos not in self.world.walls and newpos not in vision.bodies:
                validact[newpos] = act
        return validact

    def fill_dead_ends(self, head, vision):
        validact = list(self.valid_actions(head, vision).keys())
        emp = namedtuple('Vision', ['bodies', 'food'])
        emp.bodies = {}
        emp.food = {}
        for pos in list(self.world.walls):
            # act_pos = [Point(0,1), Point(0-1), Point(1,0), Point(-1,0)]
            # act_pos = ACTIONS[1:]

            l1 = [self.world.normalize(i + pos) for i in ACTIONS[1:] if
                  self.world.normalize(i + pos) not in self.world.walls]

            if l1 != []:
                for j in l1:
                    if self.world.normalize(j - pos + j) in self.world.walls:
                        res = self.search_astar(j, validact[0], emp)
                        if res != Point(-1, -1):
                            self.world.walls[j] = WALL

                        # [self.walls2[self.world.normalize(j)] for j in l1 if self.world.normalize(j-pos+j) in self.walls2]
        #print(self.world.walls[Point(42,28)])