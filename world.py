import pygame
import random
from vector import Vec
import util
from globals import Globals
import assets
from entity import *


class World:
    def __init__(self, name, size, outer_color, inner_color=None, dark=False, solid_border=False, image=None, music=None, complete_condition=None):
        self.name = name
        self.size = size
        self.bg_surface = pygame.Surface(size.tuple(), pygame.SRCALPHA, 32).convert()
        self.border = Vec(250, 250)
        self.outer_color, = outer_color,
        self.inner_color, = inner_color,
        self.dark = dark
        self.solid_border = solid_border
        self.image = image
        self.music = music

        # When this boolean getter function is true, spawn the next world sign
        # By default it is when all dungeons are defeated
        if complete_condition is None:
            self.complete_condition = lambda w: w.dungeons_defeated == len(w.dungeons) and len(w.dungeons) != 0
        else:
            self.complete_condition = complete_condition
        self.completed = False

        rect = util.rect_center(size/2, size)
        if inner_color is not None:
            self.bg_surface.fill(inner_color)
        if image is not None:
            self.bg_surface.blit(pygame.transform.scale(image, self.size.rounded().tuple()), rect)

        self.entities = []
        self.spawners = []
        self.dungeons = []
        self.dungeons_defeated = 0
        self.time_elapsed = 0

        self.enemies = set([])
        self.allies = set([])


    def start_music(self):
        if self.music is not None:
            pygame.mixer.music.load(self.music)
            if Globals.sound_on:
                pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.pause()

    def render(self, surface, pos):
        surface.blit(self.bg_surface, pos.tuple())

    def add(self, pos, e):
        self.entities.append(e)
        e.world = self
        e.pos = Vec(pos)

        if not isinstance(e, Projectile):
            if e.team == ENEMY:
                self.enemies.add(e)
            elif e.team == ALLY and not e.is_player:
                self.allies.add(e)
                #print(e)

    def remove(self, e):
        if e in self.entities:
            self.entities.remove(e)

            # remove from enemies and allies in case the entity was in those sets
            # sets are nice because you don't have to check if something's there to try to remove it
            self.enemies.discard(e)
            self.allies.discard(e)

            for spawner in self.spawners:
                for spawn in spawner.spawned:
                    if spawn == e:
                        spawner.spawned.remove(e)

    def add_spawner(self, spawner):
        self.spawners.append(spawner)
        spawner.init(self)

    def add_dungeon(self, pos, entrance):
        self.add(pos, entrance)
        self.dungeons.append(entrance)


    def rand_pos(self):
        return Vec(random.randint(0, self.size.x), random.randint(0, self.size.y))


class Spawner:
    def __init__(self, interval, spawn_func, max_num, dest=None, center_spread=1, pre_spawned=0, min_spawn=1, max_spawn=1):
        self.interval = interval
        self.spawn_func = spawn_func
        self.max_num = max_num
        self.dest = dest  # Specific position to spawn in world
        self.radius = center_spread  # Multiplier for position (< 1 is towards center, > 1 is towards edges)
        self.pre_spawned = pre_spawned  # How many to spawn at first
        self.min_spawn = min_spawn  # Min number that can spawn at once
        self.max_spawn = max_spawn  # Max number that can spawn at once

        self.time = 0
        self.spawned = []

    def init(self, world):
        for i in range(self.pre_spawned):
            self.spawn(world, world.rand_pos())

    def update(self, world):
        self.time += Globals.delta_time
        if self.time > self.interval:
            if self.dest is None:  # If dest is none, random position in world
                spawn_pos = world.rand_pos() * 1 # self.radiusspawn_pos -= world.size/2
                spawn_pos -= world.size/2
                spawn_pos *= self.radius
                spawn_pos += world.size/2
            else:
                # Else destination is specific position in world
                spawn_pos = self.dest

            amount = random.randint(self.min_spawn, self.max_spawn)

            for i in range(amount):
                if len(self.spawned) < self.max_num:
                    self.spawn(world, spawn_pos)
            self.time = 0

    def spawn(self, world, pos):
        entity = self.spawn_func()
        self.spawned.append(entity)

        world.add(pos, entity)
        entity.keep_in_bounds(world)