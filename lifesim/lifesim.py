#!/usr/bin/python
import sys
import pygame
import random
from vector import Vec

pygame.init()
pygame.key.set_repeat()
#pygame.mouse.set_visible(False)

follow_cam = True

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


class Game:
    def __init__(self):
        self.size = Vec(1200, 800)
        self.screen = pygame.display.set_mode((self.size.x, self.size.y))#, pygame.RESIZABLE)
        pygame.display.set_caption('lifesim')
        self.running = True
        #self.fullscreen = False
        #self.events = None
        self.keys = None
        self.KEY_TAPPED = False
        self.KEY_PRESSED = False
        self.CONTROL = False
        self.SHIFT = False
        self.mouse = None
        self.MOUSE_CLICKED = False
        self.MOUSE_PRESSED = False
        mouse_pos = Vec(0, 0)
        #self.BUTTON1 = False
        #self.BUTTON = False
        
        self.worlds = []
        
    def update(self):
        self.check_events()
        self.check_controls()
        for world in self.worlds:
            world.update()
        size = self.screen.get_size()
        #self.size.set(size[0], size[0])
        #self.mouseX, self.mouseY = pygame.mouse.get_pos()
        self.post_update()
        
    def render(self):
        self.screen.fill((86, 200, 93))
        for world in self.worlds:
            world.render()
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
        
    def check_controls(self):
        self.mouse = pygame.mouse.get_pressed()
        self.mouse_pos = Vec(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        self.keys = pygame.key.get_pressed()

        '''self.BUTTON1 = if self.keys[pygame.K_e] or self.keys[pygame.K_RETURN] or self.mouse[self.LEFT]:
        self.BUTTON2 =  self.keys[pygame.K_f] or self.keys[pygame.K_BACKSPACE] or self.mouse[self.RIGHT]:'''        
        self.SHIFT   = pygame.KMOD_SHIFT
        self.CONTROL = pygame.KMOD_CTRL
        self.LEFT    = self.keys[pygame.K_a] or self.keys[pygame.K_LEFT]
        self.RIGHT   = self.keys[pygame.K_d] or self.keys[pygame.K_RIGHT]
        self.UP      = self.keys[pygame.K_w] or self.keys[pygame.K_UP]
        self.DOWN    = self.keys[pygame.K_s] or self.keys[pygame.K_DOWN]
            
    def post_update(self):
        self.KEY_TAPPED = False
        self.MOUSE_CLICKED = False

    #def create(self):
    #    pass


game = Game()


class World:
    def __init__(self, size, color):
        self.size = size
        self.color = color
        self.entities = []
        self.spawners = []
        self.ground = Entity("Ground", Sprite(size, color))
        self.add(Vec(0, 0), self.ground)

    def update(self):
        for e in self.entities:
            e.update()
            for e2 in self.entities:
                if e.colliding(e2):
                    e.collide(e2)
        for s in self.spawners:
            s.update()
        
    def render(self):
        for e in self.entities:
            e.render()
            
    def add(self, pos, e):
        self.entities.append(e)
        e.pos = pos
        e.world = self

    def remove(self, e):
        if e in self.entities:
            self.entities.remove(e)
            if e.world is self:
                e.world = None
        del e

    def create_spawner(self, spawner):
        self.spawners.append(spawner)
        spawner.world = self
        
    def rand_pos():
        x = self.size.x
        y = self.size.y
        return Vec(-x/2, x/2, -y/2, y/2)


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
    def __init__(self, speed, health, team, damage = 0, invincible = True, destroy_on_hit = False):
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
        self.entity.world.remove(self.entity)
        print("ded.")

    def opposes(self, e):
        return self.team == ALLY and e.stats.team == ENEMY or \
               self.team == ENEMY and e.stats.team == ALLY
    
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
        
    def collide(self, e):
        if self.has_stats() and e.has_stats():
            if self.stats.opposes(e):
                self.stats.attack(e)
    
    def get_screen_pos(self):
        screen_pos = self.pos + game.size / 2 - self.sprite.size / 2
        # Offset by player position to follow player position
        if follow_cam:
            screen_pos -= player.pos
        return screen_pos
    
    def get_hitbox(self, screen = False):
        pos = self.pos - self.sprite.size/2
        if screen:
            pos = self.get_screen_pos()
        return self.sprite.get_hitbox_at(pos)#pygame.Rect(pos.to_tuple(), self.size.to_tuple())

    def has_stats(self):
        return self.stats is not None
    
    def __str__(self):
        return "{name} at {pos}".format(name = self.name, pos = self.pos)


class Player(Entity):
    def __init__(self, sprite, stats):
        super().__init__("Player", sprite, stats)
        #self.fire_timer = 0
        #self.fire_interval = 50 # in ms
        #self.fire_times = 0

    def update(self):
        self.move()
        """ self.fire_timer += delta_time
        if game.MOUSE_CLICKED:
            self.fire_times = 0
        if self.fire_timer > self.fire_interval:
            if game.mouse[0] and ((game.MOUSE_PRESSED and self.fire_times < 3) or game.MOUSE_CLICKED):
                self.fire()
                self.fire_timer = 0
                self.fire_times += 1"""
        if game.mouse[0] and game.MOUSE_CLICKED:
            self.fire()
            
        super().update()

    def move(self):
        horizontal = False
        vertical = False
        vel = Vec(0, 0)
        if game.LEFT:
            vel -= Vec(1, 0)
            horizontal = True
        if game.RIGHT:
            vel += Vec(1, 0)
            horizontal = True
        if game.UP:
            vel -= Vec(0, 1)
            vertical = True
        if game.DOWN:
            vel += Vec(0, 1)
            vertical = True
            
        # Normalize and set magnitude so moving diagonal is not faster
        vel = vel.norm() * self.stats.speed
        slide = 0.95
        # Control whether each component moves or slides
        if horizontal:
            self.vel.x = vel.x
        else:
            self.vel.x *= slide # slide to a standstill
            
        if vertical:
            self.vel.y = vel.y
        else:
            self.vel.y *= slide

    def fire(self):
        # add multiple types of weapons (triple, shotgun spread, big boi, 360, small angle range spread)
        #bullet = Projectile("Player Bullet", Sprite(Vec(10, 10), (0, 20, 50), True), 600, Stats(1, 100, ALLY, 5, False, True))
        bullet = spawn_bullet(ALLY)
        bullet.vel = (game.mouse_pos - Vec(self.get_hitbox(True).center)).norm() * bullet.stats.speed
        # If camera is following player, add inertia to particle to make it aim towards mouse while moving
        if follow_cam:
            bullet.vel += self.vel
        self.world.add(self.pos, bullet)


class AIEntity(Entity):
    def __init__(self, name, sprite, sight_range, stats):
        super().__init__(name, sprite, stats)
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
        if self.colliding(player):
            self.vel *= 0.95
        else:
            self.vel = (player.pos - self.pos).norm() * self.stats.speed
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


class Spawner:
    def __init__(self, interval, spawn_function, max_num):
        self.world = None
        self.interval = interval
        self.time = 0
        self.spawn_function = spawn_function
        self.max_num = max_num
        self.spawned = []
        
        
    def update(self):
        self.time += delta_time
        if self.time > self.interval and len(self.spawned) < self.max_num:
            self.time = 0
            entity = self.spawn_function()
            self.spawned.append(entity)
            self.world.add(Vec(random.randint(-100, 100), random.randint(-100, 100)), entity)


overworld = World(Vec(2000, 2000), (220, 200, 140))
game.worlds.append(overworld)


player = Player(Sprite(Vec(50, 50), (255, 240, 0), True), Stats(0.5, 100, ALLY, 0, False))
overworld.add(Vec(0, 0), player)


def spawn_enemy(team = ENEMY):
    return AIEntity("Enemy", Sprite((60, 60), (230, 0, 0)), 500, Stats(0.35, 100, team, 1, False))

def spawn_ally(team = ALLY):
    return AIEntity("Ally", Sprite((55, 55), (0, 50, 210)), 500, Stats(0.4, 100, team, 1, True))

def spawn_bullet(team):
    return Projectile("Bullet", Sprite(Vec(10, 10), (0, 20, 50), True), 600, Stats(1, 100, team, 25, False, True))


overworld.create_spawner(Spawner(2000, spawn_enemy, 4))


def debug():
    #if pygame.keys[pygame.K_g]:
    #    spawn_enemy()
    #if pygame.keys[pygame.K_b]:
    #    spawn_ally()
    pass


print(player)

while game.running:
    delta_time = clock.tick(FPS) # time between each update cycle
    game.update()
    game.render()
    
print("Exited")
pygame.quit()
sys.exit()
