import os
import pygame
from globals import Globals


def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))


def wraparound(value, min_val, max_val):
    Range = min_val - max_val - 1
    if value > max_val:
        value += Range
    elif value < min_val:
        value -= Range
    return value


def rect_center(pos, size):
    rect = pygame.Rect((0, 0), size.tuple())
    rect.center = pos.tuple()
    return rect


def rot_center(image, rect, angle):
    """rotate an image while keeping its center"""
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = rot_image.get_rect(center=rect.center)
    return rot_image


RES_PATH = "res"
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

def scale_image(image, scale):
    return pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))

fonts = {}


def write(surface, text, font_name, size, pos, color, center=False):
    if size in fonts:
        Font = fonts[size]
    else:
        Font = pygame.font.Font(os.path.join(RES_PATH, font_name), size)
        fonts[size] = Font
    text = Font.render(text, 1, color)

    if center:
        text_rect = text.get_rect(center=pos.tuple())
    else:
        text_rect = pos.tuple()
    surface.blit(text, text_rect)

