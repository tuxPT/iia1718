# Cooperating Agents Game Version 0.9 
# Initially based on the code provided by http://www.virtualanup.com at https://gist.githubusercontent.com/virtualanup/7254581/raw/d69804ce5b41f73aa847f4426098dca70b5a1294/snake2.py
# Modified by Diogo Gomes <dgomes@av.it.pt> 2016
#
# JMRodrigues <jmr@ua.pt> 2017

import sys
import copy
from collections import namedtuple, ChainMap, Counter
import pygame,random
from pygame.locals import *
import logging

from constants import *
from world import *

class Player:
    def __init__(self, name, body, world, AgentClass, color=(255,0,0)):
        self.name = name
        self.body = body[:]
        self.world = world
        
        self.agent = AgentClass(name, body[:], copy.deepcopy(world))
        
        self.IsDead = False
        self.nutrients = {}
        self.nutrients['M'] = 1000
        self.nutrients['S'] = 1000
        self.timespent = 0
        self.horizon = 20
        
    def kill(self):
        if not self.IsDead:
            self.IsDead = True
            ##self.agent.IsDead = True
            ##self.nutrients = 0
            logging.info("Player <{}> died".format(self.name))

    ## NOT USED yet
    def filterVision(self, env):
        """Return only the parts of the environment which are visible."""
        return {p:v for p,v in env.items() if self.world.dist(p, self.body[0]) <= self.horizon}  

    ## NOT USED yet
    def transferInfo(self):
        """Transfer filtered dynamic info from player into corresponding agent."""
        self.agent.body = copy.deepcopy(self.body)
        ##self.agent.world.bodies = self.filterVision(self.world.bodies)
        ##self.agent.world.food = self.filterVision(self.world.food)
    
        self.agent.nutrients = copy.deepcopy(self.nutrients)
        self.agent.timespent = self.timespent
        ##self.agent.count = self.count
        pass
        
class AgentGame:
    def __init__(self, AgentClass, width=60, height=40, tilesize=20, fps=50, visual=False, walls=15, foodquant=4, filename=None, timeout=sys.maxsize):
        logging.basicConfig(format='%(levelname)s:\t%(message)s', level=logging.WARN) 

        if filename != None:
            logging.info("Loading {} ...".format(filename))
            image = pygame.image.load(filename)
            pxarray = pygame.PixelArray(image)
            width = len(pxarray)
            height = len(pxarray[0])
        
        ## Create the game world view:
        self.world = World(Point(width, height))
        
        ## Fill the walls
        if filename != None:
            self.world.loadField(pxarray)
        else:
            self.world.generateWalls(walls)
        
        self.timeout = timeout #maximum number of cycles 
        
        self.tilesize = tilesize  #tile size, adjust according to screen size
        
        if visual: 
            #create the window and do other stuff
            pygame.init()
            self.screen = pygame.display.set_mode(((self.world.size.x)*self.tilesize,(self.world.size.y)*self.tilesize+25), pygame.RESIZABLE)
            pygame.display.set_caption('Cooperating Agents Game')
        
            #load the font
            self.font = pygame.font.Font(None, 30)
        else:
            self.screen = None
        
        self.foodquant = foodquant
        
        self.fps = fps #frames per second. The higher, the harder
        self.timeslot = 1000//self.fps//2  ## time in milliseconds for each agent...
        
        ## Create players
        self.dead = []
        self.players = []
        body = self.world.generatePlayerBody("P0")
        self.players.append(Player("P0", body, self.world, AgentClass, Green))
        body = self.world.generatePlayerBody("P1")
        self.players.append(Player("P1", body, self.world, AgentClass, Blue))
    
        
    
    def printstatus(self):
        PlayerStat = namedtuple('PlayerStat', 'name  nutrients')
        pstat = [PlayerStat(p.name, p.nutrients) for p in self.players + self.dead]
      
        score = "{}={}  {}  {}={}".format(pstat[0].name, pstat[0].nutrients, self.count, pstat[1].nutrients, pstat[1].name)
        if self.screen == None and (self.count % self.fps == 0 or self.count >= self.timeout):
            logging.info(score)
        elif self.screen != None:
            text = self.font.render(score, 1,(255,255,255))
            textpos = text.get_rect(centerx=self.screen.get_width()/2,y=(self.world.size.y)*self.tilesize)

            player1_name=self.font.render(pstat[0].name,1, White)
            player1_pos = player1_name.get_rect(x=self.screen.get_width()/2 - self.font.size(score + pstat[0].name)[0],y=(self.world.size.y)*self.tilesize)

            player2_name=self.font.render(pstat[1].name,1, White)
            player2_pos = player2_name.get_rect(x=self.screen.get_width()/2 + self.font.size(score)[0],y=(self.world.size.y)*self.tilesize)
            
            self.screen.blit(player1_name, player1_pos)
            self.screen.blit(player2_name, player2_pos)
            self.screen.blit(text, textpos)
      
        text = None
        if len([p for p in self.players if not p.IsDead]) == 0:
            dead = "All dead..."
            if self.screen == None:
                logging.info(dead)
            else:
                text=self.font.render(dead,1,(255,128,0))
        if text != None and self.screen != None:
            textpos = text.get_rect(centerx=self.screen.get_width()/2, centery=self.screen.get_height()/2)
            self.screen.blit(text, textpos)
    
    def gameKill(self, player):
        player.kill()
        self.players.remove(player)
        self.dead.append(player)

    def executeAction(self, player, action):
        assert isinstance(player, Player)
        
        ## Check action!
        if action not in DIRECTIONS:
            self.gameKill(player)
            logging.error("{} invalid action: {} -> DEAD".format(player.name, action))
            return
        
        ## Account for nutrients
        logging.info("Player <{}> took {}".format(player.name, player.timespent))   ## TODO
        cost = 1 + player.timespent//self.timeslot
        player.nutrients['S'] -= cost   ## Thinking costs nutrients!
        player.nutrients['M'] -= 1      ## Moving costs nutrients too!

        # Update the head
        head = player.body[0]    ## head of player
        head = self.world.translate(head, action)
                
        # Check if the player crashed
        if head in self.world.walls:  #hit a wall
            self.gameKill(player)
            logging.info("{} crashed against wall -> DEAD".format(player.name))
        elif head in self.world.bodies:  ## (May crash into old tail tip! BUG? FEATURE?)
            self.gameKill(player)
            logging.info("{} crashed against a body -> DEAD".format(player.name))
        else:
            if head in self.world.food:
                #the player ate the food
                t = self.world.food.pop(head)   ## remove the food
                player.nutrients[t] += 100      ## absorb nutrients
                ## grow body
                #player.body.append(tail)
                #self.world.bodies[tail] = player.name
            # Update the body
            tail = player.body[-1]   ## tail tip (may be needed after eating)
            player.body = [head] + player.body[:-1]
            self.world.bodies[head] = player.name
            self.world.bodies.pop(tail)
        
        if player.nutrients['S'] <= 0 or player.nutrients['M'] <= 0:
            self.gameKill(player)
            logging.info("{} run out of nutrients -> DEAD".format(player.name))
        
        self.checkBodies()
        
    def checkBodies(self):
        c = 0
        for player in self.players:
            for pos in player.body:
                c += 1
                assert pos in self.world.bodies
        assert c == len(self.world.bodies)
    
        
    def start(self):
        clock = pygame.time.Clock()
        self.count = 0
        ## Main loop?
        while len([p for p in self.players if not p.IsDead]) > 1 and self.count < self.timeout :
            self.count += 1
            clock.tick(self.fps)
            ## Get events
            if self.screen != None:
                for event in pygame.event.get():
                    if event.type == QUIT or (event.type == pygame.KEYDOWN and event.key == K_ESCAPE): #close window or press ESC
                        pygame.quit();
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        ## Other key down events are sent to every agent (might be used for testing)
                        for player in self.players:
                            player.agent.processkey(event.key)  ## TODO: remove call and pass info later?
                    elif event.type == pygame.VIDEORESIZE:
                        self.tilesize = int(max(event.w/(self.world.size.x), event.h/(self.world.size.y)))
                        self.screen = pygame.display.set_mode(((self.world.size.x)*self.tilesize,(self.world.size.y)*self.tilesize+25), pygame.RESIZABLE)
            
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
            for player in [a for a in self.players if not a.IsDead]:
                try:
                    ## Transfer info to agent
                    player.transferInfo()
                    vision = namedtuple('Vision', ['bodies', 'food'])
                    vision.bodies = player.filterVision(self.world.bodies)
                    vision.food = player.filterVision(self.world.food)
                    
                    ## Call the AGENT! (and measure time and catch errors)
                    s = pygame.time.get_ticks()
                    action = player.agent.chooseAction(vision)
                    f = pygame.time.get_ticks()
                    player.timespent = f - s
                    
                    ## Execute the action and update the game
                    self.executeAction(player, action)
                except Exception as error:
                    logging.error(str(error))
                    player.kill()
            
            #print all the content in the screen
            if self.screen != None:
                self.screen.fill((0,0,0))
                for player in self.players: #print players
                    f = 0.2+0.7*player.nutrients['S']/2000
                    (r,g,b) = FOODCOLOR['S']
                    head_color = (int(r*f), int(g*f), int(b*f))
                    f = 0.2+0.7*player.nutrients['M']/2000
                    (r,g,b) = FOODCOLOR['M']
                    color = (int(r*f), int(g*f), int(b*f))
                    #head + rest of body
                    pygame.draw.rect(self.screen, head_color, (player.body[0][0]*self.tilesize, player.body[0][1]*self.tilesize, self.tilesize, self.tilesize),0)
                    for part in player.body[1:]:
                        pygame.draw.rect(self.screen, color, (part[0]*self.tilesize, part[1]*self.tilesize, self.tilesize, self.tilesize), 0)

                for wall in self.world.walls: #print walls
                    pygame.draw.rect(self.screen, WALLCOLOR, (wall[0]*self.tilesize, wall[1]*self.tilesize, self.tilesize, self.tilesize), 0)
                
                for f in self.world.food: #print food
                    pygame.draw.rect(self.screen, FOODCOLOR[self.world.food[f]], (f[0]*self.tilesize, f[1]*self.tilesize, self.tilesize, self.tilesize), 0)
 
            self.printstatus()
            if self.screen != None:
                pygame.display.flip()

        if self.count >= self.timeout:
            logging.critical("GAME OVER BY TIMEOUT after {} counts".format(self.count))
        else:
            logging.info("GAME OVER after {} counts".format(self.count))
        
        #print(max(self.players, key=lambda p: p.nutrients).name)
        for p in self.players:
            try:
                p.agent.destroy()
            except Exception as error:
                logging.error(str(error))

        while self.screen != None:
            event = pygame.event.wait()
            if event.type == QUIT or (event.type == pygame.KEYDOWN and event.key == K_ESCAPE): #close window or press ESC
                pygame.quit(); 
                sys.exit()
