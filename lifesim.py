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
ALLY = 0            # Follows and damages ENEMY
ENEMY = 1           # Follows and damages ALLY
NEUTRAL = 2         # Follows BOTH (if has AI) and damages BOTH

show_hitboxes = False

SIZE = Vec(0, 0)
SCREEN = None
GAME_SURFACE = None
OVERLAY_SURFACE = None

main_font = "StayPuft.ttf"
fonts = {}

images = {}


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


def set_screen_size(size):
    global SIZE, SCREEN, GAME_SURFACE, OVERLAY_SURFACE
    SIZE = Vec(size[0], size[1])
    flags = pygame.RESIZABLE
    SCREEN = pygame.display.set_mode(size, flags)
    GAME_SURFACE = pygame.Surface(size)
    OVERLAY_SURFACE = pygame.Surface(size, pygame.SRCALPHA, 32)
    

set_screen_size((1200, 900))
pygame.display.set_caption('lifesim')
pygame.mouse.set_visible(False)


def screen_pos(v):
    return v + SIZE/2 - player.pos
    
def world_pos(v):
    return v - SIZE/2 + player.pos

def rect_center(pos, size):
    rect = pygame.Rect(0, 0, size.x, size.y)
    rect.center = (pos.x, pos.y)
    return rect


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

def draw_cursor(surface):
    size = Vec(58, 58)
    cursor = pygame.transform.scale(current_cursor, (size.x, size.y))
    pos = MOUSE_POS
    
    if current_cursor == CURSOR_PLACE:
        #pos = Vec(MOUSE_POS.x, MOUSE_POS.y - size.y/2)
        pos = Vec(MOUSE_POS + size/2)
        
    rect = rect_center(pos, size)
    surface.blit(cursor, rect)



current_cursor = None
CURSOR_TARGET = load_image("cursor_target.png")
CURSOR_PLACE = load_image("cursor_place.png")


IMG_PLAYER_ALIVE = load_image("player_alive.png")
IMG_PLAYER_DEAD = load_image("player_dead.png")


class World:
    def __init__(self, name, size, color_fg, color_bg):
        self.name = name
        self.size = size
        self.color_fg = color_fg
        self.color_bg = color_bg
        self.entities = []
        self.spawners = []
        
        self.border = True

    def update(self):
        for e in self.entities:
            if e is not None:
                e.update()
        for e1 in self.entities:
            if e1 is not None:
                for e2 in self.entities:
                    if e2 is not None and e1 != e2:
                        if e1.colliding(e2):
                            e1.collide(e2)
        for s in self.spawners:
            s.update()

    def render(self, surface):
        surface.fill(self.color_bg)
        pygame.draw.rect(surface, self.color_fg, rect_center(screen_pos(Vec(0, 0)), self.size))

        self.entities.sort(key = lambda e: e.pos.y + e.size.y/2)
        
        for e in self.entities:
            e.render(surface)
            
    def add(self, pos, e):
        if e.world is not None:
            e.world.remove(e)
        e.pos = Vec(pos)
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
        #del e

    def create_spawner(self, spawner):
        self.spawners.append(spawner)
        spawner.world = self

    def clamp_pos(self, pos, size):
        # keep entity within world bounds (stays a "radius" length from wall)
        if self.border:
            pos.x = clamp(pos.x, -self.size.x/2 + size.x/2, \
                                  self.size.x/2 - size.x/2)
            pos.y = clamp(pos.y, -self.size.y/2 + size.y/2, \
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
            entity = self.spawn_func(self)
            self.spawned.append(entity)
            self.world.add(self.world.rand_pos(), entity)


class Sprite:
    def __init__(self, size, color = None, circle = False, image_name = None, flip = False, offset = Vec(0, 0)):
        self.size = Vec(size)
        self.color = color
        self.circle = circle
        if image_name is None:
            self.image = None
        else:
            self.image = load_image(image_name)
            if flip and random.randint(1, 2) == 1:
                    self.image = pygame.transform.flip(self.image, True, False)
        self.offset = offset
        self.shake_timer = 0 # Timer to track how long to shake sprite
    
    def render_at(self, surface, pos):
        # Only draw shape if color is specified
        rect = rect_center(pos, self.size)
        
        if self.shake_timer > 0:
            shake_dist = 2
            rect.x += random.randint(-shake_dist, shake_dist)
            rect.y += random.randint(-shake_dist, shake_dist)
            self.shake_timer -= delta_time

        if self.color is not None:
            if self.circle:
                shape = pygame.draw.ellipse
            else:
                shape = pygame.draw.rect
            shape(surface, self.color, rect)
        if self.image is not None: # Image may be overlayed on shape
            img_surf = pygame.transform.scale(self.image, (int(self.size.x), int(self.size.y)))
            surface.blit(img_surf, rect)
            
    def shake(self):
        self.shake_timer = 75
    


class Stats:
    def __init__(self, speed, max_health, team, damage = 0, invincible = False, post_func = None, knockback = 0, mass = 1):
        self.entity = None
        self.speed = speed
        self.max_health = max_health
        self.health = max_health
        self.invincible = invincible
        self.damage = damage
        self.team = team
        self.post_func = post_func
        self.knockback = knockback
        self.mass = mass
        self.destroyed = False

    def update(self):
        self.health = max(0, self.health)
        if self.health <= 0:
            self.destroy()
        else:
            self.destroyed = False

    def is_alive(self):
        return self.health > 0

    def render_health_bar(self, surface):
        if not self.invincible and self.health < self.max_health:# and self.entity is not player:
            hitbox = self.entity.get_hitbox(True)
            total_width = math.sqrt(self.max_health) * 4#hitbox.width
            outline_pos = Vec(hitbox.center[0], hitbox.top - 13)
            
            outline_rect = rect_center(outline_pos, Vec(total_width, 8))
            #pygame.draw.rect(surface, (255, 255, 255), outline_rect.inflate(4, 4))
            pygame.draw.rect(surface, (0, 0, 0), outline_rect)

            fill_rect = outline_rect
            fill_rect.width = total_width * (self.health/ self.max_health)
            if self.team == ALLY:
                fill_color = (25, 150, 255)
            else:
                fill_color = (255, 0, 0)
            pygame.draw.rect(surface, fill_color, fill_rect)

    def follows(self, s):
        # Entities follow opposing entities
        return (self.team == ALLY and s.team == ENEMY) \
            or (self.team == ENEMY and s.team == ALLY)
    
    def damages(self, s):
        # Entities damage enemy, neutral damages all
        return (self.team == ALLY and (s.team == ENEMY or s.team == NEUTRAL)) \
            or (self.team == ENEMY and s.team == ALLY) \
            or self.team == NEUTRAL
    
    def blocks(self, s):
        return ((self.team == ALLY and s.team == ENEMY) \
            or (self.team == ENEMY and s.team == ALLY) \
            or self.team == NEUTRAL or s.team == NEUTRAL)
    
    def attack(self, s):
        if self.damages(s):
            if not s.invincible:
                s.health -= self.damage
                # Shake entity if alive and shake screen if dead
                if s.is_alive() > 0 and isinstance(s, Projectile):
                    s.entity.sprite.shake()
            # Accelerate with knockback force / mass
            s.entity.accel((s.entity.pos - self.entity.pos).get_norm() * (self.knockback/s.mass))
            
    def destroy(self):
        if not self.destroyed:
            self.destroyed = True
            self.health = 0
            if self.post_func is not None:
                self.post_func(self.entity, self.team)
            if self.entity is not player and self.entity is not None:
                if self.entity.world is not None:
                    self.entity.world.remove(self.entity)
                    #print(str(self.entity) + " be ded 4 realzies.")


class Entity:
    def __init__(self, name, sprite, stats = None, size = None, solid = False):
        self.name = name
        self.world = None
        self.pos = Vec(0, 0)
        self.vel = Vec(0, 0)
        self.sprite = sprite
        
        if stats is None:
            self.stats = Stats(0, 1, NEUTRAL, invincible = True)
        else:
            self.stats = stats
        self.stats.entity = self

        if size is None:
            self.size = Vec(self.sprite.size)
        else:
            self.size = size
        
        self.solid = solid

    def render(self, surface):
        self.sprite.render_at(surface, screen_pos(self.pos))
        if show_hitboxes:
            pygame.draw.rect(surface, (255, 255, 255), self.get_hitbox(True))
        self.stats.render_health_bar(surface)
        
    def update(self):
        if self.vel.get_mag() > self.stats.speed:
            self.vel = self.vel.get_norm() * self.stats.speed
        self.pos += self.vel * delta_time
        self.pos = self.world.clamp_pos(self.pos, self.size)
        self.stats.update()
        
    def accel(self, force): # Add to velocity vector, a = f/m
        self.vel += force

    def colliding(self, other):
        return self.get_hitbox().colliderect(other.get_hitbox())
        
    def collide(self, other):
        self.stats.attack(other.stats)
        # Stop other entities passing vertically through the base this entity
        if self.solid and not other.solid:
            bottom = self.pos.y + self.size.y/2
            other_bottom = other.pos.y + other.size.y/2
            if other_bottom < bottom - 5:
                other.pos.y = min(other_bottom + 18, bottom) - other.size.y/2 - 18
            else:
                other.pos.y = max(other_bottom - 10, bottom) - other.size.y/2 + 10
    
    def get_hitbox(self, screen = False):
        pos = self.pos
        if screen:
            pos = screen_pos(pos)
        return rect_center(pos, self.size)
    
    def set_world(self, world):
        world.add(Vec(0, 0), self)

    def __str__(self):
        return "{name} at {pos}".format(name = self.name, pos = self.pos)


class Player(Entity):
    def __init__(self, sprite, stats):
        super().__init__("Player", sprite, stats)
        #self.inventory = inventory
        self.wealth = 0

    def update(self):
        super().update()
        if self.stats.is_alive():
            self.sprite.image = IMG_PLAYER_ALIVE
        else:
            self.sprite.image = IMG_PLAYER_DEAD
            self.vel *= 0.95
        
    def control(self):
        if self.stats.is_alive():
            horizontal = False
            vertical = False
            direction = Vec(0, 0)
            if LEFT:
                direction -= Vec(1, 0)
                horizontal = True
            if RIGHT:
                direction += Vec(1, 0)
                horizontal = True
            if UP:
                direction -= Vec(0, 1)
                vertical = True
            if DOWN:
                direction += Vec(0, 1)
                vertical = True
            self.accel(direction.get_norm() * 0.15)
            if not (horizontal or vertical): 
                self.vel *= 0.85

    def gain_wealth(self, amount):
        self.wealth += amount


class AIEntity(Entity):
    def __init__(self, name, sprite, sight_range, stats, follow_weight):
        super().__init__(name, sprite, stats)
        self.sight_range = sight_range
        self.follow_weight = follow_weight # Force propelling entity towards followed object

        self.wandering = True
        self.wander_angle = random.randint(0, 360)
    
    def can_follow(self, e):
        return Vec.dist(self.pos, e.pos) < self.sight_range and self.stats.follows(e.stats) and e.stats.is_alive()

    def can_spread(self, e): #  Spread away from same team to prevent overlap
        return self != e and self.stats.team == e.stats.team and e.stats.is_alive()
        
    def update(self):
        follow = list(filter(self.can_follow, self.world.entities))
        spread = list(filter(self.can_spread, self.world.entities))
        
        # If there is nothing to follow
        if len(follow) == 0:
            # Curve angle of path slightly
            if self.wandering:
                self.vel.set_polar(self.stats.speed*0.5, self.wander_angle)
                self.wander_angle += random.randint(-5, 5)
                self.vel *= 0.85 # Slow down in case not accelerating
                
            if random.randint(0, 1000) < 5: # Randomly change direction and/or stop
                self.wander_angle = random.randint(0, 360)
                self.wandering = not self.wandering
        else:
            self.wandering = False
            for e in follow:
                # Vector towards: desired position - actual position
                if not self.colliding(e):
                    self.accel((e.pos - self.pos).get_norm() * self.follow_weight)
                else:
                    self.vel *= 0.96
                    
        for e in spread:
            # Only spread away from same team
            pos_diff = self.pos - e.pos
            scalar = 1 / (pos_diff.get_mag() + 0.75) # Spread away more from closer entities
            self.accel(pos_diff.get_norm() * scalar)
            
        # Slightly gravitate towards center of world
        center_dist = Vec(0, 0) - self.pos
        self.accel(center_dist.get_norm() * (center_dist.get_mag() * 0.000005))
        super().update()


class Projectile(Entity):
    def __init__(self, name, sprite, Range, stats, blockable = True):
        super().__init__(name, sprite, stats)
        self.range = Range
        self.distance = 0
        self.init_vel = Vec(0, 0)
        self.lifetime = 0
        self.blockable = blockable
        
    def collide(self, e):
        super().collide(e)
        if self.stats.blocks(e.stats):
            e.sprite.shake()
            if self.blockable:
                self.stats.destroy()

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
            ground_size = self.world.size/2
            
            # wall_dist > 0 when outer edge of sprite is outside world border
            wall_dist = Vec(abs(outer_pos.x) - abs(ground_size.x), abs(outer_pos.y) - abs(ground_size.y))
            hits_border = (wall_dist.x >= 0 or wall_dist.y >= 0) and self.lifetime > 0
        
        if self.distance > self.range or hits_border:
            self.stats.destroy()
        self.lifetime += 1


class Pickup(Entity):
    def __init__(self, name, sprite, func, size = None):
        super().__init__(name, sprite, size = size)
        self.func = func
        
    def render(self, surface):
        super().render(surface)
        write(surface, self.name, main_font, 13, screen_pos(self.pos), (255, 255, 255), True)
        
    def collide(self, e):
        super().collide(e)
        if e is player:
            self.func()
            self.stats.destroy()


class Item():
    def __init__(self, name, infinite = False):
        self.name = name
        self.in_use = False
        self.infinite = infinite
        
    def select(self):
        pass
    def click(self):
        pass
    def update(self, entity, team):
        pass


class SummonerItem(Item):
    def __init__(self, name, spawn_func, infinite = False):
        super().__init__(name, infinite)
        self.spawn_func = spawn_func
    
    def select(self):
        global current_cursor
        current_cursor = CURSOR_PLACE
        
    def click(self):
        player.world.add(world_pos(MOUSE_POS), self.spawn_func(self))
    
    def update(self, entity, team):
        pass


class WeaponItem(Item):
    def __init__(self, name, spawn_func, Range, count = 1, repeat = 1, interval = 0, spread = 0, infinite = False):
        super().__init__(name, infinite)
        self.spawn_func = spawn_func
        self.range = Range
        self.count = count                  # number of projectile spawns per shot
        self.repeat = repeat                # number of repeated shots with delay in between
        self.current_repeat = self.repeat
        self.interval = interval            # time (ms) between repeated shots (times)
        self.timer = 0
        self.spread = spread                # total angle (deg) of shot spread 
        self.current_spread = 0
    
    def select(self):
        global current_cursor
        current_cursor = CURSOR_TARGET
        
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
            if self.timer >= self.interval:# and MOUSE_HELD[0]:
                for i in range(self.count):
                    self.summon_bullet(entity, team)
                    if self.spread != 0:
                        self.current_spread += self.spread/(self.count - 1)
                self.timer = 0
                self.current_repeat += 1
            self.timer += delta_time
        else:
            self.in_use = False

    def summon_bullet(self, entity, team):
        bullet = self.spawn_func(team, self.range)
        pos_diff = MOUSE_POS - screen_pos(entity.pos)
        angle = math.degrees(math.atan2(pos_diff.y, pos_diff.x)) + self.current_spread
        
        # Transfer player's velocity to bullet to make it aim towards mouse while moving
        bullet.shoot(angle, entity.vel)
        entity.world.add(entity.pos, bullet)


class Inventory():
    def __init__(self, contents):
        self.contents = contents
        self.index = 0
        self.selected = single_gun
        self.selected.select()
    
    def add(self, item, quantity):
        if item not in self.contents.keys():
            self.contents[item] = quantity
        else:
            self.contents[item] += quantity

    def has_item(self, item):
        if item in self.contents.keys():
            return self.contents[item] > 0
        return False

    def consume(self, item):
        if self.has_item(item) and not self.selected.infinite:
            self.contents[item] -= 1
        if self.contents[item] <= 0:
            self.contents.pop(item)
            self.selected = list(self.contents.keys())[0]

    def update(self, clicked, scroll):
        if scroll != 0:
            increment = clamp(scroll, -1, 1)

            self.index += increment
            self.index = wraparound(self.index, 0, len(inventory.contents) - 1)
            self.selected = list(self.contents.keys())[self.index]
        
        if self.selected is not None:
            if scroll != 0: 
                self.selected.select()  
            if clicked:
                self.selected.click()
                self.consume(self.selected)
            self.selected.update(player, player.stats.team)

    def get_selected_info(self):
        quantity = " * " + str(self.contents[self.selected])
        if self.selected.infinite:
            quantity = ""
        return "Item: " + self.selected.name + quantity



def spawn_rock():
    return Entity("Rock", Sprite(Vec(100, 60), image_name = "rock.png", flip = True), \
            size = Vec(80, 40), solid = True)

def spawn_copper(entity = None):
    sprite = Sprite(Vec(100, 60), image_name = "pickup_copper.png", flip = True)
    stats = Stats(0, 150, NEUTRAL, 0, post_func = lambda self, other: player.gain_wealth(5))
    return Entity("Copper", sprite, stats, size = Vec(80, 40), solid = True)

def spawn_gold(entity = None):
    sprite = Sprite(Vec(100, 60), image_name = "pickup_gold.png", flip = True)
    stats = Stats(0, 200, NEUTRAL, 0, post_func = lambda self, other: player.gain_wealth(10))
    return Entity("Gold", sprite, stats, size = Vec(80, 40), solid = True)

def spawn_tree():
    sprite = Sprite(Vec(175, 175), image_name = "tree.png", flip = True)
    return Entity("Tree", sprite, size = Vec(50, 175), solid = True)

def spawn_winter_tree():
    sprite = Sprite(Vec(150, 300), image_name = "tree_winter.png", flip = True)
    return Entity("Winter Tree", sprite, size = Vec(30, 300), solid = True)


def spawn_enemy(entity = None):
    sprite = Sprite(Vec(75, 75), (210, 50, 15), image_name = "enemy.png")
    stats = Stats(0.45, 100, ENEMY, 0.75, knockback = 0.01, post_func = drop_loot)
    return AIEntity("Enemy", sprite, 500, stats, follow_weight = 0.06)

def spawn_mini_boss(entity = None):
    sprite = Sprite(Vec(100, 100), (150, 25, 5), image_name = "enemy.png")
    stats = Stats(0.575, 400, ENEMY, 1.5, knockback = 0.05, mass = 15)
    return AIEntity("Mini boss", sprite, 1500, stats = stats, follow_weight = 0.0285)

def spawn_ally(entity = None):
    sprite = Sprite(Vec(70, 70), (25, 75, 220))
    stats = Stats(0.44, 100, ALLY, 0.85, knockback = 0.01)
    return AIEntity("Ally", sprite, 400, stats, follow_weight = 0.075)


def spawn_bullet(team, Range):
    sprite = Sprite(Vec(12, 12), (10, 10, 40), True)
    stats = Stats(1.1, 100, team, damage = 25, invincible = True, knockback = 0.625)
    return Projectile("Bullet", sprite, Range, stats, blockable = True)

def spawn_grenade(team, Range):
    sprite = Sprite(Vec(16, 24), (10, 50, 20), True)
    stats = Stats(0.75, 100, team, damage = 0, invincible = True, post_func = explode)
    return Projectile("Grenade", sprite, Range, stats, blockable = True)

def spawn_explosion(team, Range):
    sprite = Sprite(Vec(100, 100), (245, 160, 50), True)
    stats = Stats(0.35, 100, NEUTRAL, damage = 5, invincible = True, knockback = 0.2)
    return Projectile("Explosion", sprite, Range, stats, blockable = False)



def explode(self, team):
    init_angle = random.randint(0, 120)
    for i in range(3):
        angle = (i * 120) + init_angle
        fragment = spawn_explosion(team, 150)
        fragment.shoot(angle)#, entity.vel)
        player.world.add(self.pos, fragment)


def spawn_shotgun_pickup(quantity = 5):
    return Pickup("Shotgun", Sprite(Vec(60, 60), (0, 0, 0)), lambda: inventory.add(shotgun, quantity))

def spawn_triple_gun_pickup(quantity = 5):
    return Pickup("Triple Gun", Sprite(Vec(55, 55), (75, 0, 0)), lambda: inventory.add(triple_gun, quantity))

def spawn_grenade_pickup(quantity = 5):
    return Pickup("Grenade", Sprite(Vec(40, 60), (10, 50, 20), circle = True), lambda: inventory.add(grenade, quantity))


def drop_loot(entity, team):
    chance = random.random()
    if chance > 0.80:
        player.world.add(entity.pos, spawn_grenade_pickup())
    elif chance > 0.35:
        player.world.add(entity.pos, spawn_shotgun_pickup())
    elif chance > 0.25:
        player.world.add(entity.pos, spawn_triple_gun_pickup())
        

def debug(key, mouse_world_pos):
    if key == pygame.K_j:
        player.world.add(mouse_world_pos, spawn_enemy())
    if key == pygame.K_u:
        player.world.add(mouse_world_pos, spawn_mini_boss())
        
    if key == pygame.K_k:
        player.world.add(mouse_world_pos, spawn_ally())
    if key == pygame.K_i:
        player.world.add(mouse_world_pos, spawn_shotgun_pickup())
    if key == pygame.K_o:
        player.world.add(mouse_world_pos, spawn_triple_gun_pickup())
    if key == pygame.K_p:
        player.world.add(mouse_world_pos, spawn_grenade_pickup())
        
    if key == pygame.K_h:
        player.stats.health += 100
        
    elif key == pygame.K_b:
        index = worlds.index(player.world) - 1
        index = wraparound(index, 0, len(worlds) - 1)
        player.set_world(worlds[index])
        
    elif key == pygame.K_n:
        index = worlds.index(player.world) + 1
        index = wraparound(index, 0, len(worlds) - 1)
        player.set_world(worlds[index])

    elif key == pygame.K_v:
        global show_hitboxes
        show_hitboxes = not show_hitboxes
    elif key == pygame.K_m:
        shake_screen(2000)
    

def render_overlay(surface):
    stat_texts = [
        "Entities: " + str(len(player.world.entities)),
        inventory.get_selected_info(),
        "World: " + player.world.name,
        "Wealth: " + str(player.wealth),
        "Position: " + str(player.pos.get_rounded()),
        "Health: " + str(max(0, round(player.stats.health))),
    ]
    y = SIZE.y - 15
    for stat in stat_texts:
        y -= 30
        write(surface, stat, main_font, 30, Vec(10, y), (255, 255, 255))


while True:
    if __name__ == '__main__':
        
        worlds = []
        screen_shake_timer = 0
        screen_shake_distance = 4
        
        overworld = World("Overworld", Vec(2000, 2000), (80, 170, 90), (220, 200, 140))
        worlds.append(overworld)
        city_world = World("City", Vec(2500, 2500), (180, 180, 180), (130, 240, 145))
        worlds.append(city_world)
        cave_world = World("Cave", Vec(2000, 1200), (65, 65, 65), (25, 25, 25))
        worlds.append(cave_world)
        forest_world = World("Forest", Vec(2000, 2000), (35, 75, 65), (13, 46, 37))
        worlds.append(forest_world)

        single_gun = WeaponItem("Single gun", spawn_bullet, 600, infinite = True)
        triple_gun = WeaponItem("Triple gun", spawn_bullet, 450, repeat = 3, interval = 100)
        shotgun = WeaponItem("Shotgun", spawn_bullet, 300, count = 4, spread = 36)
        grenade = WeaponItem("Grenade", spawn_grenade, 350)
        ally_summoner = SummonerItem("Spawn Ally", spawn_ally)
        ally_summoner = SummonerItem("Spawn Ally", spawn_ally)

        items = ( # every possible item
            single_gun,
            triple_gun,
            shotgun,
            grenade,
            ally_summoner
        )

        contents = {
            single_gun: 1,
            #triple_gun: 0,
            #shotgun: 0,
            #grenade: 0,
            ally_summoner: 100
        }
        inventory = Inventory(contents)

        player = Player(Sprite(Vec(65, 65), (255, 240, 0), circle = True, image_name = "player_alive.png"), \
                        Stats(0.55, 200, ALLY, 0, invincible = False))
        overworld.add(Vec(0, 0), player)

        for i in range(12):
            # random position, spread out from center
            overworld.add(overworld.rand_pos() * 1.25, spawn_tree())
        for i in range(5):
            overworld.add(overworld.rand_pos(), spawn_rock())
        for i in range(20):
            forest_world.add(forest_world.rand_pos() * 1.125, spawn_winter_tree())
        for i in range(6):
            forest_world.add(forest_world.rand_pos(), spawn_rock())

        overworld.create_spawner(Spawner(2000, spawn_enemy, 3))
        #city_world.create_spawner(Spawner(1500, spawn_enemy, 4))
        #cave_world.create_spawner(Spawner(1000, spawn_enemy, 5))
        cave_world.create_spawner(Spawner(1000, spawn_copper, 3))
        cave_world.create_spawner(Spawner(1000, spawn_gold, 5))
        
        forest_world.create_spawner(Spawner(5000, spawn_mini_boss, 1))


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
                elif event.type == pygame.KEYDOWN:
                    debug(event.key, world_pos(MOUSE_POS))
            if KEYS[pygame.K_r]:
                break
            
            inventory.update(MOUSE_CLICKED[0], MOUSE_SCROLL)
            player.control()
            player.world.update()
            player.world.render(SCREEN)
            
            OVERLAY_SURFACE.fill((0, 0, 0, 0))
            render_overlay(SCREEN)
            draw_cursor(SCREEN)
                
            #SCREEN.blit(GAME_SURFACE, (0, 0))
            
            #SCREEN.blit(OVERLAY_SURFACE, (0, 0))
            pygame.display.flip()
