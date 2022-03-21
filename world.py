import pygame
import random
from vector import Vec
import util
from globals import Globals
import assets


class World:
    def __init__(self, name, size, outer_color, inner_color=None, image=None, music=None):
        self.name = name
        self.size = size
        self.bg_surface = pygame.Surface(size.tuple(), pygame.SRCALPHA, 32)
        self.border = Vec(250, 250)
        #self.fg_surface = pygame.Surface((size + self.border).tuple(), pygame.SRCALPHA, 32)
        self.outer_color, = outer_color,
        self.inner_color, = inner_color,
        self.image = image

        rect = util.rect_center(size/2, size)
        if inner_color is not None:
            self.bg_surface.fill(inner_color)
        if image is not None:
            self.bg_surface.blit(pygame.transform.scale(image, self.size.rounded().tuple()), rect)

        self.entities = []
        self.spawners = []
        self.completed = False

        self.music = music

    def start_music(self):
        if self.music is not None:
            pygame.mixer.music.load(self.music)
            if Globals.sound_on:
                pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.pause()

    def render(self, surface, pos):
        surface.blit(self.bg_surface, pos.tuple())
        #surface.blit(self.fg_surface, pos.tuple())

    def add(self, pos, entity):
        self.entities.append(entity)
        entity.pos = Vec(pos)

    def remove(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)
            for spawner in self.spawners:
                for spawn in spawner.spawned:
                    if spawn == entity:
                        spawner.spawned.remove(entity)

    def add_spawner(self, spawner):
        self.spawners.append(spawner)
        spawner.init(self)

    def rand_pos(self):
        return Vec(random.randint(0, self.size.x), random.randint(0, self.size.y))


class Spawner:
    def __init__(self, interval, spawn_func, max_num, dest=None, center_spread=1, pre_spawned=0):
        self.interval = interval
        self.spawn_func = spawn_func
        self.max_num = max_num
        self.dest = dest  # Specific position to spawn in world
        self.radius = center_spread  # Multiplier for position (< 1 is towards center, > 1 is towards edges)
        self.pre_spawned = pre_spawned  # How many to spawn at first

        self.time = 0
        self.spawned = []

    def init(self, world):
        for i in range(self.pre_spawned):
            self.spawn(world)

    def update(self, world):
        self.time += Globals.delta_time
        if self.time > self.interval:
            if len(self.spawned) < self.max_num:
                self.spawn(world)
            self.time = 0

    def spawn(self, world):
        entity = self.spawn_func()
        self.spawned.append(entity)

        if self.dest is None:  # If dest is none, random position in world
            spawn_pos = world.rand_pos() * 1 # self.radiusspawn_pos -= world.size/2
            spawn_pos -= world.size/2
            spawn_pos *= self.radius
            spawn_pos += world.size/2
        else:
            # Else destination is specific position in world
            spawn_pos = self.dest

        world.add(spawn_pos, entity)