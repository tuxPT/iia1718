from game import *
from agent1 import Agent1
import importlib
import logging
import sys
import getopt


USAGE = \
"""start.py [-h/--help -m/--map <mapfile> --disable-video
          -t/--timeout MSEC
          -s/--student-agent AgentName
"""
    

#start the game
def main(argv):
    inputfile = None
    visual = True
    StudentAgent = Agent1
    timeout = sys.maxsize
    try:
        opts, args = getopt.getopt(argv,"hm:s:t:",["help","map=","disable-video","student-agent","timeout="])
    except getopt.GetoptError as e:
        print(e)
        print(USAGE)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(USAGE)
            sys.exit()
        elif opt in ("-m", "--map"):
            inputfile = arg
        elif opt in ("-t", "--timeout"):
            timeout = int(arg)
        elif opt in ("--disable-video"):
            visual = False 
        elif opt in ("-s", "--student-agent"):
            classmodule = importlib.import_module(arg.lower())
            StudentAgent = getattr(classmodule, arg)
            
    try:
        game = AgentGame(AgentClass=StudentAgent, width=60, height=40, fps=20,
                         walls=15, foodquant=4,
                         filename=inputfile,
                         visual=visual, timeout=timeout)
        print("Launching game")
        game.start()
    except Exception as e:
        logging.exception(e)
        sys.exit(1)
    
if __name__ == "__main__":
   main(sys.argv[1:])

