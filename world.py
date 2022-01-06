import pygame
from vector import Vec
import util


class World:
    def __init__(self, name, size, outer_color, inner_color=None, image=None):
        self.name = name
        self.size = size
        self.bg_surface = pygame.Surface(size.tuple(), pygame.SRCALPHA, 32)
        self.border = Vec(250, 250)
        self.fg_surface = pygame.Surface((size + self.border).tuple(), pygame.SRCALPHA, 32)
        self.outer_color, = outer_color,
        self.inner_color, = inner_color,
        self.image = image

        rect = util.rect_center(size/2, size)
        if inner_color is not None:
            self.bg_surface.fill(inner_color)
        if image is not None:
            self.bg_surface.blit(pygame.transform.scale(image, self.size.rounded().tuple()), rect)

        self.entities = []

    def add(self, pos, entity):
        self.entities.append(entity)
        entity.pos = Vec(pos)

    def remove(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)

    def render(self, surface, pos):
        surface.blit(self.bg_surface, pos.tuple())
        surface.blit(self.fg_surface, pos.tuple())



