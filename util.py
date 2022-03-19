import pygame


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


def scale_image(image, scale):
    return pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))



fonts = {}

def write(surface, text, font_name, size, pos, color, center=False):
    if size in fonts:
        Font = fonts[size]
    else:
        Font = pygame.font.Font(font_name, size)
        fonts[size] = Font

    text = Font.render(text, 1, color)

    if center:
        text_rect = text.get_rect(center=pos.tuple())
    else:
        text_rect = pos.tuple()
    surface.blit(text, text_rect)


def draw_meter(surface, pos, size, proportion, fg_color, bg_color, center=True):
    if center:
        rect = rect_center(pos, size)
    else:
        rect = pygame.Rect(pos.tuple(), size.tuple())
    # pygame.draw.rect(surface, (255, 255, 255), outline_rect.inflate(4, 4))
    pygame.draw.rect(surface, bg_color, rect)

    rect.width = proportion * size.x
    pygame.draw.rect(surface, fg_color, rect)
