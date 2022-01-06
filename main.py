import sys
import pygame
import math
from vector import Vec
import util
from inventory import Inventory, Item
from entity import *
from world import World
from globals import Globals

FPS = 90
debug_mode = False

pygame.init()
pygame.display.set_caption('lifesim')
pygame.key.set_repeat()

window = pygame.display.set_mode(Globals.SIZE.tuple(), pygame.DOUBLEBUF)
clock = pygame.time.Clock()


def screen_pos(v):
    return v + Globals.SIZE/2 - player.pos


def world_pos(v):
    return v - Globals.SIZE/2 + player.pos


import assets


def spawn_brawler():
    return AI_Entity("Enemy", assets.IMG_BRAWLER, 0.3, 0.5, ENEMY, 10, 1, 600, 0.1)


def spawn_boss():
    return AI_Entity("Enemy", assets.IMG_BRAWLER_BOSS, 0.5, 0.5, ENEMY, 100, 1, 800, 0.1)


def new_tree():
    return Entity("Tree", assets.IMG_TREE, 0.75)


def new_apple_pickup():
    return Pickup("Apple", assets.IMG_APPLE, 0.2, lambda: player.heal(4), condition=player.can_heal)


def new_bullet(parent, team, direction, range):
    return Projectile("Bullet", assets.IMG_BULLET, 1, 1, team, None, 2, direction, range, parent=parent, post_func=spawn_poof)


def single_shot(world, parent, team, direction):
    world.add(parent.pos, new_bullet(parent, team, direction, 500))


def shotgun_shot(world, parent, team, direction):
    spread = 36
    count = 3
    current_angle = -spread/2
    for i in range(count):
        new_direction = Vec.polar(1, current_angle - direction.angle())
        world.add(parent.pos, new_bullet(parent, team, new_direction, 200))
        current_angle += spread / (count - 1)


def spawn_grave(self, world, team):
    world.add(self.pos, Entity("Grave", assets.IMG_GRAVE, 0.35, health=25, team=team))


def spawn_poof(self, world, team):
    poof = Entity("Poof", assets.IMG_POOF, 1, 0.01, NEUTRAL, lifetime=100)
    poof.rotate(random.randint(0, 360))
    world.add(self.pos, poof)
    #world.add(self.pos, Projectile("Poof", assets.IMG_POOF, 0.25, 0.75, NEUTRAL, None, 0, self.vel, 20, blockable=False, parent=self, rotate=False))


def render_overlay(surface):
    stats = [
        "Position: " + str(player.pos.rounded()),
        "World: " + current_world.name,
        "Health: " + str(max(0, round(player.health))) + "/" + str(max(0, round(player.max_health))),
    ]

    if debug_mode:
        stats.append("# Entities: " + str(len(current_world.entities)))
        stats.append("FPS: " + str(round(clock.get_fps(), 1)))
    y = Globals.SIZE.y - 15
    for stat in stats:
        y -= 35
        util.write(surface, stat, assets.MAIN_FONT, 34, Vec(10, y), (255, 255, 255))

    if player.health <= 0:
        util.write(surface, "Press R to restart", assets.MAIN_FONT, 45, current_world.size/2, (255, 255, 255), center=True)
    """
    draw_pos = Vec(Globals.SIZE.x - 350, Globals.SIZE.y - 180)
    quantity = " * " + str(self.contents[self.selected])
    if self.selected.infinite:
        quantity = ""
    return self.selected.name + quantity

    util.write(surface, "Item: " + inventory.get_selected_info(), assets.MAIN_FONT, 34, draw_pos, (255, 255, 255))
    if inventory.selected is not None:
        image = inventory.selected.image
        if image is not None:
            image = pygame.transform.scale(image, (100, 100))
            rect = rect_center(Vec(Globals.SIZE.x - 175, Globals.SIZE.y - 75), Vec(100, 100))
            surface.blit(image, rect)
            """


def set_world(new_world):
    global current_world
    current_world.remove(player)
    current_world = new_world
    new_world.add(Vec(new_world.size/2), player)


def debug(key, mouse_world_pos):
    if key == pygame.K_p:
        spawn_poof(player, current_world, ALLY)
    if key == pygame.K_j:
        current_world.add(mouse_world_pos, spawn_brawler())
    if key == pygame.K_u:
        current_world.add(mouse_world_pos, spawn_boss())
    elif key == pygame.K_m:
        current_world.add(mouse_world_pos, new_apple_pickup())
    elif key == pygame.K_v:
        global debug_mode
        debug_mode = not debug_mode
    elif key == pygame.K_b:
        index = worlds.index(current_world) - 1
        index = util.wraparound(index, 0, len(worlds) - 1)
        set_world(worlds[index])

    elif key == pygame.K_n:
        index = worlds.index(current_world) + 1
        index = util.wraparound(index, 0, len(worlds) - 1)
        set_world(worlds[index])


if __name__ == "__main__":
    while True:
        keys = None

        worlds = []
        current_world = None
        player = None
        inventory = None

        overworld = World("Overworld", Vec(1000, 1000), (220, 200, 140), (80, 170, 90))
        worlds.append(overworld)
        current_world = overworld

        city_world = World("City", Vec(1500, 1500), (112, 250, 160), image=assets.IMG_BG_CITY)
        worlds.append(city_world)

        player = Player("Player", assets.IMG_PLAYER_ALIVE, 0.25, 0.65, ALLY, 16, post_func=spawn_grave)
        overworld.add(overworld.size/2, player)

        """
        enemy = AI_Entity("Enemy", assets.BRAWLER, Vec(65, 65), 0.5, 100, ENEMY, damage, follow)
        overworld.add(Vec(250, 200), enemy)
        enemy = AI_Entity("Enemy", assets.BRAWLER, Vec(65, 65), 0.5, 100, ENEMY, damage, follow)
        overworld.add(Vec(200, 250), enemy)
        enemy = AI_Entity("Enemy", assets.BRAWLER, Vec(65, 65), 0.5, 100, ENEMY, damage, follow)
        overworld.add(Vec(250, 250), enemy)"""
        """gun = Item("Gun")
        shotgun = Item("Shotgun")
        grenade = Item("Grenade")
        contents = {
            gun: 100,
            shotgun: 100,
            grenade: 100
        }
        self.inventory = Inventory(contents)"""

        frames = 0
        while True:
            frames += 1
            Globals.delta_time = clock.tick(FPS)

            KEYS = pygame.key.get_pressed()
            MOUSE_WORLD_POS = world_pos(Vec(pygame.mouse.get_pos()))

            keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Exited")
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if player.health > 0:
                        if event.button == 1:
                            single_shot(current_world, player, ALLY, MOUSE_WORLD_POS - player.pos)
                        elif event.button == 3:
                            shotgun_shot(current_world, player, ALLY, MOUSE_WORLD_POS - player.pos)
                elif event.type == pygame.KEYDOWN:
                    debug(event.key, MOUSE_WORLD_POS)


                """elif event.type == pygame.MOUSEWHEEL:
                    MOUSE_SCROLL = event.y
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button <= 3:
                        MOUSE_CLICKED[event.button - 1] = True"""
            if KEYS[pygame.K_r]:
                break

            #print(player.health)

            horizontal = False
            vertical = False
            direction = Vec(0, 0)
            if keys[pygame.K_a]:
                direction -= Vec(1, 0)
                horizontal = True
            if keys[pygame.K_d]:
                direction += Vec(1, 0)
                horizontal = True
            if keys[pygame.K_w]:
                direction -= Vec(0, 1)
                vertical = True
            if keys[pygame.K_s]:
                direction += Vec(0, 1)
                vertical = True
            player.accel(direction.norm() * 0.095)
            if not (horizontal or vertical):
                player.vel *= 0.92

            current_world.entities.sort(key = lambda e: e.pos.y + e.size.y / 2)

            for e in current_world.entities:
                e.update(current_world)
            for e in current_world.entities:
                for other in current_world.entities:
                    if e is not other and e.colliding(other):
                        e.collide(other, current_world)
                        e.last_collisions.add(other)
                    else:
                        e.last_collisions.discard(other)

            window.fill(current_world.outer_color)
            current_world.fg_surface.fill((0, 0, 0, 0))
            for e in current_world.entities:
                e.render(current_world.fg_surface)

            blit_pos = -player.pos + Globals.SIZE/2
            current_world.render(window, blit_pos)
            render_overlay(window)

            pygame.display.flip()