#! /usr/bin/env python
import pygame
from game.data import *

class CustomMenu:
    """
    
    # PyUML: Do not remove this line! # XMI_ID:_G6I-Qc_IEd6f27AX6AwMPQ
    """

    def __init__(self, *options):
        """Initialise the Menu! options should be a sequence of lists in the
        format of [option_name, option_function]"""      
        self.sound = load_sound("menu.ogg",1)
        self.options = options
        self.x = 0
        self.y = 0
        self.font = pygame.font.Font(None, 32)
        self.option = 0
        self.width = 1
        self.color = [0, 0, 0]
        self.hcolor = [255, 0, 0]
        self.height = len(self.options)*self.font.get_height()
        for o in self.options:
            text = o[0]
            ren = self.font.render(text, 1, (0, 0, 0))
            if ren.get_width() > self.width:
                self.width = ren.get_width()

    def draw(self, surface):
        """Draw the menu to the surface."""
        i=0
        for o in self.options:
            if i==self.option:
                clr = self.hcolor
            else:
                clr = self.color
            text = o[0]
            ren = self.font.render(text, 1, clr)
            if ren.get_width() > self.width:
                self.width = ren.get_width()
            surface.blit(ren, ((self.x+self.width/2) - ren.get_width()/2, self.y + i*(self.font.get_height()+4)))
            i+=1
            
    def update(self):
        """Update the menu and get input for the menu."""
                           
        if self.option > len(self.options)-1:
            self.option = 0
        if self.option < 0:
            self.option = len(self.options)-1
            
    def go_up(self):
        self.sound.play()
        self.option -= 1
    def go_down(self):
        self.sound.play()
        self.option += 1
    def enter(self):
        self.options[self.option][1]()
    def go_right(self):
        pass
    def go_left(self):
        pass

    def set_pos(self, x, y):
        """Set the topleft of the menu at x,y"""
        self.x = x
        self.y = y
        
    def set_font(self, font):
        """Set the font used for the menu."""
        self.font = font
        
    def set_highlight_color(self, color):
        """Set the highlight color"""
        self.hcolor = color
        
    def set_normal_color(self, color):
        """Set the normal color"""
        self.color = color
        
    def center_at(self, x, y):
        """Center the center of the menu at x,y"""
        self.x = x-(self.width/2)
        self.y = y-(self.height/2)
