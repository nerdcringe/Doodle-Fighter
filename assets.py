import os
import pygame
import random

RES_PATH = "res"
images = {}
fonts = {}


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

def load_sfx(name):
    path = os.path.join(RES_PATH, 'audio', name)
    sound = pygame.mixer.Sound(path)
    sound.set_volume(0.4)
    return sound

def load_music(name):
    path = os.path.join(RES_PATH, 'audio', name)
    return path

def font_path(name):
    return os.path.join(RES_PATH, name)



MAIN_FONT = font_path("StayPuft.ttf")

MUSIC_OVERWORLD = load_music("overworld.wav")

SFX_HIT_1 = load_sfx("hit_1.wav")
SFX_HIT_2 = load_sfx("hit_2.wav")
SFX_HIT_3 = load_sfx("hit_3.wav")

def random_hit_sfx():
    return random.choice((SFX_HIT_1, SFX_HIT_2, SFX_HIT_3))


IMG_CURSOR_ARROW = load_image("cursor_arrow.png")
IMG_CURSOR_TARGET = load_image("cursor_target.png")

IMG_BG_CITY = load_image("bg_city.png")

IMG_PLAYER_ALIVE = load_image("player_alive.png")
IMG_PLAYER_DEAD = load_image("player_dead.png")
IMG_PLAYER_METALSUIT = load_image("player_metalsuit.png")

IMG_BRAWLER = load_image("brawler.png")
IMG_BRAWLER_BOSS = load_image("brawler_boss.png")

IMG_PROJECTILE_BULLET = load_image("projectile_bullet.png")
IMG_PROJECTILE_ARROW = load_image("projectile_arrow.png")
IMG_POOF = load_image("poof.png")
IMG_EXPLOSION = load_image("explosion.png")


IMG_TREE = load_image("tree.png")
IMG_ROCK = load_image("rock.png")
IMG_GRAVE = load_image("grave.png")

IMG_DMG_UP = load_image("pickup_dmg_up.png")
IMG_APPLE = load_image("pickup_apple.png")

IMG_SHOTGUN = load_image("pickup_shotgun.png")
IMG_ARROWS = load_image("pickup_arrows.png")
IMG_GRENADE = load_image("pickup_grenade.png")
IMG_SPEED_SHOES = load_image("pickup_speed.png")
IMG_SHIELD = load_image("pickup_shield.png")
IMG_METALSUIT = load_image("pickup_metalsuit.png")
