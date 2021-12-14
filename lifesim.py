#!/usr/bin/python
import sys
import pygame
import math
import random
from vector import Vec

pygame.init()
pygame.key.set_repeat()

clock = pygame.time.Clock()
FPS = 60

# Teams (who follows and can damage who)
ALLY = 0 # against ENEMY
ENEMY = 1 # against ALLY
NEUTRAL = 2 # followed by neither and can damage both



def clamp(value, minval, maxval):
    return max(minval, min(value, maxval))

def round_to(n, base):
    return base * round(float(n)/base)

def dist(self, v):
    return math.hypot(self.x - v.x, self.x - v.x)

def load_image(name):
	image = pygame.image.load('Images/' + name).convert_alpha()
	return image

def screen_pos(v):
    return v + SIZE/2 - player.pos
    
def world_pos(v):
    return v - SIZE/2 + player.pos


SIZE = Vec(1200, 900)
SCREEN = pygame.display.set_mode((SIZE.x, SIZE.y))#, pygame.RESIZABLE)
pygame.display.set_caption('lifesim')
CLOCK = pygame.time.Clock()
FPS = 60


follow_cam = True


class World:
    def __init__(self, size, color_fg, color_bg):
        self.size = size
        self.color_bg = color_bg
        self.entities = []
        self.spawners = []
        self.ground = Entity("Ground", Sprite(size, color_fg))
        self.add(Vec(0, 0), self.ground)

    def update(self):
        for e in self.entities:
            if e is not None:
                e.update()
                for e2 in self.entities:
                    if e2 is not None:
                        if e.colliding(e2):
                            e.collide(e2)
        for s in self.spawners:
            s.update()
        
    def render(self):
        SCREEN.fill(self.color_bg)
        for e in self.entities:
            e.render()
            
    def add(self, pos, e):
        e.pos = pos
        e.world = self
        self.entities.append(e)

    def remove(self, e):
        if e in self.entities:
            self.entities.remove(e)
            if e.world is self:
                e.world = None
            for s in self.spawners:
                for spawn in s.spawned:
                    if spawn == e:
                        s.spawned.remove(e)
        del e

    def create_spawner(self, spawner):
        self.spawners.append(spawner)
        spawner.world = self
        
    def rand_pos(self):
        x = self.size.x
        y = self.size.y
        return Vec(random.randint(-x/2, x/2), random.randint(-y/2, y/2))


class Spawner:
    def __init__(self, interval, spawn_func, max_num):
        self.world = None
        self.interval = interval
        self.time = 0
        self.spawn_func = spawn_func
        self.max_num = max_num
        self.spawned = []
        
    def update(self):
        self.time += delta_time
        if self.time > self.interval and len(self.spawned) < self.max_num:
            self.time = 0
            entity = self.spawn_func()
            self.spawned.append(entity)
            self.world.add(self.world.rand_pos(), entity)


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
        shape(SCREEN, self.color, self.get_hitbox_at(pos))
        
    def get_hitbox_at(self, pos):
        return pygame.Rect((pos.x, pos.y), (self.size.x, self.size.y))


class Stats:
    def __init__(self, speed, health, team, damage = 0, invincible = False, destroy_on_hit = False):
        self.entity = None
        self.speed = speed
        self.health = health
        self.invincible = invincible
        self.damage = damage
        self.team = team
        self.destroy_on_hit = destroy_on_hit

    def update(self):
        self.health = max(0, self.health)
        if self.health <= 0:
            self.destroy()

    def destroy(self):
        if self.entity is player:
            player.stats.speed = 0
        else:
            if self.entity is not None:
                self.entity.world.remove(self.entity)
        print(self.entity.name + " be ded.")

    #def opposes(self, s):
    #    return self.team == ALLY and s.team == ENEMY or \
               #self.team == ENEMY and s.team == ALLY
    
    def attack(self, e):
        if e.has_stats():
            if not e.stats.invincible:
                e.stats.health -= self.damage
            if self.destroy_on_hit:
                self.destroy()


class Entity:
    def __init__(self, name, sprite, stats = None):
        self.name = name
        self.world = None
        self.pos = Vec(0, 0)
        self.sprite = sprite
        self.vel = Vec(0, 0)
        self.stats = stats
        if self.has_stats():
            self.stats.entity = self

    def render(self):
        self.sprite.render_at(self.get_screen_pos())
        
    def update(self):
        self.pos += self.vel * delta_time
        size = self.sprite.size
        world_size = self.world.size
        # keep sprite within world bounds (stays a "radius" length from wall)
        self.pos.x = clamp(self.pos.x,
                           -world_size.x/2 + size.x/2,
                           world_size.x/2 - size.x/2)
        self.pos.y = clamp(self.pos.y,
                           -world_size.y/2 + size.y/2, \
                           world_size.y/2 - size.y/2)
        if self.has_stats():
            self.stats.update()

    def colliding(self, e):
        return self.get_hitbox().colliderect(e.get_hitbox())
        
    def opposes(self, e):
        if self.has_stats() and e.has_stats():
            #return self.stats.opposes(e.stats)
            return self.stats.team == ALLY and e.stats.team == ENEMY or \
                self.stats.team == ENEMY and e.stats.team == ALLY
        
    def collide(self, e):
        #if self.has_stats() and e.has_stats():
            #if self.stats.opposes(e):
        if self.opposes(e):
            self.stats.attack(e)
    
    def get_screen_pos(self):
        # Offset by player position to follow player position
        #screen_pos = screen_pos()#self.pos + SIZE/2 - self.sprite.size/2 - player.pos
        return screen_pos(self.pos) - self.sprite.size/2
    
    def get_hitbox(self, screen = False):
        pos = self.pos - self.sprite.size/2
        if screen:
            pos = self.get_screen_pos()
        return self.sprite.get_hitbox_at(pos)

    def has_stats(self):
        return self.stats is not None

    def __str__(self):
        return "{name} at {pos}".format(name = self.name, pos = self.pos)


class Player(Entity):
    def __init__(self, sprite, stats, weapon):
        super().__init__("Player", sprite, stats)
        self.weapon = weapon

    def update(self):
        self.weapon.update(self, self.stats.team)
        super().update()


class AIEntity(Entity):
    def __init__(self, name, sprite, sight_range, stats):
        super().__init__(name, sprite, stats)
        self.sight_range = sight_range
        self.target = None

    def update(self):
        following_last = self.target is not None
        targetable = list(filter(lambda e: \
            dist(self.pos, e.pos) < self.sight_range and self.opposes(e), \
            self.world.entities))
        
        if len(targetable) > 0:
            self.target = max(targetable, key = lambda e: dist(self.pos, e.pos))
        else:
            self.target = None
            
        if self.target is None:
            if random.randint(0, 1000) < 5:
                self.vel.set_polar(self.stats.speed*0.5, random.randint(0, 360))
        else:
            if self.colliding(self.target):
                self.vel *= 0.99
            else:
                self.vel = (self.target.pos - self.pos).norm() * self.stats.speed
        super().update()


class Projectile(Entity):
    def __init__(self, name, sprite, Range, stats = None):
        super().__init__(name, sprite, stats)
        self.range = Range
        self.distance = 0

    def update(self):
        super().update()
        self.distance += abs(self.vel.get_mag()) # accumulate the change in position to get total distance
        # hits wall if within "radius" length. Disappear
        if self.distance > self.range or not self.get_hitbox() \
        .colliderect(self.world.ground.get_hitbox().inflate(-self.sprite.size.x*2, -self.sprite.size.y*2)):
            self.world.remove(self)


class Weapon():
    def __init__(self, spawn_func, repeat = 1, interval = 0, spread = 0):
        self.spawn_func = spawn_func
        self.interval = interval # time (ms) between repeated shots (times)
        self.timer = 0 # tracks time between shots
        self.repeat = repeat # number of shots per click
        self.current_repeat = 0
        self.firing = False

    def fire(self):
        if self.current_repeat >= self.repeat:
            self.current_repeat = 0
        
    def update(self, entity, team):
        if self.current_repeat < self.repeat:
            if self.timer > self.interval and MOUSE_HELD[0]:
                self.summon_bullet(entity, team)
                self.timer = 0
            self.timer += delta_time

    def summon_bullet(self, entity, team):
        bullet = self.spawn_func(team)
        bullet.vel = (MOUSE_POS - Vec(entity.get_hitbox(True).center)).norm() * bullet.stats.speed
        # If camera is following player, transfer player's velocity to bullet to make it aim towards mouse while moving
        if follow_cam and entity is player:
            bullet.vel += entity.vel
        entity.world.add(entity.pos, bullet)
        
        self.current_repeat += 1



def spawn_enemy():
    return AIEntity("Enemy", Sprite((60, 60), (230, 0, 0)), 300, Stats(0.35, 100, ENEMY, 1))

def spawn_ally():
    return AIEntity("Ally", Sprite((55, 55), (0, 50, 210)), 200, Stats(0.4, 100, ALLY, 1))

def spawn_bullet(team):
    return Projectile("Bullet", Sprite(Vec(15, 15), (25, 25, 75), True), 600, \
                      Stats(1.5, 100, team, 100, invincible = True, destroy_on_hit = True))


def debug(key, world_pos):
    if key == pygame.K_1:
        print("1")
        player.weapon = standard_gun
    if key == pygame.K_2:
        print("2")
        player.weapon = triple_gun
    if key == pygame.K_3:
        print("3")
        player.world.add(world_pos, spawn_enemy())
    if key == pygame.K_4:
        print("4")
        player.world.add(world_pos, spawn_ally())


MOUSE_HELD = []


if __name__ == '__main__':
    
    worlds = []
    
    standard_gun = Weapon(spawn_bullet)
    triple_gun = Weapon(spawn_bullet, 3, 100)


    overworld = World(Vec(1600, 1600), (86, 200, 93), (220, 200, 140))
    worlds.append(overworld)


    player = Player(Sprite(Vec(50, 50), (255, 240, 0), True), Stats(0.5, 100, ALLY, 0), triple_gun)
    overworld.add(Vec(0, 0), player)


    overworld.create_spawner(Spawner(2000, spawn_enemy, 4))
    
    while True:
        delta_time = CLOCK.tick(FPS) # time between each update cycle
        MOUSE_CLICKED = [False, False, False, False, False]
        events = pygame.event.get()

        KEYS = pygame.key.get_pressed()
        SHIFT = KEYS[pygame.KMOD_SHIFT]
        CONTROL = KEYS[pygame.KMOD_CTRL]
        LEFT = KEYS[pygame.K_a] or KEYS[pygame.K_LEFT]
        RIGHT = KEYS[pygame.K_d]or KEYS[pygame.K_RIGHT]
        UP = KEYS[pygame.K_w] or KEYS[pygame.K_UP]
        DOWN = KEYS[pygame.K_s] or KEYS[pygame.K_DOWN]

        MOUSE_HELD = pygame.mouse.get_pressed()
        MOUSE_POS = Vec(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        MOUSE_MOVED = False
        
        for event in events:
            if event.type == pygame.QUIT:
                print("Exited")
                pygame.quit()
                sys.exit()
            #elif event.type == pygame.VIDEORESIZE:
            #    self.screen = pygs= False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                MOUSE_CLICKED[event.button - 1] = True
                print(event.button)
            elif event.type == pygame.MOUSEMOTION:
                MOUSE_MOVED = True
            elif event.type == pygame.KEYDOWN:
                debug(event.key, world_pos(MOUSE_POS))

        horizontal = False
        vertical = False
        vel = Vec(0, 0)
        if LEFT:
            vel -= Vec(1, 0)
            horizontal = True
        if RIGHT:
            vel += Vec(1, 0)
            horizontal = True
        if UP:
            vel -= Vec(0, 1)
            vertical = True
        if DOWN:
            vel += Vec(0, 1)
            vertical = True
            
        # Normalize and set magnitude so moving diagonal is not faster
        vel = vel.norm() * player.stats.speed
        slide = 0.8
        # Control whether each component moves or slides
        if horizontal:
            player.vel.x = vel.x
        else:
            player.vel.x *= slide # slide to a standstill
            
        if vertical:
            player.vel.y = vel.y
        else:
            player.vel.y *= slide

        for world in worlds:
            world.update()
        
        if MOUSE_CLICKED[0]:# or (MOUSE_HELD[0] and MOUSE_MOVED):
            player.weapon.fire()
            
        for world in worlds:
            world.render()


        pygame.display.flip()
