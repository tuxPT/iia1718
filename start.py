# Run this script to start the game.
# Examples:
# python3 start.py                  # play the game with Agent1 on a random world.
# python3 start.py -m mapa4.bmp     # use a specified world map.
# python3 start.py -s StudentAgent  # use another agent.
# python3 start.py -d 1             # show a log of information messages (and above).
# python3 start.py -d 0 -v          # run fast without video, show debug log

from game import *
from agent1 import Agent1
import importlib
import logging
import sys
import getopt


USAGE = \
"""start.py [-h/--help
          -s/--student-agent AgentName
          -m/--map <mapfile>
          -v/--no-video
          -d/--debug Level(0--4)
"""


def main(argv):

    levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
    
    inputfile = None
    visual = True
    studentAgent = Agent1
    debug = 2
    
    try:
        opts, args = getopt.getopt(argv,"hm:vs:d:",["help","map=","no-video","student-agent", "debug="])
    except getopt.GetoptError as e:
        print(e)
        print(USAGE)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(USAGE)
            sys.exit()
        elif opt in ["-m", "--map"]:
            inputfile = arg
        elif opt in ["-v", "--no-video"]:
            visual = False 
        elif opt in ["-s", "--student-agent"]:
            classmodule = importlib.import_module(arg.lower())
            studentAgent = getattr(classmodule, arg)
        elif opt in ["-d", "--debug"]:  # not working?
            debug = int(arg)
        
    logging.basicConfig(format='%(levelname)s:\t%(message)s', level=levels[debug]) 
            
    try:
        game = AgentGame(AgentClass=studentAgent,
            width=60, height=40, foodquant=4, timeslot=0.020,
            filename=inputfile, walls=15,
            visual=visual, fps=25, tilesize=20)
        print("Launching game")
        score = game.start()
        print("Score:", score)
    except Exception as e:
        logging.exception(e)
        sys.exit(1)
    
if __name__ == "__main__":
    main(sys.argv[1:])

