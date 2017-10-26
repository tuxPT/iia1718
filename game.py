# LongLife: a cooperating agents game
# v1.0
# This version implements all features of the game:
# moving, thinking, communicating, nutrient redistribution and ageing.
#
# Initially based on the code provided by http://www.virtualanup.com at https://gist.githubusercontent.com/virtualanup/7254581/raw/d69804ce5b41f73aa847f4426098dca70b5a1294/snake2.py
# Modified into the ia-iia-snake game by Diogo Gomes <dgomes@av.it.pt> 2016
# Transformed into the ia-iia-longlife game by JM Rodrigues <jmr@ua.pt> 2017

import sys
import logging
import copy
from collections import namedtuple, ChainMap, Counter
import pygame
from pygame.locals import *
import time

from world import *

class Player:
    def __init__(self, name, body, world, AgentClass):
        self.name = name
        self.body = body[:]
        self.world = world
        self.age = 0
        
        self.agent = AgentClass(name, body[:], copy.deepcopy(world))
        
        self.nutrients = {}
        self.nutrients['M'] = 1000
        self.nutrients['S'] = 1000
        self.timespent = 0.0    # cpu time spent in previous cycle (s)
        self.horizon = 20
        
        self.inbox = self.outbox = b""  # message mailboxes
        
    def filterVision(self, env):
        """Return only the parts of the environment which are visible."""
        return {p:v for p,v in env.items() if self.world.dist(p, self.body[0]) <= self.horizon}  

    def transferInfo(self):
        """Transfer proprioception from player into corresponding agent."""
        self.agent.age = self.age
        self.agent.body = copy.deepcopy(self.body)
        self.agent.nutrients = copy.deepcopy(self.nutrients)
        self.agent.timespent = self.timespent
        
    def __str__(self):
        return "{}(age={},nutrients={}),head={}".format(self.name, self.age, self.nutrients, self.body[0])


class AgentGame:
    def __init__(self, AgentClass,
            width=60, height=40, foodquant=4, timeslot=0.020,
            filename=None, walls=15,
            visual=False, fps=25, tilesize=20):

        if filename != None:
            logging.info("Loading {} ...".format(filename))
            image = pygame.image.load(filename)
            pxarray = pygame.PixelArray(image)
            width = len(pxarray)
            height = len(pxarray[0])
        
        ## Create the game world view:
        self.world = World(Point(width, height))
        
        self.foodquant = foodquant  # quantity of each kind of food
        self.timeslot = timeslot    # time in seconds afforded per R units of S nutrient (Confused?)
        self.bytesPerS = 10         # bytes of communication afforded per unit of S nutrient
        
        ## Fill the walls
        if filename != None:
            self.world.loadField(pxarray)
        else:
            self.world.generateWalls(walls)
        
        self.fps = fps      # Frames per second
        self.tilesize = tilesize    # tile size
        
        if visual: 
            #create the window and do other stuff
            pygame.init()
            self.screen = pygame.display.set_mode(((self.world.size.x)*self.tilesize,(self.world.size.y)*self.tilesize+25), pygame.RESIZABLE)
            pygame.display.set_caption('LongLife Cooperating Agents Game')
            #load the font
            self.font = pygame.font.Font(None, 30)
        else:
            self.screen = None
            self.fps = 0         # no need to slow down when not displaying
        
        ## Create players
        self.allPlayers = []
        for name in ["P0", "P1"]:
            body = self.world.generatePlayerBody(name)
            self.allPlayers.append(Player(name, body, self.world, AgentClass))
        self.livePlayers = self.allPlayers[:]   # list of live players
        self.deadPlayers = []                   # list of dead players
    
    def killPlayer(self, player):
        #for t in player.nutrients:
        #    player.nutrients[t] = 0
        self.livePlayers.remove(player)
        self.deadPlayers.append(player)

    def executeAction(self, player, action):
        
        ## Check action
        if action not in ACTIONS:
            self.killPlayer(player)
            logging.error("{} invalid action: {} -> DEAD".format(player.name, action))
            return
        
        ## Check message
        if not isinstance(player.outbox, bytes):
            self.killPlayer(player)
            logging.error("{} invalid message: {} -> DEAD".format(player.name, player.outbox))
            return
        
        ## Account for nutrients
        costT = 1 + int(player.timespent/self.timeslot)   # Cost of Thinking
        costC = (len(player.outbox)+self.bytesPerS-1)//self.bytesPerS   # Cost of Communicating
        costA = 1 + player.age//1000       # Cost of Acting: increases with age
        # Thinking & Communicating consume S nutrients:
        player.nutrients['S'] -= costT + costC
        # Acting consumes M nutrients:
        player.nutrients['M'] -= costA
        logging.info("{} consumes {} units of S <= spent {} s thinking.".format(player.name, costT, player.timespent))
        logging.info("{} consumes {} units of S <= spent {} bytes communicating.".format(player.name, costC, len(player.outbox)))
        logging.info("{} consumes {} units of M <= chose action {}.".format(player.name, costA, action))
        
        if player.nutrients['S'] <= 0 or player.nutrients['M'] <= 0:
            self.killPlayer(player)
            logging.info("{} run out of nutrients -> DEAD".format(player.name))
            return
        
        ## Move (or stay put)
        if action != Stay:
            # New head position
            head = player.body[0]    ## current head of player
            head = self.world.translate(head, action)
                    
            # Check if the player crashed
            if head in self.world.walls:    # hit a wall
                self.killPlayer(player)
                logging.info("{} crashed against wall -> DEAD".format(player.name))
                return
            if head in self.world.bodies:   # hit a body
                self.killPlayer(player)
                logging.info("{} crashed against a body -> DEAD".format(player.name))
                return
            # Update the body
            tail = player.body[-1]   # tail tip (may be needed after eating)
            player.body = [head] + player.body[:-1]
            self.world.bodies[head] = player.name
            self.world.bodies.pop(tail)
            if head in self.world.food: # eat food
                ## remove the food
                t = self.world.food.pop(head)
                ## absorb nutrients (but not indefinitely)
                player.nutrients[t] = min(player.nutrients[t]+100, 2000)
                ## grow body
                #player.body.append(tail)
                #self.world.bodies[tail] = player.name
        
        self.checkBodies()  # check bodies invariant

    def checkBodies(self):
        c = 0
        for player in self.allPlayers:
            for pos in player.body:
                c += 1
                assert pos in self.world.bodies
                assert self.world.bodies[pos] == player.name
        assert c == len(self.world.bodies), (c, self.world.bodies,)
    
    def redistibuteNutrients(self):
        """Redistributes nutrients between players in order to equalize their stocks.
        For example: {'S':1, 'M':8} and {'S':8, 'M':2} -> {'S':4, 'M':5} and {'S':5, 'M':5}.
        """
        for t in FOODTYPES:
            # TODO: allPlayers? even if dead?
            players = sorted(self.allPlayers, key=lambda p: p.nutrients[t], reverse=True)
            total = sum(p.nutrients[t] for p in players)
            (m, r) = divmod(total, len(players))    # find integer mean and remainder
            for p in players:
                p.nutrients[t] = m + (r>0)  # add 1 to the first r players
                r -= 1
            # Test postcondition:
            assert total == sum(p.nutrients[t] for p in players), "Total should be conserved"
            n = [p.nutrients[t] for p in players]
            assert max(n) - min(n) <= 1, "Differences should be at most 1" 
        return
    
    
    def getEvents(self):
        ## Get events
        if self.screen != None:
            self.world.keys = []
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == pygame.KEYDOWN and event.key == K_ESCAPE): #close window or press ESC
                    pygame.quit();
                    raise KeyboardInterrupt("ESC pressed")
                elif event.type == pygame.KEYDOWN:
                    ## Other key down events will be available to every agent (may be used for testing)
                    self.world.keys.append(event.key)
                elif event.type == pygame.VIDEORESIZE:
                    self.tilesize = int(min(event.w/self.world.size.x, event.h/self.world.size.y))
                    self.screen = pygame.display.set_mode((self.world.size.x*self.tilesize, self.world.size.y*self.tilesize+25), pygame.RESIZABLE)
                    print(event, self.tilesize)
    
    def show(self):
        # Show all the game contents in the screen
        if self.screen != None:
            T = self.tilesize
            self.screen.fill((0,0,0))
            
            # Show walls
            for wall in self.world.walls:
                pygame.draw.rect(self.screen, WALLCOLOR, (wall[0]*T, wall[1]*T, T, T), 0)
            
            # Show food
            for f in self.world.food:
                pygame.draw.ellipse(self.screen, FOODCOLOR[self.world.food[f]], (f[0]*T, f[1]*T, T, T), 0)
            
            ## Show players
            for player in self.allPlayers:
                f = 0.25+0.75*player.nutrients['S']/2000
                (r,g,b) = FOODCOLOR['S']
                head_color = (int(r*f), 64, int(b*f))
                f = 0.25+0.75*player.nutrients['M']/2000
                (r,g,b) = FOODCOLOR['M']
                color = (int(r*f), 64, int(b*f))
                #head + rest of body
                pygame.draw.rect(self.screen, head_color, (player.body[0][0]*T, player.body[0][1]*T, T, T), 0)
                for part in player.body[1:]:
                    pygame.draw.rect(self.screen, color, (part[0]*T, part[1]*T, T, T), 0)
            
        # Show stats
        line = "  ".join(str(p) for p in self.allPlayers)
        
        logging.info("Stats: "+line)
        
        if self.screen != None:
            ## Show stats
            text = self.font.render(line, 1, (255,255,255))
            textpos = text.get_rect(x=0, y=(self.world.size.y)*self.tilesize)
            self.screen.blit(text, textpos)
        
        if len(self.livePlayers) == 0:
            line = "GAME OVER"
            logging.info(line)
            if self.screen != None:
                text=self.font.render(line, 1, (255,128,0), (0,0,0))
                textpos = text.get_rect(centerx=self.screen.get_width()/2, centery=self.screen.get_height()/2)
                self.screen.blit(text, textpos)
    
    def start(self):
        clock = pygame.time.Clock()
        self.count = 0
        ## Main loop
        while len(self.livePlayers) > 0:
            self.count += 1
            clock.tick(self.fps)
            
            self.getEvents()
            
            #game logic is updated in the code below
            
            ## (Re)Generate food
            foodcount = Counter(self.world.food.values())
            for t in FOODTYPES:
                while foodcount[t] < self.foodquant:
                    self.world.generateFood(t)
                    foodcount[t] += 1
            
            ## Move food
            self.world.moveFood()
 
            ## Update players
            for player in self.livePlayers:
                player.age += 1           # lived another tick!
            
                ## Transfer info to agent
                player.transferInfo()
                vision = namedtuple('Vision', ['bodies', 'food'])
                vision.bodies = player.filterVision(self.world.bodies)
                vision.food = player.filterVision(self.world.food)
                
                ## Call the AGENT (and measure time and catch errors)
                s = time.process_time()
                try:
                    action = None   # default if agent fails => Die
                    action, player.outbox = player.agent.chooseAction(vision, player.inbox)
                except Exception as e:
                    logging.exception(e)
                f = time.process_time()
                player.timespent = f - s
                logging.debug("{}.timespent = {:.4f} s".format(player.name, player.timespent))
                ## Execute the action and update the game
                self.executeAction(player, action)
            
            ## Transfer messages for next cycle
            # TODO: should this be done after each player?
            # TODO: this works only for 2 players!  Does not generalize well...
            P0, P1 = self.allPlayers
            P0.inbox, P1.inbox = P1.outbox, P0.outbox
            
            ## Check adjacency and redistribute
            # TODO: should this be done after each player?
            # TODO: this works only for 2 players!  Does not generalize well...
            h0 = P0.body[0]
            h1 = P1.body[0]
            if self.world.dist(h0, h1) == 1:
                logging.info("Rendez-vous {}-{} => Redistribution".format(h0, h1))
                logging.debug("Before: {} {}".format(*self.allPlayers))
                self.redistibuteNutrients()
                logging.debug("After: {} {}".format(*self.allPlayers))
                
            ## Show the game state
            self.show()
            
            if self.screen != None:
                pygame.display.update()

        logging.info("GAME OVER after {} counts".format(self.count))
        
        while self.screen != None:
            # Pygame BUG?: This seems to busy-wait (100% CPU)! Why?
            event = pygame.event.wait()
            if event.type == QUIT or (event.type == pygame.KEYDOWN and event.key == K_ESCAPE): #close window or press ESC
                pygame.quit(); 
                break
        
        score = sum([p.age for p in self.allPlayers])
        return score
        
