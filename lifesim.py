#!/usr/bin/python
import sys
import os
import pygame
import math
import random
from vector import Vec

pygame.init()
pygame.key.set_repeat()

clock = pygame.time.Clock()
FPS = 60

RES_PATH = 'res/'

# Teams (who follows and can damage who)
ALLY = 0 # against ENEMY
ENEMY = 1 # against ALLY
NEUTRAL = 2 # followed by neither and can damage both


def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

def wraparound(value, min_val, max_val):
    Range = min_val - max_val - 1
    if value > max_val:
        value += Range
    elif value < min_val:
        value -= Range
    return value

def round_to(n, base):
    return base * round(float(n)/base)

def dist(self, v):
    return math.hypot(self.x - v.x, self.x - v.x)


main_font = "StayPuft.ttf"
fonts = {}

def write(surface, text, font_name, size, pos, color, center=False):
    if size in fonts:
        Font = fonts[size]
    else:
        Font = pygame.font.Font(os.path.join(RES_PATH, font_name), size)
        fonts[size] = Font
    text = Font.render(text, 1, color)
    
    if center:
        text_rect = text.get_rect(center=(pos.x, pos.y))
    else:
        text_rect = (pos.x, pos.y)
    surface.blit(text, text_rect)


images = {}

def load_image(name):
    # If image has been loaded, use image from dict
    if name in images.keys():
        image = images[name]
    else:
        # Else, add loaded image to dict
        path = os.path.join(RES_PATH, 'img', name)
        image = pygame.image.load(path).convert_alpha()
        images[name] = image

    
    return image


def screen_pos(v):
    return v + SIZE/2 - player.pos
    
def world_pos(v):
    return v - SIZE/2 + player.pos

def rect_center(pos, size):
    rect = pygame.Rect(0, 0, size.x, size.y)
    rect.center = (pos.x, pos.y)
    return rect


SIZE = Vec(0, 0)
SCREEN = None

def set_screen_size(size):
    global SIZE, SCREEN
    SIZE = Vec(size[0], size[1])
    flags = pygame.RESIZABLE
    SCREEN = pygame.display.set_mode((SIZE.x, SIZE.y), flags)

set_screen_size((1200, 900))

pygame.display.set_caption('lifesim')
clock = pygame.time.Clock()
FPS = 60


class World:
    def __init__(self, name, size, color_fg, color_bg):
        self.name = name
        self.size = size
        self.color_bg = color_bg
        self.entities = []
        self.spawners = []
        self.ground = Entity("Ground", Sprite(size, color_fg, False))
        self.border = True

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
        self.ground.render()
        
        self.entities.sort(key = lambda e: e.pos.y + e.sprite.size.y/2)
        
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

    def clamp_pos(self, pos, size):
        # keep entity within world bounds (stays a "radius" length from wall)
        if self.border:
            pos.x = clamp(pos.x, \
                              -self.size.x/2 + size.x/2, \
                               self.size.x/2 - size.x/2)
            pos.y = clamp(pos.y, \
                              -self.size.y/2 + size.y/2, \
                               self.size.y/2 - size.y/2)
        return pos
    
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
    def __init__(self, size, color = None, circle = False, image_name = None, flip = False):
        self.size = size
        self.color = color
        self.circle = circle
        if image_name is not None:
            self.image = load_image(image_name)
            if flip:
                self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.image = None
    
    def render_at(self, pos):
        # Only draw shape if color is specified
        rect = rect_center(pos, self.size)
        if self.color is not None:
            if self.circle:
                shape = pygame.draw.ellipse
            else:
                shape = pygame.draw.rect
            shape(SCREEN, self.color, rect)
            
        if self.image is not None: # Image may be overlayed on shape
            img_surf = pygame.transform.scale(self.image, (int(self.size.x), int(self.size.y)))
            SCREEN.blit(img_surf, rect)

class Stats:
    def __init__(self, speed, max_health, team, damage = 0, invincible = False, destroy_on_hit = False, post_func = None, knockback = 0):
        self.entity = None
        self.speed = speed
        self.max_health = max_health
        self.health = max_health
        self.invincible = invincible
        self.damage = damage
        self.team = team
        self.destroy_on_hit = destroy_on_hit
        self.post_func = post_func
        self.knockback = knockback

    def update(self):
        self.health = max(0, self.health)
        if self.health <= 0:
            self.destroy()

    def opposes(self, e):
        return (self.team == ALLY and e.team == ENEMY) \
            or (self.team == ENEMY and e.team == ALLY) \
            or (self.team == NEUTRAL)
        
    def destroy(self):
        #print(self.entity.name + " be ded.")
        if self.post_func is not None:
            self.post_func(self.entity, self.team)
        if self.entity is player:
            player.dead = True
        else:
            if self.entity is not None:
                if self.entity.world is not None:
                    self.entity.world.remove(self.entity)
    
    def attack(self, e):
        if self.opposes(e.stats):
            if not e.stats.invincible:
                e.stats.health -= self.damage
                e.accel = (e.pos - self.entity.pos).get_norm() * self.knockback
            if self.destroy_on_hit:
                self.destroy()
                    
        if self.destroy_on_hit and e.solid:
            self.destroy()

"""
class PlayerStats(Stats):
    def __init__(self, speed, max_health, team, max_energy):
        super().__init__(speed, max_health, ALLY, damage = 0, invincible = False, destroy_on_hit = False)
        self.energy = max_energy
        self.max_energy = max_energy
        self.money = money
"""


class Entity:
    def __init__(self, name, sprite, stats = Stats(0, 1, NEUTRAL, invincible = True), hitbox = None, solid = False):
        self.name = name
        self.world = None
        self.pos = Vec(0, 0)
        self.sprite = sprite
        self.stats = stats
        self.stats.entity = self
        
        if hitbox is None:
            self.hitbox = Vec(self.sprite.size)
        else:
            self.hitbox = hitbox
            
        self.solid = solid
        self.vel = Vec(0, 0)
        self.accel = Vec(0, 0)

    def render(self):
        self.sprite.render_at(self.get_screen_pos())
        
    def update(self):
        #self.vel += self.accel
        #self.accel *= 0.75
        self.pos += self.vel * delta_time
        self.pos = self.world.clamp_pos(self.pos, self.hitbox)
        
        """size = self.sprite.size
        world_size = self.world.size
        # keep sprite within world bounds (stays a "radius" length from wall)
        self.pos.x = clamp(self.pos.x,
                           -world_size.x/2 + size.x/2,
                           world_size.x/2 - size.x/2)
        self.pos.y = clamp(self.pos.y,
                           -world_size.y/2 + size.y/2, \
                           world_size.y/2 - size.y/2)"""
        self.stats.update()

    def colliding(self, e):
        return self.get_hitbox().colliderect(e.get_hitbox())
        
    def collide(self, e):
        self.stats.attack(e)
    
    def get_screen_pos(self):
        # Offset by player position to follow player position
        return screen_pos(self.pos)
    
    def get_hitbox(self, screen = False):
        pos = self.pos
        if screen:
            pos = screen_pos(self.pos)
        return rect_center(pos, self.hitbox)

    def set_world(self, world):
        self.world.remove(self)
        world.add(Vec(0, 0), self)

    def __str__(self):
        return "{name} at {pos}".format(name = self.name, pos = self.pos)


class Player(Entity):
    def __init__(self, sprite, stats):
        super().__init__("Player", sprite, stats)
        self.dead = False
        #self.inventory = inventory


class AIEntity(Entity):
    def __init__(self, name, sprite, sight_range, stats):
        super().__init__(name, sprite, stats)
        self.sight_range = sight_range
        self.target = None

    def update(self):
        following_last = self.target is not None
        targetable = list(filter(lambda e: \
            dist(self.pos, e.pos) < self.sight_range and self.stats.opposes(e.stats), \
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
                self.vel = (self.target.pos - self.pos).get_norm() * self.stats.speed
        super().update()


class Projectile(Entity):
    def __init__(self, name, sprite, Range, stats, init_vel = Vec(0, 0)):
        super().__init__(name, sprite, stats)
        self.range = Range
        self.distance = 0
        self.init_vel = Vec(0, 0)
        self.lifetime = 0

    def shoot(self, angle, init_vel = Vec(0, 0)):
        self.vel.set_polar(self.stats.speed, angle)
        self.init_vel = init_vel
        self.vel += init_vel

    def update(self):
        super().update()
        # accumulate the change in position to get total distance
        relative_vel = self.vel - self.init_vel
        self.distance += abs(relative_vel.get_mag() * delta_time)

        hits_border = False

        if self.world.border:
            # hits border if within "radius" length.
            outer_pos = Vec(abs(self.pos.x), abs(self.pos.y)) + self.sprite.size/2
            ground_size = self.world.ground.sprite.size/2
            
            # wall_dist > 0 when outer edge of sprite is outside world border
            wall_dist = Vec(abs(outer_pos.x) - abs(ground_size.x), abs(outer_pos.y) - abs(ground_size.y))
            hits_border = (wall_dist.x >= 0 or wall_dist.y >= 0) and self.lifetime > 0
        
        if self.distance > self.range or hits_border:
            self.stats.destroy()
        self.lifetime += 1


class Item():
    def __init__(self, name):
        self.name = name
        self.in_use = False
    def click(self):
        pass
    def update(self, entity, team):
        pass


class SummonerItem(Item):
    
    def __init__(self, name, spawn_func):
        super().__init__(name)
        self.spawn_func = spawn_func
        
    def click(self):
        player.world.add(world_pos(MOUSE_POS), self.spawn_func())
    
    def update(self, entity, team):
        pass


class WeaponItem(Item):
    def __init__(self, name, spawn_func, Range, repeat = 1, interval = 0, spread = 0):
        super().__init__(name)
        self.spawn_func = spawn_func
        self.repeat = repeat # number of shots per click
        self.current_repeat = self.repeat
        self.interval = interval # time (ms) between repeated shots (times)
        self.timer = 0 # tracks time between shots
        self.spread = spread
        self.current_spread = 0
        self.range = Range

    def click(self):
        super().click()
        if self.current_repeat >= self.repeat:
            self.current_repeat = 0
            self.current_spread = -self.spread/2
            self.timer = self.interval
        
    def update(self, entity, team):
        super().update(entity, team)
        if self.current_repeat < self.repeat:
            self.in_use = True
            if self.timer > self.interval:# and MOUSE_HELD[0]:
                self.summon_bullet(entity, team)
                self.timer = 0
                self.current_repeat += 1
                if self.spread != 0:
                    self.current_spread += self.spread/self.repeat
            self.timer += delta_time
        else:
            self.in_use = False

    def summon_bullet(self, entity, team):
        bullet = self.spawn_func(team, self.range)
        pos_diff = MOUSE_POS - Vec(entity.get_hitbox(True).center)
        angle = math.degrees(math.atan2(pos_diff.y, pos_diff.x)) + self.current_spread

        #bullet.vel.set_polar(bullet.stats.speed, math.degrees(math.atan2(pos_diff.y, pos_diff.x)) + self.current_spread)
        
        # Transfer player's velocity to bullet to make it aim towards mouse while moving
        bullet.shoot(angle, entity.vel)
        entity.world.add(entity.pos, bullet)


class Pickup(Entity):
    def __init__(self, name, sprite, func):
        super().__init__(name, sprite)
        self.func = func

    def collide(self, e):
        if e is player:
            self.func()
        super().collide()



class Inventory():
    def __init__(self):
        self.contents = {
            triple_gun: 100,
            shotgun: 100,
            grenade: 100,
            ally_summoner: 100
        }

        self.index = 0
        self.selected = None
    
    def add(self, item, quantity):
        self.contents[item] += quantity

    def has_item():
        if item in self.inventory.keys():
            return self.inventory[item] > 0
        return False

    def remove(self, item):
        if has_item(item):
            self.contents[item] -= 1

    def update(self, clicked, scroll):
        if scroll != 0:
            self.index += clamp(scroll, -1, 1)
            
        self.index = wraparound(self.index, 0, len(inventory.contents) - 1)
        self.selected = items[self.index]
        
        if self.selected is not None:
            if clicked:
                self.selected.click()
            self.selected.update(player, player.stats.team)
    


def spawn_enemy(team = ENEMY):
    return AIEntity("Enemy", Sprite(Vec(60, 60), (230, 60, 50)), 400, Stats(0.35, 100, team, 0.5))

def spawn_ally(team = ALLY):
    return AIEntity("Ally", Sprite(Vec(55, 55), (40, 100, 230)), 300, Stats(0.4, 100, team, 0.5))


def spawn_bullet(team, Range):
    return Projectile("Bullet", Sprite(Vec(12, 12), (10, 10, 40), True), Range, \
                      Stats(0.9, 100, team, damage = 20, invincible = True, destroy_on_hit = True, knockback = 0.0))

def spawn_grenade(team, Range):
    return Projectile("Grenade", Sprite(Vec(16, 16), (25, 25, 75), False), Range, \
                      Stats(0.75, 100, team, damage = 0, invincible = True, destroy_on_hit = True, post_func = explode))

def spawn_fragment(team, Range):
    return Projectile("Fragment", Sprite(Vec(30, 30), (240, 160, 50), True), Range, \
                      Stats(0.25, 100, NEUTRAL, damage = 4, invincible = True, destroy_on_hit = False, knockback = 0.0))


def explode(entity, team):
    for i in range(6):
        angle = i * 60
        fragment = spawn_fragment(team, 100)
        fragment.vel.set_polar(fragment.stats.speed, angle)
        player.world.add(entity.pos, fragment)
        


def debug(key, mouse_world_pos):
    if key == pygame.K_j:
        player.world.add(mouse_world_pos, spawn_enemy())
    if key == pygame.K_k:
        player.world.add(mouse_world_pos, spawn_ally())
    if key == pygame.K_h:
        player.dead = False
        player.stats.health += 100
    elif key == pygame.K_b:
        index = worlds.index(player.world) - 1
        index = wraparound(index, 0, len(worlds) - 1)
        player.set_world(worlds[index])
        
    elif key == pygame.K_n:
        index = worlds.index(player.world) + 1
        index = wraparound(index, 0, len(worlds) - 1)
        player.set_world(worlds[index])
    


MOUSE_HELD = []
#def write(surface, text, fontFace, pos, size, color, center=False):
def render_overlay():
    color = (255, 255, 255)

    stat_texts = [
        "Item: " + inventory.selected.name,
        "World: " + player.world.name,
        "Position: " + str(player.pos.get_rounded()),
        "Health: " + str(max(0, round(player.stats.health))),
    ]
    x = 10
    y = SIZE.y - 10
    for stat in stat_texts:
        y -= 30
        write(SCREEN, stat, main_font, 30, Vec(x, y), color)



while True:
    if __name__ == '__main__':
        
        worlds = []

        overworld = World("Overworld", Vec(2000, 2000), (80, 170, 90), (220, 200, 140))
        worlds.append(overworld)
        city_world = World("City", Vec(2500, 2500), (180, 180, 180), (142, 245, 155))
        worlds.append(city_world)
        cave_world = World("Cave", Vec(2000, 1200), (65, 65, 65), (25, 25, 25))
        worlds.append(cave_world)
        forest_world = World("Forest", Vec(2000, 2000), (35, 75, 65), (13, 46, 37))
        worlds.append(forest_world)


        single_gun = WeaponItem("Single gun", spawn_bullet, 700)
        triple_gun = WeaponItem("Triple gun", spawn_bullet, 450, repeat = 3, interval = 125)
        shotgun = WeaponItem("Shotgun", spawn_bullet, 300, repeat = 3, interval = 0, spread = 25)
        grenade = WeaponItem("Grenade", spawn_grenade, 250)
        ally_summoner = SummonerItem("Spawn Ally", spawn_ally)
        
        items = (
            single_gun,
            triple_gun,
            shotgun,
            grenade,
            ally_summoner
        )
        inventory = Inventory()

        player = Player(Sprite(Vec(55, 55), (255, 240, 0), circle = True, image_name = "meep.png"), Stats(0.5, 200, ALLY, 0, invincible = False))
        overworld.add(Vec(0, 0), player)

        for i in range(8):
            pos = overworld.rand_pos() * 1.75 # random position, spread out from center
            overworld.add(pos, Entity("Tree", Sprite(Vec(150, 150), image_name = "tree.png", flip = random.randint(0, 1)), \
                                      hitbox = Vec(50, 150), solid = True))

        for i in range(20):
            pos = forest_world.rand_pos() * 1.25
            forest_world.add(pos, Entity("Winter Tree", Sprite(Vec(150, 300), image_name = "tree_winter.png", flip = random.randint(0, 1)), \
                                         hitbox = Vec(30, 300), solid = True))

        overworld.create_spawner(Spawner(2000, spawn_enemy, 3))
        city_world.create_spawner(Spawner(1500, spawn_enemy, 4))
        cave_world.create_spawner(Spawner(1000, spawn_enemy, 5))

        inv_slot = 0
        
        while True:
            delta_time = clock.tick(FPS) # time between each update cycle
            MOUSE_CLICKED = [False, False, False, False, False]
            events = pygame.event.get()

            KEYS = pygame.key.get_pressed()
            SHIFT = KEYS[pygame.KMOD_SHIFT]
            CTRL= KEYS[pygame.KMOD_CTRL]
            LEFT = KEYS[pygame.K_a] or KEYS[pygame.K_LEFT]
            RIGHT = KEYS[pygame.K_d]or KEYS[pygame.K_RIGHT]
            UP = KEYS[pygame.K_w] or KEYS[pygame.K_UP]
            DOWN = KEYS[pygame.K_s] or KEYS[pygame.K_DOWN]

            MOUSE_HELD = pygame.mouse.get_pressed()
            MOUSE_POS = Vec(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
            MOUSE_SCROLL = 0
            #MOUSE_MOVED = False
            
            for event in events:
                if event.type == pygame.QUIT:
                    print("Exited")
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    set_screen_size(event.size)
                elif event.type == pygame.MOUSEWHEEL:
                    MOUSE_SCROLL = event.y
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button <= 3:
                        MOUSE_CLICKED[event.button - 1] = True
                #elif event.type == pygame.MOUSEMOTION:
                #    MOUSE_MOVED = True
                elif event.type == pygame.KEYDOWN:
                    debug(event.key, world_pos(MOUSE_POS))

            if KEYS[pygame.K_r]:
                break

            if not player.dead:
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
                    
                # get_normalize and set magnitude so moving diagonal is not faster
                vel = vel.get_norm() * player.stats.speed
                slide = 0.99
                # Control whether each component moves or slides
                if horizontal:
                    vel.x = vel.x
                else:
                    vel.x *= slide # slide to a standstill
                if vertical:
                    vel.y = vel.y
                else:
                    vel.y *= slide
                player.vel = vel
            else:
                player.vel = Vec(0, 0)

            inventory.update(MOUSE_CLICKED[0], MOUSE_SCROLL)

            player.world.update()
            player.world.render()
            
            render_overlay()

            pygame.display.flip()
