'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "gamelib"
package.
'''
from pygame import joystick
import keyword

import pygame, os
from pygame.locals import *
import control
from menu import menu

def main():
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    #pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()
    pygame.mouse.set_visible(0)
    #pygame.display.set_icon(pygame.image.load(data.filepath("icon.gif")))
    pygame.display.set_caption("Get the Flag!!!")
    screen = pygame.display.set_mode((640, 480))
    
    keyboard = control.Key_Control()
    pygame.joystick.init()
    controls = [keyboard]
    for i in range(0,pygame.joystick.get_count()):
            controls.append(control.Joy_Control(i))
                
    menu.Menu(screen,controls)
    
    
        
