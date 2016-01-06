#! /usr/bin/env python

import pygame
from pygame.locals import *

from data import *

from sprites import *

class Level:

    """
    
    # PyUML: Do not remove this line! # XMI_ID:_G462QM_IEd6f27AX6AwMPQ
    """

    def __init__(self, lvl=1):
        self.bonus_map = BonusMap()
        
        self.level = pygame.image.load(filepath(("lvl%d.png" % lvl))).convert()
        self.x = 0
        self.y = 0
        for y in range(self.level.get_height()):
            self.y = y
            for x in range(self.level.get_width()):
                self.x = x
                color = self.level.get_at((self.x, self.y))
                if color == (0, 0, 0, 255):
                    l=r=False
                    tile = "middle"
                    Platform((self.x*16, self.y*16), tile, l, r)

                if color == (255,255,0,255):
                    self.bonus_map.add_by_type((self.x*16+8, self.y*16+8),"lifeup")
                if color == (0,0,255,255):
                    self.bonus_map.add_by_type((self.x*16, self.y*16),"machine_gun")
                if color == (255,0,0,255):
                    self.bonus_map.add_by_type((self.x*16, self.y*16),"shot_gun")
                if color == (0,255,0,255):
                    self.bonus_map.add_by_type((self.x*16+8, self.y*16+8),"bomb")

    def get_bonus_map(self):
        return self.bonus_map                
                    
                                       
    def get_at(self, dx, dy):
        try:
            return self.level.get_at((self.x+dx, self.y+dy))
        except:
            pass
            
    def get_size(self):
        return [self.level.get_size()[0]*32, self.level.get_size()[1]*32]

class BonusMap():
    def __init__(self):
        self.bonuses = [None]
    def add(self,bonus):
        self.bonuses.append([bonus.rect.center,bonus.type,0])
        
    def add_by_type(self,pos,type):
        self.bonuses.append([pos,type,0])
        
    def create_all(self):
        for b in self.bonuses:
            if not b == None:
                if b[1] == "lifeup":
                    Bonus(b[0],b[1],self)
                else:
                    InvBonus(b[0],b[1],self)
        del self.bonuses[:]
        self.bonuses=[None]             
            
        
    def update(self):
        for b in self.bonuses:
            if not b == None:
                b[2]+=1
                if b[2] == 1000:
                    if b[1] == "lifeup":
                        Bonus(b[0],b[1],self)
                    else:
                        InvBonus(b[0],b[1],self)
                    self.bonuses.remove(b)

        
    
    