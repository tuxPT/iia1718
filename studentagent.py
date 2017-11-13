from agent import *
import random


# This is an example of an agent to play the LongLife game.
# It is not very intelligent: it simply avoids crashing onto walls or bodies.

class StudentAgent(Agent):
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

        head = self.body[0] # posicao atual

        # get the list of valid actions for us
        validact = ACTIONS[:1]  # staying put is always valid

        targets = list(vision.food)# converte as keys, Point(), para uma lista
        targets.sort(key=lambda x: self.distance(head, x))# sortea por distancia

        for act in ACTIONS[1:]:
            newpos = self.world.translate(head, act)
            if newpos not in self.world.walls and newpos not in vision.bodies:
                validact.append(act)

        # algoritmo de pesquisa basico, altamente ineficiente
        # D* lite ou melhor por implementar
        if targets != [] and len(validact) > 1:
            action = random.choice(validact[1:])
            newpos = self.world.translate(head, action)
            d = self.distance(newpos,targets[0])
            for act in validact[1:]:
                newpos = self.world.translate(head, act)
                dnext = self.distance(newpos, targets[0])
                if dnext < d:
                    d = dnext
                    action = act
            return action, b""
        else:
            return random.choice(validact),b""

    def distance(self, head, pos):
        dx = abs(head.x - pos.x)
        dy = abs(head.y - pos.y)
        if dx > self.world.size.x/2:
            dx = self.world.size.x - dx
        if dy > self.world.size.y/2:
            dy = self.world.size.y - dy
        return pow(pow(dx, 2) + pow(dy, 2), 1 / 2)
