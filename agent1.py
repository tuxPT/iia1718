from agent import *
import random

class Agent1(Agent):
    def __init__(self, name, body, world):
        super().__init__(name, body, world)

    def chooseAction(self, vision):
        #this is the brain of the agent
        head = self.body[0]
        
        #get the list of valid actions for us
        validact = ACTIONS[:1]   # staying put is always valid
        for act in ACTIONS[1:]:
            newpos = self.world.translate(head, act)
            if newpos not in self.world.walls and newpos not in vision.bodies:
                validact.append(act)
        
        action = random.choice(validact)
        return action
