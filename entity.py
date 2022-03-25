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


def opposes(self, other):
    return ((self.team == ALLY and other.team == ENEMY) \
            or (self.team == ENEMY and other.team == ALLY) \
            or (self.team == ALLY and other.team == NEUTRAL)) \
            and (not other.invincible or other.is_player)


class Entity:
    def __init__(self, name, image, image_scale=1, team=NEUTRAL, health=None, solid=False, hitbox_size=None,
                 post_func=None):
        self.name = name
        self.default_image = image
        self.current_image = image
        self.image_scale = image_scale
        self.team = team

        if health == None:
            self.health = 100
            self.invincible = True
        else:
            self.health = health
            self.invincible = False
        self.max_health = self.health
        self.solid = solid
        self.post_func = post_func # Callback to run after death

        self.pos = Vec(0, 0)
        self.vel = Vec(0, 0)
        self.speed = 0
        self.shake_timer = 0  # Timer to track how long to shake sprite
        self.take_knockback = False # Whether to get pushed back when hurt
        self.last_collisions = set([])

        self.world = None
        self.lifetime = -1  # The amount of time able to live before dying. The default value -1 means live forever
        self.time = 0  # Total time alive in world
        self.is_player = False


        default_image_size = (Vec(image.get_size()) * image_scale).tuple()
        # Size is the true hitbox size of the entity (doesn't affect iimage)
        if hitbox_size is None:
            # By default size contains the entire image
            self.size = Vec(default_image_size)
        else:
            # Override hitbox size to custom dimensions
            self.size = Vec(hitbox_size)

        self.surface = pygame.Surface(default_image_size, pygame.SRCALPHA, 32).convert_alpha()
        self.image_size = Vec(image.get_size())
        self.set_image(image)

    def set_image(self, image):
        self.current_image = image
        self.image_size = Vec(image.get_size()) * self.image_scale
        self.surface.fill((0, 0, 0, 0))
        self.surface.blit(util.scale_image(image, self.image_scale), (0, 0))

    def rotate(self, angle):
        self.surface = pygame.transform.rotate(self.surface, angle)

    def render(self, surface, overlay_surface, pos):
        hitbox = self.hitbox()
        hitbox.center = pos.tuple()

        render_rect = hitbox.copy()
        # Render image in center of hitbox
        render_rect.x += (self.size.x - self.image_size.x) / 2
        render_rect.y += (self.size.y - self.image_size.y) / 2

        if self.shake_timer > 0 and not isinstance(self, Projectile):
            dist = 3
            if True:  # not self.is_player:
                render_rect.x += random.randint(-dist, dist)
                render_rect.y += random.randint(-dist, dist)
            self.shake_timer -= Globals.delta_time

        surface.blit(self.surface, render_rect)
        # Draw healthbar
        if self.is_player or not self.invincible:
            if self.health < self.max_health:
                pos = Vec(hitbox.centerx, render_rect.top - 13)
                bg_width = math.sqrt(self.max_health) * 9

                if self.team == ALLY:
                    fg_color = (80, 130, 255)
                else:
                    fg_color = (255, 0, 0)

                if self.is_player and self.invincible:
                    fg_color = (119, 143, 155)

                util.draw_bar(surface, pos, Vec(bg_width, 6), self.health / self.max_health, fg_color, (0, 0, 0))

        if Globals.debug_mode:
            pygame.draw.rect(surface, (255, 255, 255), hitbox, 3)

    def update(self, world):
        self.time += Globals.delta_time

        if self.vel.mag() > self.speed:
            self.vel = self.vel.norm() * self.speed
        self.pos += self.vel * Globals.delta_time

        # keep entity within world bounds (stays a "radius" length from wall) if it is able to move
        # if the entity has 0 speed (doesn't move), then it was placed out of bounds intentionally
        if self.speed != 0:
            self.keep_in_bounds(world)

        if self.time > self.lifetime and self.lifetime != -1:
            world.remove(self)

    def keep_in_bounds(self, world):
        self.pos.x = util.clamp(self.pos.x, self.size.x / 2, world.size.x - self.size.x / 2)

        # Keep bottom 20 pixels inside the world boundaries instead of the entire entity
        # This simulates the depth of the entity, maintaining the illusion of 3D
        self.pos.y = util.clamp(self.pos.y, -self.size.y / 2 + 20, world.size.y - self.size.y / 2)

    def colliding(self, other):
        return self.hitbox().colliderect(other.hitbox())

    def collide(self, other, world):
        if self.solid and not other.solid and not isinstance(other, Projectile):
            bottom = self.pos.y + self.size.y / 2
            other_bottom = other.pos.y + other.size.y / 2
            # Keep base of other entity either above or below base of this entity
            if other_bottom < bottom:
                other.pos.y = min(other_bottom + 20, bottom) - other.size.y / 2 - 20
            else:
                other.pos.y = max(other_bottom - 20, bottom) - other.size.y / 2 + 20

    def accel(self, v):
        self.vel += v

    def hitbox(self):
        return util.rect_center(self.pos, self.size)

    def hurt(self, amount, world):
        alive = self.health > 0
        if not self.invincible:
            self.health -= amount
            self.health = max(0, self.health)
            self.shake_timer = 150
        if self.health <= 0 and alive:
            if self.post_func is not None:
                self.post_func(self, world, self.team)
            world.remove(self)

    def __str__(self):
        return "{name} at {pos}".format(name=self.name, pos=self.pos)


class Portal(Entity):
    """ Sends the player to a desired world, position, or entity when interacted with (SPACE or right click)"""

    def __init__(self, name, image, image_scale, team=NEUTRAL, health=None, hover_message="",
                 to_world=None, to_position=None, to_entity=None, solid=False,
                hitbox_size=None, post_func=None):

        super().__init__(name, image, image_scale, team, health, solid=solid, hitbox_size=hitbox_size, post_func=post_func)
        self.hover_message = hover_message
        self.to_world = to_world
        self.to_position = to_position
        self.to_entity = to_entity
        self.touching_player = False

    def destination_position(self):
        if self.to_position is not None: # Go to position if specified
            return self.to_position
        elif self.to_entity is not None: # Go to entity's position if entity is specified
            return Vec(self.to_entity.pos)
        return None

    def destination_world(self):
        if self.to_entity is not None: # Go to the entity's world if entity is specified
            return self.to_entity.world
        return self.to_world

    def render(self, surface, overlay_surface, pos):
        super().render(surface, overlay_surface, pos)
        if self.touching_player:
            util.write(overlay_surface, self.hover_message, assets.MAIN_FONT, 45,(Globals.SIZE / 2) + Vec(0, 100),
                       (255, 255, 255), center=True)

    def update(self, world):
        super().update(world)
        self.touching_player = False


    def collide(self, other, world):
        super().collide(other, world)
        if other.is_player:
            self.touching_player = True




class AIEntity(Entity):
    def __init__(self, name, image, image_scale, speed, team, health, damage, sight_range, follow_weight, atk_interval, retreat_range,
                 post_func=None, hitbox_size=None, side_image=None):
        super().__init__(name, image, image_scale, team, health, solid=False, hitbox_size=hitbox_size, post_func=post_func)
        self.speed = speed
        self.damage = damage
        self.sight_range = sight_range
        self.follow_weight = follow_weight
        self.atk_interval = atk_interval
        self.atk_timer = 0
        self.retreat_range = retreat_range
        if side_image is not None:
            self.right_image = side_image
            self.left_image = pygame.transform.flip(side_image, True, False)
        else:
            self.right_image = None
            self.left_image = None

        self.wandering = False

    def render(self, surface, overlay_surface, pos):
        if self.right_image is not None:
            if abs(self.vel.x) > abs(self.vel.y):
                if self.vel.x > 0:
                    self.set_image(self.right_image)
                else:
                    self.set_image(self.left_image)
            else:
                self.set_image(self.default_image)

        super().render(surface, overlay_surface, pos)

    def in_range(self, other):
        return Vec.dist(self.pos, other.pos) <= self.sight_range

    def can_follow(self, other):
        if other.is_player:
            if other.current_image == assets.IMG_PLAYER_INVIS:
                return False
        return opposes(self, other) and self.in_range(other) and not (self.team == ALLY and other.team == NEUTRAL)

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
        center_dist = (world.size / 2) - self.pos
        self.accel(center_dist.norm() * (center_dist.mag() * 0.00001))

    def spread(self, world):
        # Spread away from same team to prevent overlapping sprites
        spread = list(filter(self.can_spread, world.entities))
        for other in spread:
            dir = self.pos - other.pos
            scalar = 1 / (dir.mag() + 0.1)  # Spread away more from closer entities
            self.accel(dir.norm() * scalar)

    def attack(self, target_direction, world):
        self.accel(target_direction.norm() * self.follow_weight)

    def retreat(self, target, target_direction):
        # Keep at a certain radius target_direction from player
        radius_pos = target.pos - target_direction.norm() * self.retreat_range
        radius_dir = radius_pos - self.pos
        magnitude = self.vel.mag() / self.speed + 0.5
        self.accel(radius_dir.norm() * self.follow_weight * magnitude)
        self.atk_timer += Globals.delta_time

    def update(self, world):
        follow = list(filter(self.can_follow, world.entities))
        if len(follow) > 0:
            target = follow[0]

            # approach player, but keep at distance until attack is charged
            target_dir = target.pos - self.pos

            if self.atk_timer > self.atk_interval:
                self.attack(target_dir, world)

                if self.colliding(target):
                    target.hurt(self.damage, world)
                    if target.take_knockback:
                        target.accel((target.pos - self.pos) * 0.05)
                        # pygame.mixer.Sound.play(assets.random_hit_sfx())
                        assets.play_sound(assets.random_hit_sfx())
                    self.atk_timer = 0
            else:
                self.retreat(target, target_dir)

        else:
            self.atk_timer = self.atk_interval
            self.wander(world)
        self.spread(world)
        super().update(world)


class RangedAIEntity(AIEntity):
    def __init__(self, name, image, image_scale, speed, team, health, damage, sight_range, follow_weight, atk_interval,
                 retreat_range, weapon_func,
                 post_func=None, hitbox_size=None):
        super().__init__(name, image, image_scale, speed, team, health, damage, sight_range, follow_weight,
                         atk_interval, retreat_range,
                         post_func=post_func, hitbox_size=hitbox_size)
        self.weapon_func = weapon_func

    def attack(self, target_direction, world):
        self.weapon_func(world, self, self.team, target_direction)
        self.atk_timer = 0

    def retreat(self, target, target_direction):
        # Keep at a certain radius target_direction from player
        radius_pos = target.pos - target_direction.norm() * self.retreat_range
        radius_dir = radius_pos - self.pos
        magnitude = self.vel.mag() / self.speed + 0.5
        self.accel(radius_dir.norm() * self.follow_weight * magnitude)
        self.atk_timer += Globals.delta_time


class Projectile(Entity):
    def __init__(self, name, image, image_scale, speed, team, health, damage, direction, Range, parent=None,
                 blockable=True, rotate=True, post_func=None):
        super().__init__(name, image, image_scale, team, health, post_func=post_func)
        self.speed = speed
        self.damage = damage
        self.vel = direction.norm() * self.speed
        self.range = Range
        if rotate:
            self.rotate(self.vel.angle())
        self.blockable = blockable

        if parent is None:
            self.init_vel = Vec(0, 0)
        else:
            if parent.is_player:
                self.damage *= parent.damage_multiplier
            self.init_vel = parent.vel
        self.vel += self.init_vel
        self.distance = 0

    def update(self, world):
        super().update(world)
        # accumulate the change in position to get total distance
        relative_vel = self.vel - self.init_vel
        self.distance += abs(relative_vel.mag() * Globals.delta_time)

        # hits border if within "radius" length.
        ground_size = world.size / 2
        x, y = self.pos.x, self.pos.y
        w, h = self.size.x, self.size.y
        # wall_dist > 0 when outer edge of sprite is outside world border
        hits_border = x - w / 2 <= 0 or y - h / 2 <= 0 \
                      or x + w / 2 >= world.size.x or y + h / 2 >= world.size.y

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
                if other.is_player:
                    assets.play_sound(assets.SFX_OW_PLAYER)
                    if other.invincible:
                        self.distance = self.range + 1  # remove from world
                other.hurt(damage, world)

            if other.take_knockback:
                other.accel((other.pos - self.pos) * 10)
            if self.blockable:
                if self.post_func is not None:
                    self.post_func(self, world, self.team)
                world.remove(self)


class Item(Entity):
    def __init__(self, name, image, image_scale, collide_func, condition=None):
        super().__init__(name, image, image_scale)
        self.collide_func = collide_func # Callback function to run when the player collides
        self.condition = condition # Boolean function that must be true to collect the item

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
