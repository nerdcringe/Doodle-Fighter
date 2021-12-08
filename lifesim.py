#!/usr/bin/python
import pygame
import sys
import random
import math

pygame.init()
pygame.key.set_repeat()
#pygame.mouse.set_visible(False)


follow_cam = True

# Teams
ALLY = 0
ENEMY = 1
NEUTRAL = 1


def debug():
    pass


def clamp(value, minval, maxval):
    return max(minval, min(value, maxval))

def round_to(n, base):
    return base * round(float(n)/base)


def dist(self, v):
    return math.hypot(self.x - v.x, self.x - v.x)

""" 2-component vector class """
class Vec:
    def __init__(self, x, y = None):
        self.set(x, y)

    def set(self, x, y = None):
        if y == None:
                # if two arguments, then use them as components
            try:
                self.x = x.x
                self.y = x.y
            except:
                self.x = x[0]
                self.y = x[1]
                
        else:
            # if one argument, assume it's a vector & copy its components
            self.x = x
            self.y = y
    
    def __add__(self, v):
        return Vec(self.x + v.x, self.y + v.y)
    
    def __sub__(self, v):
        return Vec(self.x - v.x, self.y - v.y)
    
    def __mul__(self, c):
        return Vec(self.x * c, self.y * c)
    
    def __rmul__(self, c):
        return self.__mul__(c)
    
    def __truediv__(self, c):
        return Vec(self.x / c, self.y / c)
    
    def __floordiv__(self, c):
        return Vec(self.x / c, self.y / c)
    
    def __eq__(self, v):
         return self.x == v.x and self.y == v.y
        
    def __neg__(self):
        return Vec(-self.x, -self.y)

    def __str__(self):
        return "({x}, {y})".format(x = self.x, y = self.y)
    
    def get_mag(self):
        return math.sqrt(self.x**2 + self.y**2)
    
    """ Get the normalized vector, keeping the ratio of the components """
    def norm(self):
        mag = self.get_mag()
        if mag == 0:
            return Vec(0, 0)
        return Vec(self.x / mag, self.y / mag)

    def to_tuple(self):
        return (self.x, self.y)
    
    
    #""" Set the magnitude of the vector, preserving the ratio of the components """
    #def set_mag(self, m):
    #    newv = vec(get_norm() * get_mag())
    #    self.set(newv)

    

class Game:
    def __init__(self):
        self.size = Vec(800, 800)
        self.screen = pygame.display.set_mode((self.size.x, self.size.y))#, pygame.RESIZABLE)
        pygame.display.set_caption('lifesim')
        self.running = True
        #self.fullscreen = False
        #self.events = None
        self.keys = None
        self.KEY_TAPPED = False
        self.KEY_PRESSED = False
        #self.CONTROL = False
        #self.SHIFT = False

        self.mouse = None
        self.MOUSE_CLICKED = False
        self.MOUSE_PRESSED = False
        mouse_pos = Vec(0, 0)
        #self.MOUSE_MOVED = False
        #self.MOUSE_L = 0
        #self.MOUSE_R = 2
        #self.MOUSE_M = 1
        #self.BUTTON1 = False
        #self.BUTTON = False
        self.clock = pygame.time.Clock()
        
        self.entities = []
        self.stat_entities = []
        self.worlds = []
        
        
    def update(self):
        self.check_events()
        self.check_controls()

        for entity in self.entities:
            entity.update()

        size = self.screen.get_size()
        #self.size.set(size[0], size[0])
        #self.mouseX, self.mouseY = pygame.mouse.get_pos()
        self.post_update()
        

    def render(self):
        self.screen.fill((86, 200, 93))
        
        for entity in self.entities:
            entity.render()
        pygame.display.flip()
        
    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            #elif event.type == pygame.VIDEORESIZE:
            #    self.screen = pygs= False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.MOUSE_CLICKED = True
                self.MOUSE_PRESSED = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.MOUSE_PRESSED = False
            #if event.type == pygame.MOUSE_MOTION:
            #    self.MOUSEMOVED = True
        
    def check_controls(self):
        self.mouse = pygame.mouse.get_pressed()
        
        self.mouse_pos = Vec(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        
        '''self.BUTTON1 = if self.keys[pygame.K_e] or self.keys[pygame.K_RETURN] or self.mouse[self.LEFT]:
        self.BUTTON2 =  self.keys[pygame.K_f] or self.keys[pygame.K_BACKSPACE] or self.mouse[self.RIGHT]:'''

        #self.MOUSE_L = mouse[self.LEFT]
        #self.MOUSE_R = mouse[self.RIGHT]
        #self.MOUSE_M = mouse[pygame.MIDDLE]
        
        self.keys = pygame.key.get_pressed()
        
        self.SHIFT   = pygame.KMOD_SHIFT
        self.CONTROL = pygame.KMOD_CTRL
        self.LEFT    = self.keys[pygame.K_a] or self.keys[pygame.K_LEFT]
        self.RIGHT   = self.keys[pygame.K_d] or self.keys[pygame.K_RIGHT]
        self.UP      = self.keys[pygame.K_w] or self.keys[pygame.K_UP]
        self.DOWN    = self.keys[pygame.K_s] or self.keys[pygame.K_DOWN]
            
    def post_update(self):
        self.KEY_TAPPED = False
        self.MOUSE_CLICKED = False
        #self.MOUSE_MOVED = False

    def create(self):
        pass

    def add(self, entity):
        self.entities.append(entity)
        if entity.stats is not None:
            self.stat_entities.append(entity)

    def remove(self, entity):
        self.entities.remove(entity)
        if entity.stats is not None:
            self.stat_entities.remove(entity)
        del entity


game = Game()
world_size = Vec(700, 700)


'''class World:
    def __init__(self, size, color):
        self.size = size
        self.color = color
        self.entities = []

    def update(self):
        for entity in self.entities:
            entity.update()
        
    def render(self):
        for entity in self.entities:
            entity.render()'''

class Sprite:
    def __init__(self, size, color, circle = False):
        self.size = Vec(size)
        self.circle = circle
        self.color = color

    def render_at(self, pos):
        if self.circle:
            shape = pygame.draw.ellipse
        else:
            shape = pygame.draw.rect
        
        shape(game.screen, self.color, self.get_hitbox_at(pos))
        
    def get_hitbox_at(self, pos):
        return pygame.Rect(pos.to_tuple(), self.size.to_tuple())


class Stats:
    def __init__(self, speed, health, team, damage = 0, invincible = True):
        self.speed = speed
        self.health = health
        self.invincible = invincible
        self.damage = damage
        self.team = team



class Entity:
    def __init__(self, name, pos, sprite, stats = None):
        self.name = name
        #self.world = None
        self.pos = Vec(pos)
        self.sprite = sprite
        self.vel = Vec(0, 0)
        self.stats = stats

    def render(self):
        self.sprite.render_at(self.get_screen_pos())
        
    def update(self):
        #self.vel = Vec(100, 100)
        self.pos += self.vel
        size = self.sprite.size
        self.pos.x = clamp(self.pos.x, -world_size.x/2 + size.x/2,
                           world_size.x/2 - size.x/2)
        self.pos.y = clamp(self.pos.y, -world_size.y/2 + size.y/2, \
                           world_size.y/2 - size.y/2)
    
    def get_screen_pos(self):
        screen_pos = self.pos + game.size / 2 - self.sprite.size / 2
        # Offset by player position to follow player position
        if follow_cam:
            screen_pos -= player.pos
        return screen_pos
    
    def get_hitbox(self, screen):
        pos = self.pos
        if screen:
            pos = self.get_screen_pos()
        return self.sprite.get_hitbox_at(pos)#pygame.Rect(pos.to_tuple(), self.size.to_tuple())
    
    def __str__(self):
        return "{name} at {pos}".format(name = self.name, pos = self.pos)

    
    
class Player(Entity):
    def __init__(self, pos, sprite, stats = None):
        super().__init__("Player", pos, sprite, stats)

    def update(self):
        self.move()
        if game.mouse[0] and game.MOUSE_CLICKED:
            self.fire()
        super().update()

    def move(self):
        vel = Vec(0, 0)
        pressing = False
        
        if game.LEFT:
            vel -= Vec(1, 0)
            pressing = True
        if game.RIGHT:
            vel += Vec(1, 0)
            pressing = True
        if game.UP:
            vel -= Vec(0, 1)
            pressing = True
        if game.DOWN:
            vel += Vec(0, 1)
            pressing = True
            
        # normalize and set magnitude so moving diagonal is not faster
        if pressing:
            self.vel = vel.norm() * self.stats.speed
        else:
            self.vel *= 0.96

    def fire(self):
        # add multiple types of weapons (triple, shotgun spread, big boi, 360, small angle range spread)
        bullet = Projectile("Player Bullet", self.pos, Sprite(Vec(10, 10), (0, 20, 50)), 600)
        bullet.vel.set((game.mouse_pos - Vec(self.get_hitbox(True).center)).norm() * 2)
        
        # If camera is following player, add inertia to particle to make it aim towards mouse while moving
        if follow_cam:
            bullet.vel += self.vel
            
        game.add(bullet)
        #print(bullet.vel.get_mag())


class AIEntity(Entity):
    def __init__(self, name, pos, sprite, sight_range, stats):
        super().__init__(name, pos, sprite, stats)
        self.sight_range = sight_range
        self.following = False
        self.target_pos = Vec(0, 0)
        
    def update(self):
        '''closest_entity = None
        closest_dist = 1000
        
        for entity in game.stat_entities:
            if self.stats.team == ALLY and entity.stats.team == ENEMY or \
               self.stats.team == ENEMY and entity.stats.team == ALLY:

                dist = dist(self.pos, entity.pos)

                if dist < sight_range: 
                    closest_entity = entity
                    closest_dist = dist()
                    
            if closest_entity is not None:'''
        #self.target_pos = player.pos#closest_entity.pos
        vel = (player.pos - self.pos).norm() * self.stats.speed


class Projectile(Entity):
    def __init__(self, name, pos, sprite, Range, stats = None):
        super().__init__(name, pos, sprite, stats)
        self.range = Range
        self.distance = 0

    def update(self):
        super().update()
        self.distance += abs(self.vel.get_mag()) # accumulate the change in position to get total distance

        if self.distance > self.range:
            game.remove(self)


    #def update(self):
        

game.add(Entity("Ground", Vec(0, 0), Sprite(world_size, (220, 200, 140))))

player = Player(Vec(0, 0), Sprite(Vec(50, 50), (255, 240, 0), True), Stats(0.8, 1000, ALLY, 0, False))
game.add(player)

game.add(AIEntity("Enemy", Vec(300, 300), Sprite((75, 75), (90, 110, 90)), 500, Stats(0.6, 1000, ENEMY, 1, False)))

print(player)


#game.entities.append(Entity("e", 50, 50, 100, 100, 255, 240, 0

while game.running:
    game.update()
    game.render()
    
print("Exited")
pygame.quit()
sys.exit()
