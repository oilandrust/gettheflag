#! /usr/bin/env python

import pygame, random
from pygame.locals import *
from data import *
import pymunk as pm
from pymunk import vec2d
from control import *

TOP_SIDE    = 0
BOTTOM_SIDE = 2
LEFT_SIDE   = 3
RIGHT_SIDE  = 1

def speed_to_side(dx,dy):
    if abs(dx) > abs(dy):
        dy = 0
    else:
        dx = 0
    if dy < 0:
        return 0
    elif dx > 0:
        return 1
    elif dy > 0:
        return 2
    elif dx < 0:
        return 3
    else:
        return 0, 0
    
class Collidable(pygame.sprite.Sprite):
    """
    
    # PyUML: Do not remove this line! # XMI_ID:_G49SgM_IEd6f27AX6AwMPQ
    """

    def __init__(self, *groups):
        pygame.sprite.Sprite.__init__(self, groups)
        self.collision_groups = []
        self.xoffset = 0
        self.yoffset = 0

    def collide(self, group):
        if group not in self.collision_groups:
            self.collision_groups.append(group)

    def move(self, dx, dy, collide=True):
        if collide:
            if dx!=0:
                dx, dummy = self.__move(dx,0)
            if dy!=0:
                dummy, dy = self.__move(0,dy)
        else:
            self.rect.move_ip(dx, dy)
        return dx, dy

    def clamp_off(self, sprite, side):
        if side == TOP_SIDE:
            self.rect.top = sprite.rect.bottom
        if side == RIGHT_SIDE:
            self.rect.right = sprite.rect.left
        if side == BOTTOM_SIDE:
            self.rect.bottom = sprite.rect.top
        if side == LEFT_SIDE:
            self.rect.left = sprite.rect.right

    def __move(self,dx,dy):
        oldr = self.rect
        self.rect.move_ip(dx, dy)
        side = speed_to_side(dx, dy)

        for group in self.collision_groups:
            for spr in group:
                if spr.rect.colliderect(self.rect):
                    self.on_collision(side, spr, group)

        return self.rect.left-oldr.left,self.rect.top-oldr.top

    def on_collision(self, side, sprite, group):
        self.clamp_off(sprite, side)

    def draw(self, surf):
        surf.blit(self.image, (self.rect[0]+self.xoffset, self.rect[1]+self.yoffset))
        

        
class Inventory():
    def __init__(self):
        self.weapons = []
        self.bombs = 0
        self.current_weapon = 0
        
    def add_item(self,item):
        if isinstance(item, Bomb):
            self.bombs += 1
        else:
            type = item.type
            for it in self.weapons:
                if it.type == type:
                    it.ammo = item.ammo
                    return it
            self.weapons.append(item)
            return item
            
    def use_bomb(self):
        self.bombs -= 1
        
    def get_weapon(self):
        return self.weapons[self.current_weapon]
    
    def clear(self):
        self.bombs = 0
        self.current_weapon = 0
        del self.weapons[:]
    
    def get_next(self):
        self.current_weapon = (self.current_weapon + 1) % len(self.weapons)
        return self.weapons[self.current_weapon]   
                 
class Player(Collidable):
    """
    
    # PyUML: Do not remove this line! # XMI_ID:_G5L8BM_IEd6f27AX6AwMPQ
    """

    def __init__(self, pos):
        Collidable.__init__(self, self.groups)
        #score storage
        self.points = 0
        self.frags = 0
        
        #Game attributes
        self.flag= None
        self.hp = 100
        self.dead = False
        #Movements
        self.launch_strengh = 0
        self.speed = 3
        self.dir = [0,0]
        self.shoot_dir = [1,0]
        self.init_pos=pos #for respawn
        self.inventory = Inventory()
        self.inventory.add_item(Gun(self))
        self.weapon = self.inventory.get_weapon()
        self.dying = False
        
        #SPRITES
        self.image = self.right_images[0]
        self.rect = self.image.get_rect(topleft = pos)
        self.frame = 0
        self.facing = 1
        
        #Timer for animation
        self.hit_timer = 0
        self.kill_timer = 0
        
        self.counter=0;
        self.c_module=0;
        
        self.extra_life_sound=load_sound("extra_life.ogg", 0.2)
        self.take_bomb_sound=load_sound("take_bomb.ogg")
        self.take_machine_gun_sound=load_sound("m_take.ogg")
        self.take_shot_gun_sound=load_sound("m_take.ogg")
        self.death_sound=load_sound("player_death.ogg")

        
        
    def reinit(self):
        self.points=0
        self.frags=0
        self.hp = 100
        self.launch_strengh = 0
        self.speed = 3
        self.dir = [0,0]
        self.shoot_dir = [0,1]
        self.pos=self.init_pos #for respawn
        
           
    def make_move(self):
        if self.dir[0]>0.8:
            self.dir[0]=1
        if self.dir[1]>0.8:
            self.dir[1]=1
        if self.dir[0]<-0.8:
            self.dir[0]=-1
        if self.dir[1]<-0.8:
            self.dir[1]=-1            
            
        self.move(self.speed*self.dir[0], self.speed*self.dir[1])
        return
        
        if not self.dir[0]==0:
            self.move(self.speed*self.dir[0], 0)
            for p in self.platforms:
                if pygame.sprite.collide_mask(p,self):
                    self.move(-self.speed*self.dir[0], 0)
                    break
        
        if not self.dir[1]==0:
            self.move(0, self.speed*self.dir[1])
            for p in self.platforms:
                if pygame.sprite.collide_mask(p,self):
                    self.move(0, -self.speed*self.dir[1])
                    break
            
    def set_shoot_dir(self,dir):
        self.shoot_dir = dir
        
    def take_flag(self,flag):
        self.flag=flag
        
    def release_flag(self):
        if not self.flag == None :
            self.flag.reinit()
            self.flag = None

    def score(self):
        self.points+=1 
        
    def change_weapon(self):
        #changed
        self.weapon.stop_shooting()
        self.weapon = self.inventory.get_next()
        
    def kill(self):
        self.dead = True
        self.weapon.stop_shooting()
        self.death_sound.play()
        PlayerDie(self)
              
    
    def throw_bomb(self):
        if not self.inventory.bombs == 0:
            self.inventory.use_bomb()
            Bomb(self.rect.center,self.shoot_dir,self.launch_strengh)
            self.launch_strengh = 0
        
       
    def on_collision(self, side, sprite, group):      
        if  isinstance(sprite, Bonus):
            if isinstance(sprite, InvBonus):
                if not sprite.type == "bomb":
                    # before adding weapon
                    self.take_shot_gun_sound.play()
                    self.weapon.stop_shooting()
                    self.weapon=self.inventory.add_item(sprite.get_bonus(self))

                else:
                    self.take_bomb_sound.play()
                    self.inventory.bombs+=1
            elif sprite.type == "lifeup":
                self.heal(10)
                self.extra_life_sound.play()
            sprite.kill()
        else:
            self.clamp_off(sprite, side)
                
    def heal(self,pts):
        if self.hp <= 100 - pts:
            self.hp = self.hp + pts
            
    def hit(self,pt=10):
        if not self.dead:
            self.hp -= pt
            if self.hp <= 0:
                self.hp = 0
                self.kill()
            
    def arm_bomb(self):
        if self.inventory.bombs > 0:
            self.launch_strengh += 1
            
    def shoot(self):
        self.weapon.shoot()
        
    def keep_shooting(self):
        self.weapon.keep_shooting()
        
    def stop_shooting(self):
        self.weapon.stop_shooting() 
        
    def update(self):
        if not self.dead:
            self.make_move()
            self.weapon.update()
                    
            self.frame += 1
            self.hit_timer -= 1             
    
            #ANIMATION
            if (not(self.dir[0]==0 and self.dir[1]==0)):
                self.counter=self.counter+1
                if(self.counter==10): 
                    self.counter=0
                self.c_module=1+(self.counter/5); # so or 1 or 2
    
            else:
                self.counter=0
                self.c_module=0
                
            vec_sdir = pm.Vec2d(self.shoot_dir)
            self.angle = pm.Vec2d.get_angle_between(vec_sdir, (1,0))
            self.image=pygame.transform.rotate(self.right_images[self.c_module], self.angle)
            
            if self.rect.left <= 0:
                self.rect.left = 0
            if self.rect.top <= 0:
                self.rect.top = 0
            if self.rect.right >= 640:
                self.rect.right = 640
            if self.rect.bottom >= 480:
                self.rect.bottom = 480
    
                        
            if not self.flag == None:
                self.flag.set_pos(self.rect.topleft)
            
    def respawn(self):
        self.dead = False
        if not self.flag == None:
            self.flag.reinit()
            self.flag=None
        self.hp = 100
        self.inventory.clear()
        self.inventory.add_item(Gun(self))
        self.weapon = self.inventory.get_weapon()
        self.image = self.right_images[0]
        self.rect = self.image.get_rect(topleft = self.init_pos)
        self.shoot_dir = [1,0]

class Player1(Player):
    """
    
    # PyUML: Do not remove this line! # XMI_ID:_G5gFEM_IEd6f27AX6AwMPQ
    """
    def __init__(self, pos):
        Player.__init__(self, pos)
       
   
class Player2(Player):
    """
    
    # PyUML: Do not remove this line! # XMI_ID:_G5h6QM_IEd6f27AX6AwMPQ
    """
    def __init__(self,pos):
        Player.__init__(self, pos)
        # to fix initialization on player 2 so that he looks on the left
        self.shoot_dir = [-1,0]
        
    def reinit(self):
        Player.reinit(self)
        self.shoot_dir = [-1,0]
        
    def respawn(self):
        Player.respawn(self)
        self.shoot_dir = [-1,0]
        

        
class Weapon():
    """
     # PyUML: Do not remove this line! # XMI_ID:_G5ihVM_IEd6f27AX6AwMPQ
    """
    def __init__(self,owner):
        self.owner = owner
        self.infinite = True
        self.ammo = 0      
        
    def shoot(self):
        if self.ammo == 0:
            return
        if not self.infinite:
            self.ammo -= 1
    def keep_shooting(self):
        pass
    
    def stop_shooting(self):
        pass 
        
    def update(self):
        if self.shooting:
            self.shoot_timer -= 1
            if self.shoot_timer <= 0:
                self.shooting = False
    def get_canon_pos(self):
        dir = pm.Vec2d(self.owner.shoot_dir)
        return self.owner.rect.center + 14 * dir.perpendicular() + 12 * dir
 
class ShotGun(Weapon):
    """
     # PyUML: Do not remove this line! # XMI_ID:_G5k9lc_IEd6f27AX6AwMPQ
    """
    def __init__(self,owner):
        Weapon.__init__(self,owner)
        #shooting variable
        self.type = "shot_gun"
        self.shooting = False
        self.shoot_timer = 0
        self.damage = 15
        
        self.shotgun_sound=load_sound("shotgun.ogg")

        
    def keep_shooting(self):
        pass
        
    def shoot(self):
        if not self.shooting:
            self.shotgun_sound.play()
            self.shooting = True
            self.shoot_timer = 30
            BaddieShot(self.get_canon_pos(),pm.Vec2d(self.owner.shoot_dir).rotated(15),self.owner,self.damage)
            BaddieShot(self.get_canon_pos(),pm.Vec2d(self.owner.shoot_dir).rotated(-15),self.owner,self.damage)
            BaddieShot(self.get_canon_pos(),self.owner.shoot_dir,self.owner,self.damage)

                   
class Gun(Weapon):
    """
     # PyUML: Do not remove this line! # XMI_ID:_G5k9lc_IEd6f27AX6AwMPQ
    """
    def __init__(self,owner):
        Weapon.__init__(self,owner)
        #shooting variable
        self.type = "gun"
        self.shooting = False
        self.shoot_timer = 0        
        # first sound-load
        self.gun_sound=load_sound("gun_sound.ogg")

        self.shoot_freq = 20
        
    def keep_shooting(self):
        pass
        
    def shoot(self):
        if not self.shooting:
            self.gun_sound.play()
            self.shooting = True
            self.shoot_timer = self.shoot_freq
            BaddieShot(self.get_canon_pos(),self.owner.shoot_dir,self.owner)

                
class MachineGun(Weapon):
    """
     # PyUML: Do not remove this line! # XMI_ID:_G5mywc_IEd6f27AX6AwMPQ
    """
    def __init__(self,owner):
        Weapon.__init__(self,owner)
        #shooting variable
        self.shooting = False
        self.shoot_timer = 0
        self.shoot_freq = 8
        self.type = "machine_gun"
        self.damage = 8
        
        self.machine_gun_sound=load_sound("machine_gun.ogg")
        
        self.need_to_start_music_from_keep_shooting=False;
        
    def shoot(self, nchannel=6):
        if not self.shooting:          
            pygame.mixer.Channel(nchannel).stop()
            pygame.mixer.Channel(nchannel).play(self.machine_gun_sound, loops=-1)

            self.shooting = True
            self.shoot_timer = self.shoot_freq
            BaddieShot(self.get_canon_pos(),self.owner.shoot_dir,self.owner)
            
    def stop_shooting(self, nchannel=6):
        pygame.mixer.Channel(nchannel).stop()
        

    def keep_shooting(self, nchannel=6):
        if not self.shooting:
            self.shooting = True
            if not pygame.mixer.Channel(nchannel).get_busy():
                pygame.mixer.Channel(nchannel).play(self.machine_gun_sound, loops=-1)

            self.shoot_timer = self.shoot_freq
            BaddieShot(self.get_canon_pos(),self.owner.shoot_dir,self.owner,self.damage)
        
        
     
class Platform(Collidable):
    """
    
    # PyUML: Do not remove this line! # XMI_ID:_G5rrQM_IEd6f27AX6AwMPQ
    """
    def __init__(self, pos, tile, l, r):
        Collidable.__init__(self, self.groups)
        self.image = self.images["platform-%s.png" % tile]
        self.rect = self.image.get_rect(topleft = pos)
        self.on_left = l
        self.on_right = r                                         
                       

                        
class BaddieShot(Collidable):
    """
    
    # PyUML: Do not remove this line! # XMI_ID:_G5670M_IEd6f27AX6AwMPQ
    """
    def __init__(self, pos,dir,owner,damage = 10):
        Collidable.__init__(self, self.groups)
        self.rect = self.image.get_rect(center = pos)
        [self.dirx ,  self.diry] = dir
        self.owner=owner
        self.damage = damage
    def update(self):
        speed = 10
        self.move(self.dirx*speed,self.diry*speed)     
    def on_collision(self, side, sprite, group):
        if  isinstance(sprite, Platform):
            self.kill()
        
            
class PlayerDie(Collidable):
    """
    
    # PyUML: Do not remove this line! # XMI_ID:_G59YEs_IEd6f27AX6AwMPQ
    """
    def __init__(self, player):
        Collidable.__init__(self, self.groups)
        self.player = player
        self.timer = 0
        if isinstance(player,Player1):
            self.image=pygame.transform.rotate(Player1.right_images[3], self.player.angle)
        else:
            self.image=pygame.transform.rotate(Player2.right_images[3], self.player.angle)

        
        self.rect = self.image.get_rect(topleft = self.player.rect.topleft)

   
    def update(self):
        self.timer+=1
        if self.timer > 70:
            self.player.respawn()
            self.kill()
   
class Flag(Collidable):
    """
    
    # PyUML: Do not remove this line! # XMI_ID:_G5_0VM_IEd6f27AX6AwMPQ
    """
    def __init__(self,pos,team):
        Collidable.__init__(self, self.groups)
        self.init_pos = pos
        self.image = self.images[team-1]
        self.rect = self.image.get_rect(center = pos)
        self.team = team
    def set_pos(self,pos):
        self.rect = self.image.get_rect(center = pos)
    def reinit(self):
        self.set_pos(self.init_pos)
        
class Camp(Collidable):
    """
    
    # PyUML: Do not remove this line! # XMI_ID:_G6C3oM_IEd6f27AX6AwMPQ
    """
    def __init__(self,pos,team):
        Collidable.__init__(self, self.groups)
        self.team=team
        self.image = self.images[team-1]
        self.rect = self.image.get_rect(center = pos)
       
class Bonus(Collidable):
    """
     # PyUML: Do not remove this line! # XMI_ID:_G6EFxc_IEd6f27AX6AwMPQ
    """
    def __init__(self,pos,type,bonusmap):
        Collidable.__init__(self, self.groups)
        self.rect = self.image.get_rect(center = pos)
        self.type = type
        self.bonusmap = bonusmap
        
    def kill(self):
        self.bonusmap.add(self)   
        Collidable.kill(self)
        
        
class Bomb(Collidable):
    """
     # PyUML: Do not remove this line! # XMI_ID:_DRRVdtN-Ed66-a8AKrHVAw
    """
    def __init__(self,pos,dir,strengh=1):
        Collidable.__init__(self, self.groups)
        self.rect = self.image.get_rect(center = pos)
        self.images=[]
        self.images.append(self.image)
        for i in range(1,8):
            self.images.append(pygame.transform.rotate(self.image,45*i))
        self.z = 0
        self.strengh = strengh
        self.t=0
        self.frame = 0
        self.dir = dir
            
    def update(self):
        self.z += 1
        self.t += 1
        
        self.z = -0.5*self.t*self.t+1*self.t*10
        if self.t%2 == 0:
            self.frame+=1
            self.image = self.images[self.frame%8]
        if self.z>0:
            self.image = pygame.transform.scale(self.image,(int(self.z),int(self.z)))
        else:
            Explosion(self.rect.center)
            self.kill()
        
        self.move(4*self.dir[0]*self.strengh/10,4*self.dir[1]*self.strengh/10)
        #+self.rect.width/2
        
class Explosion(Collidable):
    """
     # PyUML: Do not remove this line! # XMI_ID:_DRTxsNN-Ed66-a8AKrHVAw
    """
    def __init__(self,pos):
        Collidable.__init__(self, self.groups)
        self.rect = self.image.get_rect(center = pos)
        self.time_life = 40
        self.hit1 = 0
        self.hit2 = 0
        
        self.bomb_explosion_sound=load_sound("bomb_explosion.ogg",0.1)

        
    def update(self):
        # sound of explosion
        self.bomb_explosion_sound.play()
        self.time_life -=1
        if self.time_life < 0:
            self.kill()
            
        if not self.hit1 == 0:
            self.hit1 -= 1
        if not self.hit2 == 0:
            self.hit2 -= 1

    def burn(self,character):
        if isinstance(character, Player1) and self.hit1 == 0:
            self.hit1 = 7
            dx=self.rect.center[0] - character.rect.center[0]
            dy=self.rect.center[1] - character.rect.center[1]
            l = pm.Vec2d(dx,dy).get_length()
            character.hit(int((48-l)*0.7))
        elif isinstance(character, Player2) and self.hit2 == 0:
            self.hit2 = 7
            dx=self.rect.center[0] - character.rect.center[0]
            dy=self.rect.center[1] - character.rect.center[1]
            l = pm.Vec2d(dx,dy).get_length()
            character.hit(int((48-l)*0.7))
            
        
        
        
class InvBonus(Bonus):
    """
     # PyUML: Do not remove this line! # XMI_ID:_G6FT48_IEd6f27AX6AwMPQ
    """
    def __init__(self,pos,type,bonusmap):
        Bonus.__init__(self,pos,type,bonusmap)
        if self.type == "machine_gun":
            self.image = self.images[0]
        elif self.type == "shot_gun":
            self.image = self.images[1] 
        elif self.type == "bomb":
            self.image = self.images[2]
        self.ammo = 30
        
    def get_bonus(self,player):
        if self.type == "machine_gun":
            return MachineGun(player)
        elif self.type == "shot_gun":
            return ShotGun(player) 
        elif self.type == "bomb":
            return Bomb()           
            
