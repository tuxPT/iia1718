from constants import *
import logging

class Agent:
    def __init__(self, name, body, world):
        self.name = name
        self.body = body #initially located here
        self.world = world
        
        #self.timeslot = timeslot
        self.IsDead = False
        self.points = 0
        logging.basicConfig(format=':%(levelname)s:%(message)s', level=logging.DEBUG)

    def chooseAction(self, vision):
        return  ## return action (one of the DIRECTIONS)

    def processkey(self, key):
        pass #nothing to do here it is just to support human players

    def destroy(self):
        pass
    
