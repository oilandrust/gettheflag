import pymunk as pm
from pymunk import vec2d
import pygame
from pygame.locals import *
import data

class Control():
    """
     # PyUML: Do not remove this line! # XMI_ID:_DQt70NN-Ed66-a8AKrHVAw
    """
    def __init__(self, menu= None, game= None, player= None):
        self.player = player
        self.game = game
        self.menu = menu
        self.key_config = None
    def handle_event(self,e):
        pass
    def handle_state(self):
        pass    
  
    
class Key_Control(Control):
    """
     # PyUML: Do not remove this line! # XMI_ID:_DQxmMNN-Ed66-a8AKrHVAw
    """
    def __init__(self, player= None, menu= None, game= None):
        Control.__init__(self, player)
        self.key_config = Key_config()
    def handle_event(self,e):
        if e.type == KEYDOWN:
            if not self.player == None and not self.player.dead:
                if e.key == self.key_config.change_weapon:
                    self.player.change_weapon()
                elif e.key == self.key_config.shoot:
                    self.player.shoot()
                elif e.key == self.key_config.lookup:
                    self.player.set_shoot_dir ([0,-1])
                elif e.key == self.key_config.lookdown:
                    self.player.set_shoot_dir ([0,1])
                elif e.key == self.key_config.lookright:
                    self.player.set_shoot_dir ([1,0])
                elif e.key == self.key_config.lookleft:
                    self.player.set_shoot_dir ([-1,0])
            if not self.menu == None :
                if e.key == self.key_config.MenuDown:
                    self.menu.go_down()
                elif e.key == self.key_config.MenuUp:    
                    self.menu.go_up()
                elif e.key == self.key_config.MenuRight:    
                    self.menu.go_right()
                elif e.key == self.key_config.MenuLeft:    
                    self.menu.go_left()
                elif e.key == self.key_config.MenuOk:
                    self.menu.enter()
                elif e.key == self.key_config.MenuBack:
                    self.menu.back()
                    return
            if not self.game == None :
                if e.key == K_ESCAPE:
                    self.game.pause()
                    
        if e.type == KEYUP:
            if not self.player == None and not self.player.dead:
                if e.key == self.key_config.bomb:
                    self.player.throw_bomb()
                if e.key == self.key_config.shoot:
                    self.player.stop_shooting()
                
    def handle_state(self):
        if not self.player == None and not self.player.dead:
            key = pygame.key.get_pressed()
            
            dx , dy = 0 , 0
            dsx , dsy = 0 , 0
           
            if key[self.key_config.left]:
                dx = -1
            if key[self.key_config.right]:
                dx = 1
            if key[self.key_config.up]:
                dy = -1
            if key[self.key_config.down]:
                dy = 1
                
            if key[self.key_config.lookleft]:
                dsx = -1
            elif key[self.key_config.lookright]:
                dsx = 1
            if key[self.key_config.lookup]:
                dsy = -1
            elif key[self.key_config.lookdown]:
                dsy = 1
                
            if key[self.key_config.shoot]:
                self.player.keep_shooting()
            if key[self.key_config.bomb]:
                self.player.arm_bomb()
                
            if not dx == 0 or not dy == 0:
                self.player.dir = pm.Vec2d(dx,dy).normalized()
                if dsx == 0 and dsy == 0 and not key[self.key_config.hold_dir]:
                    self.player.set_shoot_dir (pm.Vec2d(dx,dy).normalized())
            else:
                self.player.dir = [0,0]
                if not dsx == 0 or not dsy == 0:
                    self.player.set_shoot_dir (pm.Vec2d(dsx,dsy).normalized())
                   

class Joy_Control(Control):
    """
     # PyUML: Do not remove this line! # XMI_ID:_DQzbYdN-Ed66-a8AKrHVAw
    """
    def __init__(self,joy_number, menu = None, game = None, player = None):
        Control.__init__(self, player)
        self.joy_id = joy_number
        self.joy = pygame.joystick.Joystick(joy_number)
        pygame.joystick.Joystick(joy_number).init()
        self.joy.init()
        self.config = Joy_config(self.joy.get_name())
        
        
    def handle_event(self,e):
        if e.type == JOYBUTTONDOWN:
            if not self.menu == None:
                if e.button == self.config.MenuDown and e.joy==self.joy_id:
                    self.menu.go_down()
                elif e.button == self.config.MenuUp and e.joy==self.joy_id:    
                    self.menu.go_up()
                elif e.button == self.config.MenuOk and e.joy==self.joy_id:
                    self.menu.enter()
                elif e.button == self.config.MenuBack and e.joy==self.joy_id:
                    self.menu.back()
            if not self.game == None:
                if e.button == self.config.Pause and e.joy==self.joy_id:
                    self.game.pause()
            if not self.player == None and not self.player.dead:    
                if e.button == self.config.shoot and e.joy==self.joy_id:
                    self.player.shoot() 
                elif e.button == self.config.change and e.joy==self.joy_id:
                    self.player.change_weapon()
                
        if e.type == JOYBUTTONUP:  
            if not self.player == None and not self.player.dead:  
                if e.button == self.config.bomb and e.joy==self.joy_id:
                    self.player.throw_bomb() 
                if e.button == self.config.shoot and e.joy==self.joy_id:
                    self.player.stop_shooting()            
                
    def handle_state(self):
        if not self.game == None:
            pass
        if not self.menu == None:
            pass
        if not self.player == None and not self.player.dead: 
            newdir =  pm.Vec2d(self.joy.get_axis(self.config.axMovex),self.joy.get_axis(self.config.axMovey)) 
            lengh =newdir.get_length_sqrd()
            if lengh>0.1:
                self.player.dir = newdir.normalized()
            else:
                self.player.dir =[0,0]
                
            newlookdir = pm.Vec2d(self.joy.get_axis(self.config.axLookx),self.joy.get_axis(self.config.axLooky))
            if newlookdir.get_length_sqrd()>0.2:  
                self.player.set_shoot_dir (newlookdir.normalized())
            elif lengh>0.1:
                self.player.set_shoot_dir (self.player.dir)
            
            if self.joy.get_button(self.config.shoot):
                self.player.keep_shooting()
            if self.joy.get_button(self.config.bomb):
                self.player.arm_bomb() 
               

class Key_config(object):
    """
    
    # PyUML: Do not remove this line! # XMI_ID:_G5FOU8_IEd6f27AX6AwMPQ
    """
    def __init__(self,up = K_w,down = K_s,right=K_d,left=K_a,shoot = K_RSHIFT,hold_dir = K_k, updir=K_UP, downdir=K_DOWN,rightdir=K_RIGHT,leftdir=K_LEFT,change = K_g,bomb = K_b):
        self.up = up
        self.down = down
        self.right = right
        self.left = left
        self.shoot = shoot   
        self.hold_dir = K_SPACE 
        self.lookup = updir
        self.lookdown = downdir
        self.lookright = rightdir
        self.lookleft = leftdir 
        self.change_weapon = K_BACKSPACE
        self.bomb = K_RETURN
        self.MenuUp  = K_UP
        self.MenuDown  = K_DOWN
        self.MenuRight  = K_RIGHT
        self.MenuLeft  = K_LEFT
        self.MenuOk  = K_RETURN
        self.MenuBack  = K_ESCAPE
        self.Pause = K_ESCAPE
        
class Joy_config(object):
    def __init__(self,joyname):
        f=data.load("JoyConfig.txt", 'r')
        found=False
        print joyname
        
        l=f.readline()
        while l != 'Config:\n':
            print l
            if l.find(joyname)!=-1:
                found = True
            l=f.readline()

        if not found:
            print "Joystick not recognised - Default Configuration, edit JoyConfig.txt to fix it"
            self.axMovex = 0
            self.axMovey = 1
            self.axLookx = 2
            self.axLooky = 3
            self.shoot   = 7
            self.bomb    = 6
            self.change  = 9
            self.MenuUp  = 0
            self.MenuDown  = 1
            self.MenuRight  = 2
            self.MenuLeft  = 3
            self.MenuOk  = 2
            self.MenuBack  = 4
            self.Pause = 3
        else:
            l=f.readline()
            while l.find(joyname)==-1:
                l=f.readline()
            self.axMovex = int(f.readline()[0])
            self.axMovey = int(f.readline()[0])
            self.axLookx = int(f.readline()[0])
            self.axLooky = int(f.readline()[0])
            self.shoot   = int(f.readline()[0])
            self.bomb    = int(f.readline()[0])
            self.change  = int(f.readline()[0])
            self.MenuUp  = int(f.readline()[0])
            self.MenuDown  = int(f.readline()[0])
            self.MenuRight  = int(f.readline()[0])
            self.MenuLeft  = int(f.readline()[0])
            self.MenuOk  = int(f.readline()[0])
            self.MenuBack  = int(f.readline()[0])
            self.Pause = int(f.readline()[0])
            
            
    
        
    