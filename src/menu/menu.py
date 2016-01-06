#! /usr/bin/env python

import pygame, sys
from pygame.locals import *
import ezmenu
from game.data import *
from game import game
from game.control import *
import random


def Launch_Game(screen,controls, level = 0):
    if level ==0:
        level = random.randint(1,5)
    TheGame = game.Game(screen,controls,level)
    if TheGame.main_loop():
        GotoMapScreen(screen,controls)


def Help(screen):
    game.cutscene(screen, ["About GetTheFlag",
    "",
    "\"Get The flag is one of these awesome",
    "games in which you have a gun and",
    "feel the power of killing and owning you friends\"",
    "                    (someone said that for sure)",
    "",
    "Well, you need a joypad to play...", 
    "And 2 joypads would be even better!",
    "Once you have them, bring a friend",
    "and you will have sleepless nights",
    "playing this little shooting game",
    "And remember!,",
    "Shooting your friend is cool and fun",
    "but you won't win until you take his flag",
    "And bring it back to your camp, the title speaks!"])


def GotoMapScreen(screen,controls):
    LevelMenu(screen,controls)

class Menu(object):
    """
    
    # PyUML: Do not remove this line! # XMI_ID:_G6YO0s_IEd6f27AX6AwMPQ
    """
 
    def __init__(self, screen, controls):
        self.controls = controls
        for c in self.controls :
            c.menu = self
            
        self.sound = load_sound("menu.ogg",1)
        self.screen = screen
        self.menu = ezmenu.CustomMenu(["Quick Game", lambda: Launch_Game(screen,controls)], ["Select Level", lambda: GotoMapScreen(screen,controls)], ["About", lambda: Help(screen)],  ["QUIT GAME", sys.exit])
        self.menu.set_highlight_color((255, 0, 0))
        self.menu.set_normal_color((255, 255, 255))
        self.menu.center_at(300, 400)
        self.menu.set_font(pygame.font.Font(filepath("ARNORG.ttf"), 16))
        self.bg = [load_image("titlescreen_get_00.png"),
                   load_image("titlescreen_get_01.png"),
                   load_image("titlescreen_get_02.png"),
                   load_image("titlescreen_get_03.png"),
                   load_image("titlescreen_get_04.png"),
                   load_image("titlescreen_get_05.png"),
                   load_image("titlescreen_get_06.png"),
                   load_image("titlescreen_get_07.png"),
                   load_image("titlescreen_get_08.png"),
                   load_image("titlescreen_get_09.png"),
                   load_image("titlescreen_get_10.png"),
                   load_image("titlescreen_get_11.png"),
                   load_image("titlescreen_get_12.png"),
                   load_image("titlescreen_get_13.png"),
                   load_image("titlescreen_get_14.png"),
                   load_image("titlescreen_get_15.png"),
                   load_image("titlescreen_get_16.png"),
                   load_image("titlescreen_get_17.png"),
                   load_image("titlescreen_get_18.png"),
                   load_image("titlescreen_get_19.png"),
                   load_image("titlescreen_get_20.png"),
                   load_image("titlescreen_get_21.png"),
                   load_image("titlescreen_get_22.png"),
                   load_image("titlescreen_get_23.png"),
                   load_image("titlescreen_the_00.png"),
                   load_image("titlescreen_the_01.png"),
                   load_image("titlescreen_the_02.png"),
                   load_image("titlescreen_the_03.png"),
                   load_image("titlescreen_the_04.png"),
                   load_image("titlescreen_the_05.png"),
                   load_image("titlescreen_the_06.png"),
                   load_image("titlescreen_the_07.png"),
                   load_image("titlescreen_the_08.png"),
                   load_image("titlescreen_flag_00.png"),
                   load_image("titlescreen_flag_01.png"),
                   load_image("titlescreen_flag_02.png")]
        
        self.font = pygame.font.Font(filepath("ARNORG.ttf"), 16)
        self.clock = pygame.time.Clock()
        self.menu.update()
        self.menu.draw(self.screen)
        self.main_loop()
  
    def main_loop(self):
        i=1
        j=0
        self.machine_gun_sound=load_sound("machine_gun.ogg")
        self.machine_gun_sound.play()


        while 1:
            for c in self.controls :
                c.menu = self
            self.clock.tick(30)
            events = pygame.event.get()
            for e in events:
                for c in self.controls:
                    c.handle_event(e)           
                if e.type == QUIT:
                    pygame.quit()
                    return
                    
            self.menu.update()
            #-----------------------------------------------
            # to show the sequence of image at the beginning
            if j<len(self.bg)-1:
                i=(i+1)
                j=(i/2)%len(self.bg)
            #-----------------------------------------------
            
            self.screen.blit(self.bg[j], (0, 0))
            ren = self.font.render("COPYRIGHT (C) 2009", 1, (255, 255, 255))
            self.screen.blit(ren, (320-ren.get_width()/2, 310))
       
            self.menu.draw(self.screen)
            pygame.display.flip()
            
            

    
    def Options(self,screen):
        self.menu = ezmenu.CustomMenu()
        
    def go_up(self):
        self.menu.go_up()
    def go_down(self):
        self.menu.go_down()
    def enter(self):
        self.menu.enter()
    def go_right(self):
        pass
    def go_left(self):
        pass
    def back(self):
        pygame.quit()
    
             
class LevelMenu:

    def __init__(self, screen,controls):
        self.controls = controls
        for c in self.controls :
            c.menu = self
        self.screen=screen
        self.inMenu = True
        self.sound = load_sound("menu.ogg",1)
        self.level = 0
        self.x = 0
        self.y = 0
        self.clock = pygame.time.Clock()
        self.number_of_levels = 5
        self.option = 0
        self.width = 1
        self.lvlbuttons = []
        self.color = [0, 0, 0]
        
        for i in range(1,self.number_of_levels+1):
            image = load_image("level%d.png"%i)
            imageb = pygame.transform.scale(image, (image.get_width()/2, image.get_height()/2))
            imaget = pygame.transform.scale(image, (image.get_width()/10, image.get_height()/10))
            self.lvlbuttons.append(("level%d"%i,imaget,imageb))
            
        self.border = load_image("border.png")
            
        self.font=pygame.font.Font(filepath("ARNORG.ttf"), 16)
        self.bg = pygame.Surface((640,480))
        self.bg.fill((0,0,0))
        self.screen.blit(self.bg,(320-100,230-100))
                
        self.update()

    def draw(self):
        """Draw the menu to the surface."""
        self.screen.blit(self.bg,(0,0))
        self.screen.blit(self.lvlbuttons[self.level][2],
                         (320-self.lvlbuttons[self.level][2].get_width()/2,
                          240-self.lvlbuttons[self.level][2].get_height()/2-60)
                         )
    
        i=0
        for b in self.lvlbuttons:
            self.screen.blit(b[1],(16+i*128,350))
            i+=1
            
        self.screen.blit(self.border,(16+self.level*128,350))
        
        
        ren = self.font.render(self.lvlbuttons[self.level][0], 1, (255, 255, 255))
        self.screen.blit(ren, (320-ren.get_width()/2, 310))
        pygame.display.flip()
       

            
    def update(self):
        
        while self.inMenu:
            self.clock.tick(60)
            for e in pygame.event.get():
                if e.type == QUIT:
                    pygame.quit()
                    return
                for c in self.controls:
                    c.handle_event(e)
                    
            self.draw()
            
            
    def go_up(self):
        pass
    def go_down(self):
        pass
    def enter(self):
        self.inMenu = False
        Launch_Game(self.screen,self.controls,self.level+1)
    def go_right(self):
        self.sound.play()
        self.level = (self.level+1)%self.number_of_levels
    def go_left(self):
        self.sound.play()
        self.level = (self.level-1)%self.number_of_levels
    def back(self):
        self.inMenu = False

       
