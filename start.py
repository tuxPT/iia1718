# Run this script to start the game.

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
          --disable-video
          -t/--timeout MSEC
          -d/--debug Level(0--4)
"""


def main(argv):

    levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL] 
    
    inputfile = None
    visual = True
    StudentAgent = Agent1
    timeout = sys.maxsize
    debug = 2
    
    try:
        opts, args = getopt.getopt(argv,"hm:s:t:d:",["help","map=","disable-video","student-agent","timeout=", "debug="])
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
        elif opt in ["-t", "--timeout"]:
            timeout = int(arg)
        elif opt in ["--disable-video"]:
            visual = False 
        elif opt in ["-s", "--student-agent"]:
            classmodule = importlib.import_module(arg.lower())
            StudentAgent = getattr(classmodule, arg)
        elif opt in ["-d", "--debug"]:  # not working?
            debug = int(arg)
        
    logging.basicConfig(format='%(levelname)s:\t%(message)s', level=levels[debug]) 
            
    try:
        game = AgentGame(AgentClass=StudentAgent,
            width=60, height=40, foodquant=4, timeslot=10,
            filename=inputfile, walls=15,
            visual=visual, fps=20, tilesize=20,
            timeout=timeout)
        print("Launching game")
        score = game.start()
        print("Score:", score)
    except Exception as e:
        logging.exception(e)
        sys.exit(1)
    
if __name__ == "__main__":
    main(sys.argv[1:])

