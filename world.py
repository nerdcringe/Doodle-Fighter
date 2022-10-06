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

    def add_dungeon(self, pos, entrance):
        self.add(pos, entrance)
        self.dungeons.append(entrance)

    def rand_pos(self):
        return Vec(random.randint(0, self.size.x), random.randint(0, self.size.y))


class Spawner:
    def __init__(self, interval, spawn_func, spawn_limit=4, spawn_amount=1, destination=None, ):
        self.interval = interval
        self.spawn_func = spawn_func
        self.spawn_limit = spawn_limit      # Only spawns when there aren't too many already existing
        self.spawn_amount = spawn_amount    # Number to spawn at once
        self.destination = destination      # Specific position to spawn in world
        self.time = 0
        self.spawned = []

    def update(self, world):
        self.time += Globals.delta_time
        if self.time > self.interval:
            self.spawn(world)
            self.time = 0

    def spawn(self, world):
        spawn_pos = Vec(0, 0)
        if self.destination is None:  # If no destination specified, choose random position in world
            spawn_pos = world.rand_pos()
        else:
            # Else destination is specific position in world
            spawn_pos = self.destination

        for i in range(self.spawn_amount):
            if len(self.spawned) < self.spawn_limit:
                entity = self.spawn_func()
                self.spawned.append(entity)
                world.add(spawn_pos, entity)
                entity.keep_in_bounds(world)