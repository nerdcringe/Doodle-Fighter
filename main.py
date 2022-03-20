import sys
import pygame
from globals import Globals

pygame.init()
pygame.display.set_caption('lifesim')
pygame.key.set_repeat()
pygame.mouse.set_visible(False)

window = pygame.display.set_mode(Globals.SIZE.tuple(), pygame.DOUBLEBUF | pygame.RESIZABLE)
clock = pygame.time.Clock()



def screen_pos(v):
    return v + Globals.SIZE/2 - player.pos

def world_pos(v):
    return v - Globals.SIZE/2 + player.pos


from entity import *
from world import World, Spawner


def new_tree():
    return Entity("Tree", assets.IMG_TREE, 0.675, health=25, solid=True, hitbox_size=Vec(50, 165), post_func=tree_death)

def new_winter_tree():
    return Entity("Winter Tree", assets.IMG_TREE_WINTER, 0.675, health=25, solid=True, hitbox_size=Vec(30, 320), post_func=tree_death)


def new_rock():
    return Entity("Rock", assets.IMG_ROCK, 1, solid=True, hitbox_size=Vec(85, 50))


def new_building():
    return Entity("Building", assets.IMG_BUILDING, 1, health=10, hitbox_size = Vec(125, 160), solid=True)


def new_brawler():
    return AIEntity("Brawler", assets.IMG_BRAWLER, 0.3, 0.5, ENEMY, 6, 1, 600, 0.1, 750, 175, post_func=brawler_loot)

def new_brawler_boss():
    boss = AIEntity("Brawler Boss", assets.IMG_BRAWLER_BOSS, 0.53, 0.6, ENEMY, 50, 3, 2000, 0.04, 2000, 225, hitbox_size=Vec(128, 128), post_func=brawler_boss_loot)
    boss.take_knockback = False
    return boss

def new_ranger():
    return RangedAIEntity("Ranger", assets.IMG_RANGER, 0.25, 0.4, ENEMY, 4, 1, 700, 0.08, 1500, 350,
                          weapon_func=arrow_shot, post_func=ranger_loot, hitbox_size=Vec(64, 64))

def new_boomer():
    return RangedAIEntity("Ranger", assets.IMG_BOOMER, 0.3, 0.25, ENEMY, 10, 1, 400, 0.05, 3000, 250,
                          weapon_func=grenade_shot, post_func=ranger_loot, hitbox_size=Vec(70, 70))


def new_apple_pickup():
    return Pickup("Apple", assets.IMG_APPLE, 0.25, lambda: player.heal(10), condition=player.can_heal)

def new_dmg_up_pickup():
    return Pickup("Dmg Up", assets.IMG_DMG_UP, 0.25, lambda: player.raise_damage_multiplier(0.5))

def new_shield_pickup():
    return Pickup("Shield", assets.IMG_SHIELD, 0.25, lambda: player.raise_max_health(10))


def new_shotgun_pickup():
    return Pickup("Shotgun", assets.IMG_SHOTGUN, 0.25, lambda: gain_powerup(shotgun))

def new_arrows_pickup():
    return Pickup("Arrows", assets.IMG_ARROWS, 0.25, lambda: gain_powerup(arrows))

def new_grenade_pickup():
    return Pickup("Grenade", assets.IMG_GRENADE, 0.25, lambda: gain_powerup(grenade))

def new_speed_pickup():
    return Pickup("Sped Shoes", assets.IMG_SPEED_SHOES, 0.25, lambda: gain_powerup(speed_shoes))

def new_metalsuit_pickup():
    return Pickup("Metalsuit", assets.IMG_METALSUIT, 0.25, lambda: gain_powerup(metalsuit))



def new_bullet(parent, team, direction, Range):
    return Projectile("Bullet", assets.IMG_PROJECTILE_BULLET, 1, 1.25, team, None, 2, direction, Range, parent=parent, post_func=spawn_poof, blockable=True)

def single_shot(world, parent, team, direction):
    assets.play_sound(assets.random_shoot_sfx())
    world.add(parent.pos, new_bullet(parent, team, direction, 450))

def shotgun_shot(world, parent, team, direction):
    assets.play_sound(assets.SFX_SHOOT_SG)
    total_spread = 24
    count = 3
    current_angle = -total_spread/2
    for i in range(count):
        new_direction = Vec.polar(1, current_angle - direction.angle())
        world.add(parent.pos, new_bullet(parent, team, new_direction, 250))
        current_angle += total_spread / (count - 1)

def arrow_shot(world, parent, team, direction):
    assets.play_sound(assets.SFX_SHOOT_ARROW)
    arrow = Projectile("Arrow", assets.IMG_PROJECTILE_ARROW, 0.8, 1.8, team, None, 2, direction, 650, parent=parent, post_func=spawn_poof, blockable=False)
    world.add(parent.pos, arrow)

def grenade_shot(world, parent, team, direction):
    assets.play_sound(assets.SFX_SHOOT_GRENADE)
    grenade = Projectile("Grenade", assets.IMG_GRENADE, 0.2, 1, team, None, 2, direction, 400, parent=parent,
                       post_func=spawn_explosion, blockable=True)
    world.add(parent.pos, grenade)


def spawn_grave(self, world, team):
    world.add(self.pos, Entity("Grave", assets.IMG_GRAVE, 0.35, health=25, team=team, solid=True))

def spawn_explosion(self, world, team):
    assets.play_sound(assets.SFX_BOOM)
    world.add(self.pos, Projectile("Explosion", assets.IMG_EXPLOSION, 0.45, 0.04, team, None, 3, self.vel, 100, parent=self, blockable=False))

def spawn_poof(self, world, team):
    poof = Entity("Poof", assets.IMG_POOF, 1, 0.01, NEUTRAL)
    poof.lifetime = 100
    poof.rotate(random.randint(0, 360))
    world.add(self.pos, poof)
    #world.add(self.pos, Projectile("Poof", assets.IMG_POOF, 0.25, 0.75, NEUTRAL, None, 0, self.vel, 20, blockable=False, parent=self, rotate=False))


def tree_death(self, world, team):
    if random.randint(0, 1):
        world.add(self.pos, new_apple_pickup())

def brawler_loot(self, world, team):
    if random.random() < 0.25:
        loot = random.choice((new_shotgun_pickup, new_speed_pickup, new_arrows_pickup))
        world.add(self.pos, loot())

def ranger_loot(self, world, team):
    if random.random() < 0.25:
        loot = random.choice((new_shotgun_pickup, new_speed_pickup, new_arrows_pickup))
        world.add(self.pos, loot())

def brawler_boss_loot(self, world, team):
    loot = random.choice((new_metalsuit_pickup, new_shield_pickup, new_dmg_up_pickup))
    world.add(self.pos, loot())



Globals.cursor_img = assets.IMG_CURSOR_TARGET


def draw_cursor(surface):
    size = Vec(58, 58)
    cursor = pygame.transform.scale(Globals.cursor_img, size.tuple())
    pos = MOUSE_POS

    if Globals.cursor_img == assets.IMG_CURSOR_ARROW:
        pos = Vec(MOUSE_POS + size / 2)

    rect = util.rect_center(pos, size)
    surface.blit(cursor, rect)



class Player(Entity):
    def __init__(self, name, image, image_scale, speed, team, health, post_func=None, hurt_func=None):
        super().__init__(name, image, image_scale, speed, team, health, post_func=post_func)
        self.hurt_func = hurt_func
        self.is_player = True
        self.damage_multiplier = 1
        self.ow_image = False
        self.has_metalsuit = False

    def update(self, world):
        super().update(world)
        if self.shake_timer <= 0 and self.ow_image:
            self.set_image(assets.IMG_PLAYER_ALIVE)
            self.ow_image = False

    def control(self, keys):
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
        self.accel(direction.norm() * 0.12)
        if not (horizontal or vertical):
            self.vel *= 0.88

    def hurt(self, amount, world):
        super().hurt(amount, world)
        self.shake_timer = 150
        deplete_powerup(metalsuit, amount*500)

        if not self.has_metalsuit:
            self.set_image(assets.IMG_PLAYER_OW)
            self.ow_image = True

    def heal(self, amount):
        self.health += amount
        self.health = min(self.health, self.max_health)

    def can_heal(self):
        return self.health < self.max_health

    def raise_max_health(self, amount):
        self.max_health += amount

    def raise_damage_multiplier(self, amount):
        self.damage_multiplier += amount
        #print(self.damage_multiplier)


def set_world(new_world):
    global current_world
    if player in current_world.entities:
        current_world.remove(player)
        current_world = new_world
        new_world.add(Vec(new_world.size/2), player)



class Powerup:
    def __init__(self, name, image, gain_amount):
        self.name = name
        self.image = util.scale_image(image, 0.315)
        self.gain_amount = gain_amount
        self.current_max = gain_amount

# Add time/uses from powerup
def gain_powerup(powerup, amount=None):
    if amount is None:
        amount = powerup.gain_amount
    powerups[powerup] += amount
    #powerups[powerup] = min(powerups[powerup], powerup.gain_amount)
    powerup.current_max = powerups[powerup]

# Remove time/uses from powerup
def deplete_powerup(powerup, amount):
    if powerups[powerup] > 0:
        powerups[powerup] -= amount
        powerups[powerup] = max(powerups[powerup], 0)



def debug(key, mouse_world_pos):
    if key == pygame.K_j:
        current_world.add(mouse_world_pos, new_brawler())
    elif key == pygame.K_k:
        current_world.add(mouse_world_pos, new_brawler_boss())
    elif key == pygame.K_l:
        current_world.add(mouse_world_pos, new_ranger())
    elif key == pygame.K_SEMICOLON:
        current_world.add(mouse_world_pos, new_boomer())

    elif key == pygame.K_1:
        current_world.add(mouse_world_pos, new_apple_pickup())
    elif key == pygame.K_2:
        current_world.add(mouse_world_pos, new_shield_pickup())
    elif key == pygame.K_3:
        current_world.add(mouse_world_pos, new_dmg_up_pickup())

    elif key == pygame.K_4:
        current_world.add(mouse_world_pos, new_shotgun_pickup())
    elif key == pygame.K_5:
        current_world.add(mouse_world_pos, new_arrows_pickup())
    elif key == pygame.K_6:
        current_world.add(mouse_world_pos, new_speed_pickup())
    elif key == pygame.K_7:
        current_world.add(mouse_world_pos, new_metalsuit_pickup())
    if key == pygame.K_8:
        current_world.add(mouse_world_pos, new_grenade_pickup())

    elif key == pygame.K_v:
        Globals.debug_mode = not Globals.debug_mode
    elif key == pygame.K_c:
        Globals.show_overlay = not Globals.show_overlay

    elif key == pygame.K_b:
        index = worlds.index(current_world) - 1
        index = util.wraparound(index, 0, len(worlds) - 1)
        set_world(worlds[index])

    elif key == pygame.K_n:
        index = worlds.index(current_world) + 1
        index = util.wraparound(index, 0, len(worlds) - 1)
        set_world(worlds[index])


def set_sound(on):
    if on:
        pass#pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.pause()


if __name__ == "__main__":
    while True:
        frames = 0

        pygame.mixer.music.set_volume(0.35)
        pygame.mixer.music.load(assets.MUSIC_OVERWORLD)
        set_sound(False)


        shotgun = Powerup("Shotgun", assets.IMG_SHOTGUN, 20000)
        arrows = Powerup("Arrows", assets.IMG_ARROWS, 20000)
        grenade = Powerup("Grenade", assets.IMG_GRENADE, 15000)
        speed_shoes = Powerup("Speed", assets.IMG_SPEED_SHOES, 10000)
        metalsuit = Powerup("Metalsuit", assets.IMG_METALSUIT, 10000)

        # Amount of time/uses left for each powerup
        powerups = {
            shotgun: 0,
            arrows: 0,
            grenade: 0,
            speed_shoes: 0,
            metalsuit: 0,
        }


        worlds = []
        overworld = World("Overworld", Vec(2500, 2500), (220, 200, 140), (85, 175, 95))
        worlds.append(overworld)
        current_world = overworld

        city_world = World("Cityworld", Vec(3000, 3000), (105, 210, 150), (175, 175, 175))#image=assets.IMG_BG_CITY)
        worlds.append(city_world)

        forest_world = World("Forestworld", Vec(2250, 2250), (13, 46, 37), (35, 75, 65))
        #forest_world = World("Forestworld", Vec(2000, 2000), (30, 34, 41), (56, 70, 94))
        worlds.append(forest_world)

        #house_world = World("HouseWorld", Vec(800, 800), (201, 156, 40), (217, 191, 124))
        #worlds.append(house_world)


        player_speed = 0.65
        player = Player("Player", assets.IMG_PLAYER_ALIVE, 0.28, player_speed, ALLY, 20, post_func=spawn_grave)
        overworld.add(overworld.size/2, player)


        overworld.add(Vec(500, 500), Entity("House", assets.IMG_HOUSE, 0.8, solid=True))
        for i in range(15):
            overworld.add(overworld.rand_pos(), new_rock())
        overworld.add_spawner(Spawner(8000, new_tree, max_num=12, center_spread=1.25, pre_spawned=12))
        overworld.add_spawner(Spawner(4000, new_brawler, max_num=5))
        #overworld.add_spawner(Spawner(10000, new_ranger, max_num=3))
        overworld.add_spawner(Spawner(45000, new_brawler_boss, max_num=1))

        city_world.add_spawner(Spawner(0, new_building, max_num=12, center_spread=1, pre_spawned=12))


        for i in range(8):
            forest_world.add(forest_world.rand_pos(), new_rock())
        #forest_world.add_spawner(Spawner(7000, new_ranger, max_num=4, pre_spawned=2))
        forest_world.add_spawner(Spawner(5000, new_winter_tree, max_num=5, pre_spawned=20))


        while True:
            frames += 1
            Globals.delta_time = clock.tick(Globals.FPS)

            keys = pygame.key.get_pressed()
            MOUSE_POS = Vec(pygame.mouse.get_pos())
            MOUSE_WORLD_POS = world_pos(MOUSE_POS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Exited")
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if MOUSE_POS.x < 55 and MOUSE_POS.y < 60:
                        Globals.sound_on = not Globals.sound_on

                    elif player.health > 0:
                        if event.button == 1:
                            default_gun = True

                            if powerups[shotgun] > 0:
                                shotgun_shot(current_world, player, ALLY, MOUSE_WORLD_POS - player.pos)
                                default_gun = False
                                deplete_powerup(shotgun, 750)

                            if powerups[arrows] > 0:
                                arrow_shot(current_world, player, ALLY, MOUSE_WORLD_POS - player.pos)
                                default_gun = False
                                deplete_powerup(arrows, 750)

                            if powerups[grenade] > 0:
                                grenade_shot(current_world, player, ALLY, MOUSE_WORLD_POS - player.pos)
                                default_gun = False
                                deplete_powerup(grenade, 750)

                            if default_gun:
                                single_shot(current_world, player, ALLY, MOUSE_WORLD_POS - player.pos)

                elif event.type == pygame.KEYDOWN:
                    debug(event.key, MOUSE_WORLD_POS)
                    if event.key == pygame.K_m:
                        Globals.sound_on = not Globals.sound_on
                        set_sound(Globals.sound_on)
                    """if event.key == pygame.K_e:
                        for entity in player.last_collisions:
                            if entity.name == "House":
                                set_world(house_world)"""
                elif event.type == pygame.VIDEORESIZE:
                    Globals.SIZE = Vec(event.size)

            if keys[pygame.K_r]:
                break


            deplete_powerup(shotgun, Globals.delta_time)
            deplete_powerup(grenade, Globals.delta_time)
            deplete_powerup(arrows, Globals.delta_time)

            player.has_metalsuit = powerups[metalsuit] > 0

            if powerups[speed_shoes] > 0:
                if player.has_metalsuit:
                    player.speed = player_speed * 1.25
                else:
                    player.speed = player_speed * 1.4
                deplete_powerup(speed_shoes, Globals.delta_time)
            else:
                if player.has_metalsuit:
                    player.speed = player_speed * 0.8
                else:
                    player.speed = player_speed

            if player.has_metalsuit:
                if player.image is assets.IMG_PLAYER_ALIVE:
                    player.set_image(assets.IMG_PLAYER_METALSUIT)
                player.invincible = True
                player.take_knockback = False
                deplete_powerup(metalsuit, Globals.delta_time)
            else:
                if player.image is assets.IMG_PLAYER_METALSUIT:
                    player.set_image(assets.IMG_PLAYER_ALIVE)
                player.invincible = False
                player.take_knockback = True


            player.control(keys)

            for s in current_world.spawners:
                s.update(current_world)
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
            blit_pos = -player.pos + Globals.SIZE/2
            current_world.render(window, blit_pos)

            current_world.entities.sort(key = lambda e: e.pos.y + e.size.y / 2)
            for e in current_world.entities:
                e.render(window, screen_pos(Vec(e.hitbox().center)))

            if Globals.show_overlay:
                stats = [
                    "Position: " + str(player.pos.rounded()),
                    "World: " + current_world.name,
                    "Damage Multiplier: * " + str(round(player.damage_multiplier, 1)),
                    "Health: " + str(max(0, round(player.health))) + "/" + str(max(0, round(player.max_health))),
                ]

                """for powerup in powerups:
                    if powerups[powerup] > -100:
                        stats.append(powerup.name + ": " + str(powerups[powerup]))"""

                if Globals.debug_mode:
                    stats.append("# Entities: " + str(len(current_world.entities)))
                    stats.append("FPS: " + str(round(clock.get_fps(), 1)))

                util.draw_meter(window, Vec(115, Globals.SIZE.y - 35 * 4 - 6), Vec(200, 33),
                                player.health / player.max_health, (80, 130, 255), (0, 0, 0), center=False)

                stat_y = Globals.SIZE.y - 15  # - 35
                for stat in stats:
                    stat_y -= 35
                    util.write(window, stat, assets.MAIN_FONT, 34, Vec(10, stat_y), (255, 255, 255))

                if player.health <= 0:
                    util.write(window, "Press R to restart", assets.MAIN_FONT, 45, Globals.SIZE / 2 + Vec(0, 100), (255, 255, 255),
                               center=True)
                x = 0
                y = 0
                for powerup in powerups:
                    if powerups[powerup] > 0:
                        image_pos = Vec(Globals.SIZE.x - 95, 5) + (Vec(-x * 85, y * 85))
                        window.blit(powerup.image, image_pos.tuple())
                        timer_value = min(powerups[powerup] / powerup.current_max, 1)
                        util.draw_meter(window, image_pos + Vec(42, 100), Vec(50, 6), timer_value, (255, 255, 255),
                                        (100, 100, 100), center=True)
                        x += 1
                        if x >= 3:
                            x = 0
                            y += 1

            sound_icon = None
            if Globals.sound_on:
               sound_icon = assets.IMG_SOUND_ON
            else:
               sound_icon = assets.IMG_SOUND_OFF
            window.blit(sound_icon, (0, 0))


            draw_cursor(window)

            pygame.display.flip()