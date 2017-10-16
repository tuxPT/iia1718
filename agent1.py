from agent import Agent
from constants import *
import random

class Agent1(Agent):
    def __init__(self, name, body, world):
        super().__init__(name, body, world)
        self.direction = (1,0)
    
    def chooseAction(self, vision):
        #this is the brain of the agent
        olddir = self.direction
        head = self.body[0]
        
        #get the list of valid DIRECTIONS for us
        validdir = []
        for dir in DIRECTIONS:
            newpos = self.world.translate(head, dir)
            if newpos not in self.world.walls and newpos not in vision.bodies:
                validdir.append(dir)
        
        self.direction = random.choice(validdir)
        return self.direction
