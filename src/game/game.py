#! /usr/bin/env python

import sys
import random

import pygame
from pygame.locals import *

from menu import *
from cutscenes import *
from data import *
from sprites import *
from level import *
from control import *



class Game(object):
    """
    
    # PyUML: Do not remove this line! # XMI_ID:_G4yTYM_IEd6f27AX6AwMPQ
    """

    def __init__(self, screen, controls, level = 4, time_limit = 500, score_limit = 10):
        self.controls = controls
        for c in self.controls:
            c.game = self
            c.menu = None
        self.clock = pygame.time.Clock()
            
            
        pygame.display.set_mode((640,480), pygame.FULLSCREEN)
        self.screen = screen
        
        self.time_limit = time_limit
        self.score_limit = score_limit
        self.time = 0
        
        #CREATION OF THE GAME OBJECT / COLLISION GROUPS
        self.sprites = pygame.sprite.OrderedUpdates()
        self.players = pygame.sprite.OrderedUpdates()
        self.platforms = pygame.sprite.OrderedUpdates()
        self.shots = pygame.sprite.OrderedUpdates()
        self.bonuses = pygame.sprite.OrderedUpdates()
        self.bombs = pygame.sprite.OrderedUpdates()
        self.explosions = pygame.sprite.OrderedUpdates()
        self.playerdies = pygame.sprite.OrderedUpdates()
        Player.platforms = self.platforms
        
        self.end_match_sound=load_sound("applause_end_match.ogg")
        
        self.bg_music=load_sound("bg_circuit.ogg", 0.8)
        self.can = pygame.mixer.Channel(5)
        
        #LOAD PICTURE HERE
        Player1.right_images = [load_image("player1_right_standying_gun_right.png", 32),
                                load_image("player1_right_feet_right_gun_right.png", 32),
                                load_image("player1_right_feet_left_gun_right.png", 32),
                                load_image("player1_died.png", 32),
                                ]
       
        Player2.right_images = [load_image("player2_right_standying_gun_right.png", 32),
                                load_image("player2_right_feet_right_gun_right.png", 32),
                                load_image("player2_right_feet_left_gun_right.png", 32),
                                load_image("player2_died.png", 32),
                                ]
        

        #SETTING THE IMAGES OF GAME OBJECT CLASSES
        Platform.images = {"platform-top.png": load_image("brick.png",16), "platform-middle.png": load_image("brick.png",16)}
        BaddieShot.image = load_image("shot.png")
        Flag.images = [load_image("flag1.png"),load_image("flag2.png")]
        Camp.images = [load_image("Camp1.png"),load_image("Camp2.png")]
        Bonus.image = load_image("heart-full.png")
        
        InvBonus.images = [load_image("machine_gun.png",32),
                           load_image("shotgun.png",32),
                           load_image("bomb.png",16)]
        
        Bomb.image = load_image("bomb.png",32)
        Explosion.image = load_image("Misc_Explosion.png")
        
        #ASSIGNING GAME OBJECT CLASSES TO GROUPS
        Player1.groups = self.sprites, self.players 
        Player2.groups = self.sprites, self.players
        PlayerDie.groups = self.sprites, self.playerdies
        Platform.groups = self.sprites, self.platforms
        BaddieShot.groups = self.sprites, self.shots
        Camp.groups = self.sprites
        Flag.groups = self.sprites
        Bonus.groups = self.sprites, self.bonuses
        InvBonus.groups = self.sprites, self.bonuses
        Bomb.groups = self.sprites, self.bombs
        Explosion.groups = self.sprites, self.explosions

        #INITIALISATION OF THE LEVEL AND INTRO SCENE
        self.lvl   = level
        self.level = Level(self.lvl)
        self.bg = load_image("bg.png")
        self.Camp1 = Camp((0,240),1)
        self.Camp2 = Camp((640,240),2)
        self.flag1 = Flag((16,240),1)
        self.flag2 = Flag((624,240),2)
        self.game_start(screen)      
         
        #PLAYERS APPEAR IN THE SCREEN AFTER THE INTRO SCENE        
        self.player1 = Player1((10,240))
        Player1.init_pos = (10,240)
        self.player2 = Player2((620,240))
        Player2.init_pos = (620,240)

        #ASSIGN CONTROLS TO PLAYERS
        if not len(controls) <= 1:
            self.player1.control = controls[1]
            controls[1].player = self.player1
        else:
            self.player1.control = controls[0]
            controls[0].player = self.player1
        if not len(controls) <= 2:
            self.player2.control = controls[2]
            controls[2].player = self.player2
        else:
            self.player2.control = controls[0]
            controls[0].player = self.player2
        
        #BONUSES APPEAR AFTER INTRO SCEENE
        self.bonus_map = self.level.get_bonus_map()
        self.bonus_map.create_all()
  
        #SPRITES FOR STATS
        self.font = pygame.font.Font(filepath("ARNORG.ttf"), 16)
        self.heart1 = load_image("heart-full.png")
        self.machine_gun = load_image("machine_gun.png",16)#0.25)
        self.machine_gun = pygame.transform.scale(self.machine_gun,(16,16))
        self.bomb = load_image("bomb.png", 16)#0.1)
        self.bomb = pygame.transform.scale(self.bomb,(16,16))
        
        #sounds 
        self.score_sound=load_sound("score_plus_one.ogg")

        self.running = 1
             
        
    def reinit(self):
        self.running = 1
        for s in self.sprites:
            s.kill()
        if not self.bonus_map == None:
            del self.bonus_map
        
        self.level = Level(self.lvl)
        self.Camp1 = Camp((0,240),1)
        self.Camp2 = Camp((640,240),2)
        self.flag1 = Flag((16,240),1)
        self.flag2 = Flag((624,240),2)
        
        
        self.game_start(self.screen)
        for p in self.playerdies:
            p.timer = 70
        self.player1.points = 0
        self.player2.points = 0
       

        self.bonus_map = self.level.get_bonus_map()
        self.bonus_map.create_all()
        
    def endofgame(self, nchannel=5):
        pygame.mixer.Channel(nchannel).stop()
        self.end()
        EndScreen(self.screen, self)  

    def end(self,changeLev=False):
        self.running = 0
        self.change = changeLev
        self.deregister()
        
    def pause(self):
        # pause the channel reproducing the background sound
        self.can.pause()
        PauseScreen(self.screen,self)
          
    def clear_sprites(self):
        for s in self.sprites:
            pygame.sprite.Sprite.kill(s)
            

    def main_loop(self):

        while self.running:
            
            #CHECK FOR END OF GAME
            if not self.time_limit == -1 and self.time >= self.time_limit :
                self.end_match_sound.play()
                self.endofgame()
            if self.player1.points == self.score_limit or self.player2.points == self.score_limit :
                self.end_match_sound.play()
                self.endofgame()

            self.clock.tick(60)
            #self.time += 1
            
            #UPDATE GAME OBJECTS
            self.shots.update()
            self.bombs.update()
            self.explosions.update()
            self.bonus_map.update()
            self.player1.update()
            self.player2.update()
            self.playerdies.update()
             
            #CHECK AND PROCESS COLLISIONS          
            self.player1.collide(self.platforms)
            self.player2.collide(self.platforms)
            self.player1.collide(self.bonuses)
            self.player2.collide(self.bonuses)
            
            if self.player1.rect.colliderect(self.flag2.rect):
                self.player1.take_flag(self.flag2)
            if self.player1.rect.colliderect(self.Camp1.rect):
                if self.player1.flag:
                    self.score_sound.play();
                    self.player1.release_flag()
                    self.player1.score()
                
            if self.player2.rect.colliderect(self.flag1.rect):
                self.player2.take_flag(self.flag1)
            if self.player2.rect.colliderect(self.Camp2.rect):
                if self.player2.flag:
                    self.player2.score()
                    self.score_sound.play();
                    self.player2.release_flag()
   
            for s in self.shots:
                s.collide(self.platforms)
                if not s.rect.colliderect(self.screen.get_rect()):
                    s.kill()
                if s.rect.colliderect(self.player2.rect) and s.owner==self.player1:
                    self.player2.hit(s.damage)
                    s.kill()
                if s.rect.colliderect(self.player1.rect) and s.owner==self.player2:
                    self.player1.hit(s.damage)
                    s.kill()
            
            for s in self.explosions:
                if s.rect.colliderect(self.player1.rect):
                    s.burn(self.player1)
                if s.rect.colliderect(self.player2.rect):
                    s.burn(self.player2)
                  
            #CONTROLS HANDLING   
            for c in self.controls:
                c.handle_state()    
            for e in pygame.event.get():
                for c in self.controls:
                    c.handle_event(e)
                if e.type == QUIT:
                    sys.exit()                        
                                    
            #DRAWINGS
            self.screen.blit(self.bg, (0 , 0))
            self.draw_sprites(self.screen, self.sprites)
            self.draw_stats()
            pygame.display.flip()
            
        #HACK TO GO TO SELECT SCREEN WHEN SELECTING CHANGE LEVEL IN PAUSE    
        return self.change
            
            
    
    def draw_sprites(self, surf, sprites):
        for s in sprites:
            if isinstance(s, Player):
                if not s.dead:
                    surf.blit(s.image, s)
            else:
                surf.blit(s.image, s)
                

    def draw_stats(self):

        if not self.player1==None:
            self.screen.blit(self.bomb, (16,34))    
            ren = self.font.render(" x %d" % (self.player1.inventory.bombs) , 1, (255, 255, 255))
            self.screen.blit(ren, (32, 34))
            color = get_color(self.player1.hp)
            BarRect = pygame.Surface((32,100))
            LifeRect = pygame.Surface((self.player1.hp,16))
            LifeRect.fill(color)
            self.screen.blit(LifeRect,(16,16))
        if not self.player2==None:
            color2 = get_color(self.player2.hp)
            BarRect = pygame.Surface((32,100))
            LifeRect2 = pygame.Surface((self.player2.hp,16))
            LifeRect2.fill(color2)
            self.screen.blit(LifeRect2,(640-16-self.player2.hp,16))
            self.screen.blit(self.bomb, (640 - 60,34))    
            ren = self.font.render(" x %d" % (self.player2.inventory.bombs) , 1, (255, 255, 255))
            self.screen.blit(ren, (640 - 44, 34))

        ren = self.font.render("%d / %d" % (self.player1.points,  self.player2.points) , 1, (255, 255, 255))
        self.screen.blit(ren, (320-(ren.get_width()/2), 16))

    def deregister(self):
        for c in self.controls:
            c.game = None
            
    def game_start(self,screen):
        font = pygame.font.Font(filepath("ARNORG.ttf"), 100)
        text = "3"
        texts = ["GO!!","1","2"]
    
        t=0
        self.screen.blit(self.bg, (0 , 0))
        self.draw_sprites(self.screen, self.sprites)
        pygame.display.flip()
        pygame.time.wait(100)
    

        ren = font.render(text, 1, (255, 255, 0))
        screen.blit(ren, (320-ren.get_width()/2, 240- (font.get_height()/2)))
        
        #self.bg_music.play(loops=-1)
        self.can.play(self.bg_music, loops=-1)
     
        while 1:
            t+=1
            pygame.time.wait(10)
            for e in pygame.event.get():
                for c in self.controls:
                    c.handle_event(e)
                if e.type == QUIT:
                    sys.exit() 
                    
            if t == 70:
                t=0
                if not len(texts)==0:
                    text = texts.pop()
                    self.screen.blit(self.bg, (0 , 0))
                    self.draw_sprites(self.screen, self.sprites)
                    
                    ren = font.render(text, 1, (255, 255, 0))
                    screen.blit(ren, (320-ren.get_width()/2, 240- (font.get_height()/2)))
                        
                else:
                    return
        
            pygame.display.flip()

        
def get_color(hp):
    
    if hp <50 :
        g = int(2*255*hp/100.)
        if g > 255:
            g=255
        elif g < 0:
            g=0
        return pygame.Color(255,g,0,255)
    else:
        r = int(2*255*(1-hp/100.))
        if r > 255:
            r=255
        elif r < 0:
            r=0
        return pygame.Color(r,255,0,255)


class PauseScreen():
    
    def __init__(self,screen,game):
        self.controls = game.controls
        for c in self.controls:
            c.menu = self
            c.game = None
        
        self.sound = load_sound("menu.ogg",1)
        self.clock = game.clock
        self.pause = True
        self.game = game
        self.screen = screen
        self.option = 0
        self.options =["Resume Game","Restart","Change Level","Main Menu","Quit Game"]
        self.color = [255, 255, 255]
        self.hcolor = [255, 0, 0]
        self.font = pygame.font.Font(filepath("ARNORG.ttf"), 16)

        self.width = 1
        self.height = len(self.options)*self.font.get_height()
        for o in self.options:
            text = o
            ren = self.font.render(text, 1, self.color)
            if ren.get_width() > self.width:
                self.width = ren.get_width()
        self.x = 320-(self.width/2)
        self.y = 240-(self.height/2)
        self.bg = pygame.Surface((self.width+64,self.height+64))
        self.bg.fill((0,0,0))
        self.update()
        
    def update(self):
        while self.pause:
            self.clock.tick(30)
            for e in pygame.event.get():
                for c in self.controls:
                    c.handle_event(e)
                if e.type == QUIT:
                    sys.exit()
                        
            if self.option > len(self.options)-1:
                self.option = 0
            if self.option < 0:
                self.option = len(self.options)-1
            
            self.draw()
        
        for c in self.controls:
            c.game = self.game
            
    def draw(self):
        i=0
        
        self.screen.blit(self.bg,(320 - self.bg.get_width()/2,240 - self.bg.get_height()/2))
        
        
        for o in self.options:
            if i==self.option:
                clr = self.hcolor
            else:
                clr = self.color
            text = o
            ren = self.font.render(text, 1, clr)
            self.screen.blit(ren, ((self.x+self.width/2) - ren.get_width()/2, self.y + i*(self.font.get_height()+4)))
            i+=1
            
        pygame.display.flip()
    
    def go_up(self):
        self.sound.play()
        self.option -= 1
    def go_down(self):
        self.sound.play()
        self.option += 1
        
        
    def enter(self, nchannel=5):
        if self.options[self.option] == "Resume Game":
            self.pause = False
            
            pygame.mixer.Channel(nchannel).unpause()
            
            for c in self.controls:
                c.game = self.game
        if self.options[self.option] == "Restart":
            pygame.mixer.Channel(nchannel).stop()
            self.game.reinit()
            self.pause = False
        elif self.options[self.option] == "Change Level":
            pygame.mixer.Channel(nchannel).stop()
            self.game.end(True)
            self.pause = False
        elif self.options[self.option] == "Main Menu":
            pygame.mixer.Channel(nchannel).stop()
            self.game.end()
            self.pause = False
        elif self.options[self.option] == "Quit Game":
            pygame.mixer.Channel(nchannel).stop()
            sys.exit()
        self.deregister()
        
    def go_right(self):
        pass
    def go_left(self):
        pass
    def back(self):
        self.pause = False
        for c in self.controls:
            c.game = self.game
            c.menu = None
        
    def deregister(self):
        for c in self.controls:
            c.menu = None
        
class EndScreen():
    
    def __init__(self,screen,game):
        self.controls = game.controls
        for c in self.controls:
            c.menu = self
            c.game = None
                
        self.clock = game.clock
        self.sound = load_sound("menu.ogg",1)
        self.pause = True
        self.game = game
        self.winner = 0
        self.set_winner()
        self.screen = screen
        self.option = 0
        self.options =["Replay","Next Level","Main Menu","Quit Game"]
        self.color = [255, 255, 255]
        self.hcolor = [255, 0, 0]
        self.font = pygame.font.Font(filepath("ARNORG.ttf"), 16)

        self.width = 1
        self.height = len(self.options)*self.font.get_height()
        for o in self.options:
            text = o
            ren = self.font.render(text, 1, self.color)
            if ren.get_width() > self.width:
                self.width = ren.get_width()
        self.x = 320-(self.width/2)
        self.y = 240-(self.height/2)
        self.bg = pygame.Surface((self.width+64,self.height+64))
        self.bg.fill((0,0,0))
        self.update()
        
    def update(self):
        while self.pause:
            self.clock.tick(30)
            for e in pygame.event.get():
                if e.type == QUIT:
                    sys.exit()
                for c in self.controls:
                    c.handle_event(e)
            if self.option > len(self.options)-1:
                self.option = 0
            if self.option < 0:
                self.option = len(self.options)-1
            
            self.draw()
        for c in self.controls:
            c.game = self.game
    def draw(self):
        i=0
        
        self.screen.blit(self.bg,(320 - self.bg.get_width()/2,240 - self.bg.get_height()/2))
        if not self.winner ==0:
            ren = self.font.render("Player %d  WINS!!" % self.winner, 3, (255,255,255))
        else :
            ren = self.font.render("Spare... :(", 3, (255,255,255))
        self.screen.blit(ren, ((self.x+self.width/2) - ren.get_width()/2, self.y - self.font.get_height()))     
        
        for o in self.options:
            if i==self.option:
                clr = self.hcolor
            else:
                clr = self.color
            text = o
            ren = self.font.render(text, 1, clr)
            self.screen.blit(ren, ((self.x+self.width/2) - ren.get_width()/2, self.y + i*(self.font.get_height()+4)))
            i+=1
            
        pygame.display.flip()
        
    def go_up(self):
        self.option -= 1
        self.sound.play()
    def go_down(self):
        self.option += 1
        self.sound.play()
    def enter(self):
        if self.options[self.option] == "Replay":
            self.pause = False
            self.game.reinit()
            self.deregister()
        elif self.options[self.option] == "Next Level":
            old = self.game.lvl 
            del self.game
            self.game = Game(self.screen,self.controls,(old+1)%3+1)
            self.game.main_loop()
            self.pause = False
            del self
        elif self.options[self.option] == "Main Menu":
            self.game.end()
            self.pause = False
            self.deregister()
        elif self.options[self.option] == "Quit Game":
            sys.exit()
            self.deregister()
    def go_right(self):
        pass
    def go_left(self):
        pass
    def back(self):
        self.game.end()
        self.pause = False 
        
    def set_winner(self):
        if self.game.player1.points > self.game.player2.points:
            self.winner = 1
        elif self.game.player1.points < self.game.player2.points:
            self.winner = 2
        elif self.game.player1.frags > self.game.player2.frags:
            self.winner = 1
        elif self.game.player1.frags < self.game.player2.frags:
            self.winner = 2
        else:
            self.winner = 0
                    
    def deregister(self):
        for c in self.controls:
            c.menu = None

    