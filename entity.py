import pygame
import math
import random
from vector import Vec
import util
from globals import Globals
import assets

ALLY = 0
ENEMY = 1
NEUTRAL = 2


class Entity:
    def __init__(self, name, image, image_scale=1, speed=0, team=NEUTRAL, health=None, post_func=None, size=None, solid=False, take_knockback=True, lifetime =-1):
        self.name = name
        self.image_scale = image_scale
        self.speed = speed
        self.team = team

        if health == None:
            self.health = 100
            self.invincible = True
        else:
            self.health = health
            self.invincible = False
        self.max_health = self.health
        self.post_func = post_func
        self.solid = solid
        self.lifetime = lifetime # By default -1 means not maximum lifespan
        self.take_knockback = take_knockback

        self.pos = Vec(0, 0)
        self.vel = Vec(0, 0)
        self.last_collisions = set([])
        self.time = 0 # Total time alive in world
        self.shake_timer = 0 # Timer to track how long to shake sprite
        self.is_player = False

        default_image_size = (Vec(image.get_size()) * image_scale).tuple()
        # Size is the true hitbox size of the entity (doesn't affect iimage)
        if size is None:
            # By default size contains the entire image
            self.size = Vec(default_image_size)
        else:
            # Override hitbox size to custom dimensions
            self.size = Vec(size)

        self.surface = pygame.Surface(default_image_size, pygame.SRCALPHA, 32).convert_alpha()
        self.image_size = Vec(image.get_size())
        self.set_image(image)

    def set_image(self, image):
        self.image = image
        self.image_size = Vec(image.get_size()) * self.image_scale
        self.surface.fill((0, 0, 0, 0))
        self.surface.blit(util.scale_image(image, self.image_scale), (0, 0))

    def rotate(self, angle):
        self.surface = pygame.transform.rotate(self.surface, angle)

    def render(self, surface, pos):
        hitbox = self.hitbox()
        hitbox.center = pos.tuple()
        # Draw healthbar meter
        if self.health < self.max_health and (not self.invincible or self.is_player):
            pos = Vec(hitbox.centerx, hitbox.top - 13)
            bg_width = math.sqrt(self.max_health) * 8

            if self.team == ALLY:
                fg_color = (80, 130, 255)
            else:
                fg_color = (255, 0, 0)

            if self.is_player and self.invincible:
                fg_color = (119, 143, 155)

            util.draw_meter(surface, pos, Vec(bg_width, 6), self.health/self.max_health,  fg_color, (0, 0, 0))

        render_rect = hitbox.copy()
        # Render image in center of hitbox
        render_rect.x += (self.size.x - self.image_size.x) / 2
        render_rect.y += (self.size.y - self.image_size.y) / 2

        if self.shake_timer > 0:
            dist = 2
            render_rect.x += random.randint(-dist, dist)
            render_rect.y += random.randint(-dist, dist)
            self.shake_timer -= Globals.delta_time

        surface.blit(self.surface, render_rect)
        if Globals.debug_mode:
            pygame.draw.rect(surface, (255, 255, 255), hitbox)

    def update(self, world):
        self.time += Globals.delta_time

        if self.vel.mag() > self.speed:
            self.vel = self.vel.norm() * self.speed
        self.pos += self.vel * Globals.delta_time

        # keep entity within world bounds (stays a "radius" length from wall)
        self.pos.x = util.clamp(self.pos.x, self.image_size.x / 2, world.size.x - self.image_size.x / 2)
        self.pos.y = util.clamp(self.pos.y, self.image_size.y / 2, world.size.y - self.image_size.y / 2)

        if self.time > self.lifetime and self.lifetime != -1:
            world.remove(self)

    def colliding(self, other):
        return self.hitbox().colliderect(other.hitbox())

    def collide(self, other, world):
        if self.solid and not other.solid and not isinstance(other, Projectile):
            bottom = self.pos.y + self.size.y/2
            other_bottom = other.pos.y + other.size.y/2
            # Keep base of other entity either above or below base of this entity
            if other_bottom < bottom - 0:
                other.pos.y = min(other_bottom + 20, bottom) - other.size.y/2 - 20
            else:
                other.pos.y = max(other_bottom - 20, bottom) - other.size.y/2 + 20

    def accel(self, v):
        self.vel += v

    def hitbox(self):
        return util.rect_center(self.pos, self.size)

    def hurt(self, amount, world):
        alive = self.health > 0
        if not self.invincible:
            self.health -= amount
            self.health = max(0, self.health)
            self.shake_timer = 200
        elif self.is_player:
            self.shake_timer = 50
        if self.health <= 0 and alive:
            if self.post_func is not None:
                self.post_func(self, world, self.team)
            world.remove(self)

    def __str__(self):
        return "{name} at {pos}".format(name=self.name, pos=self.pos)



def opposes(self, other):
    return ((self.team == ALLY and other.team == ENEMY) \
        or (self.team == ENEMY and other.team == ALLY) \
        or (self.team == ALLY and other.team == NEUTRAL)) \
        and (not other.invincible or other.is_player)


class AI_Entity(Entity):
    def __init__(self, name, image, image_scale, speed, team, health, damage, sight_range, follow_weight, atk_interval, post_func=None, size=None, take_knockback=True):
        super().__init__(name, image, image_scale, speed, team, health, post_func, size, take_knockback=take_knockback)
        self.damage = damage
        self.sight_range = sight_range
        self.follow_weight = follow_weight
        self.atk_interval = atk_interval
        self.atk_timer = self.atk_interval
        self.wandering = False

    def collide(self, other, world):
        super().collide(other, world)
        """if opposes(self, other) and other not in self.last_collisions:
            other.hurt(self.damage, world)
            if other.take_knockback:
                other.accel((other.pos - self.pos) * 0.01)
                pygame.mixer.Sound.play(assets.SFX_HIT_1)

            self.atk_timer = 0"""

    def in_range(self, other):
        return Vec.dist(self.pos, other.pos) <= self.sight_range

    def can_follow(self, other):
        return opposes(self, other) and self.in_range(other)

    def can_spread(self, other):
        return self is not other and self.team is other.team and other.health > 0 and self.in_range(other)

    def wander(self, world):
        if random.random() < 0.005:
            self.wandering = not self.wandering
            self.vel = Vec.polar(0.01, random.randint(0, 360))
        if self.wandering:
            self.accel(self.vel.norm() * 0.01)
            pass
        else:
            self.vel *= 0.95
        # Slightly gravitate towards center of world
        center_dist = (world.size/2) - self.pos
        self.accel(center_dist.norm() * (center_dist.mag() * 0.00001))

    def spread(self, world):
        # Spread away from same team to prevent overlapping sprites
        spread = list(filter(self.can_spread, world.entities))
        for other in spread:
            dir = self.pos - other.pos
            scalar = 1 / (dir.mag() + 0.1)  # Spread away more from closer entities
            self.accel(dir.norm() * scalar)

    def update(self, world):
        follow = list(filter(self.can_follow, world.entities))
        if len(follow) > 0:
            can_attack = self.atk_timer > self.atk_interval
            target = follow[0]

            # approach player, but keep at distance until attack is charged

            target_dir = target.pos - self.pos
            attack_range = 175
            if can_attack:
                self.accel(target_dir.norm() * self.follow_weight)
            else:
                # Keep at a certain radius away from player
                radius_pos = target.pos - target_dir.norm() * attack_range
                radius_dir = radius_pos - self.pos
                magnitude = self.vel.mag()/self.speed + 0.5
                self.accel(radius_dir.norm() * self.follow_weight * magnitude)
            self.atk_timer += Globals.delta_time

            if can_attack and self.colliding(target):
                target.hurt(self.damage, world)
                if target.take_knockback:
                    target.accel((target.pos - self.pos) * 0.05)
                    pygame.mixer.Sound.play(assets.random_hit_sfx())
                self.atk_timer = 0

        else:
            self.wander(world)
        self.spread(world)
        super().update(world)


class Projectile(Entity):
    def __init__(self, name, image, image_scale, speed, team, health, damage, direction, Range, parent=None, blockable=True, rotate=True, post_func=None):
        super().__init__(name, image, image_scale, speed, team, health, post_func=post_func)
        self.damage = damage
        self.vel = direction.norm() * self.speed
        self.range = Range
        if rotate:
            self.rotate(self.vel.angle())
        self.parent = parent
        self.blockable = blockable

        if self.parent is None:
            self.init_vel = Vec(0, 0)
        else:
            self.init_vel = parent.vel
        self.vel += self.init_vel
        self.distance = 0

    def update(self, world):
        super().update(world)
        # accumulate the change in position to get total distance
        relative_vel = self.vel - self.init_vel
        self.distance += abs(relative_vel.mag() * Globals.delta_time)

        # hits border if within "radius" length.
        ground_size = world.size/2
        x, y = self.pos.x, self.pos.y
        w, h = self.size.x, self.size.y
        # wall_dist > 0 when outer edge of sprite is outside world border
        hits_border = x-w/2 <= 0 or y-h/2 <= 0 \
                    or x+w/2 >= world.size.x or y+h/2 >= world.size.y

        if self.distance > self.range or hits_border and self.time > 0:
            if self.post_func is not None:
                self.post_func(self, world, self.team)
            world.remove(self)

    def collide(self, other, world):
        super().collide(other, world)
        opposed = opposes(self, other) and other not in self.last_collisions

        if opposed or other.solid:
            other.shake_timer = 150
            if opposed:
                damage = self.damage
                if self.parent.is_player:
                    damage *= self.parent.damage_multiplier
                other.hurt(damage, world)

            if other.take_knockback:
                other.accel((other.pos - self.pos) * 10)
            if self.blockable:
                if self.post_func is not None:
                    self.post_func(self, world, self.team)
                world.remove(self)


class Pickup(Entity):
    def __init__(self, name, image, image_scale, collide_func, condition=None):
        super().__init__(name, image, image_scale)
        self.collide_func = collide_func
        self.condition = condition

    def hitbox(self):
        # Bob up and down to indicate that this is a pickup
        freq = 0.004
        amp = 8
        offset = Vec(0, math.sin(self.time * freq) * amp)
        return util.rect_center(self.pos + offset, self.size)

    def collide(self, other, world):
        super().collide(other, world)
        if other.is_player:
            collect = True
            if self.condition is not None:
                collect = self.condition()
            if collect:
                self.collide_func()
                world.remove(self)