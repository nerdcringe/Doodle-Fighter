import os
import pygame
import random
import util
from globals import Globals

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

def load_sfx(name, volume=0.4):
    path = os.path.join(RES_PATH, 'audio', name)
    sound = pygame.mixer.Sound(path)
    sound.set_volume(volume*0.5)
    sfx.append(sound)
    return sound

def load_music(name):
    path = os.path.join(RES_PATH, 'audio', name)
    return path

def font_path(name):
    return os.path.join(RES_PATH, name)




MAIN_FONT = font_path("StayPuft.ttf")

MUSIC_OVERWORLD = load_music("overworld.wav")

sfx = []
SFX_HIT_1 = load_sfx("hit_1.wav", 0.2)
SFX_HIT_2 = load_sfx("hit_2.wav")
SFX_HIT_3 = load_sfx("hit_3.wav", 0.3)
SFX_SHOOT_1 = load_sfx("shoot_1.wav", 0.45)
SFX_SHOOT_2 = load_sfx("shoot_2.wav")
SFX_SHOOT_SG = load_sfx("shoot_sg.wav", 0.3)
SFX_SHOOT_ARROW = load_sfx("shoot_arrow.wav")
SFX_SHOOT_GRENADE = load_sfx("shoot_grenade.wav", 0.5)
SFX_BOOM = load_sfx("boom.wav", 0.3)

SFX_OW_PLAYER = load_sfx("ow_player.wav", 0.8)

def random_hit_sfx():
    return random.choice((SFX_HIT_1, SFX_HIT_2, SFX_HIT_3))

def random_shoot_sfx():
    return random.choice((SFX_SHOOT_1, SFX_SHOOT_2))


def play_sound(sound):
    if Globals.sound_on:
        pygame.mixer.Sound.play(sound)


IMG_CURSOR_ARROW = load_image("cursor_arrow.png")
IMG_CURSOR_TARGET = load_image("cursor_target.png")
IMG_SOUND_ON = util.scale_image(load_image("ui_sound_on.png"), 0.4)
IMG_SOUND_OFF = util.scale_image(load_image("ui_sound_off.png"), 0.4)


IMG_BG_CITY = load_image("bg_city.png")

IMG_PLAYER_ALIVE = load_image("player_alive.png")
IMG_PLAYER_DEAD = load_image("player_dead.png")
IMG_PLAYER_OW = load_image("player_ow.png")
IMG_PLAYER_METALSUIT = load_image("player_metalsuit.png")

IMG_BRAWLER = load_image("brawler.png")
IMG_BRAWLER_BOSS = load_image("brawler_boss.png")
IMG_RANGER = load_image("ranger.png")

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