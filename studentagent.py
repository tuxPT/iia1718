from agent import *
import random


# This is an example of an agent to play the LongLife game.
# It is not very intelligent: it simply avoids crashing onto walls or bodies.

class Agent1(Agent):
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

        action = Stay
        msg = b""  # an empty message costs nothing
        return action, msg
