
import sys
import pygame
from globals import Globals

pygame.init()
pygame.display.set_caption('lifesim')
pygame.key.set_repeat()
pygame.mouse.set_visible(False)

icon = pygame.image.load('res/img/icon.png')
pygame.display.set_icon(icon)


window = pygame.display.set_mode(Globals.SIZE.tuple(), pygame.DOUBLEBUF | pygame.RESIZABLE)
clock = pygame.time.Clock()
pygame.mixer.music.set_volume(0.15)


overlay = pygame.Surface(window.get_size()).convert_alpha()

def screen_pos(v):
    return v + Globals.SIZE/2 - player.pos

def world_pos(v):
    return v - Globals.SIZE/2 + player.pos


import assets
from entity import *
from world import World, Spawner



def new_tree():
    return Entity("Tree", assets.IMG_TREE, 0.675, health=25, solid=True, hitbox_size=Vec(50, 165), death_func=tree_loot)

def new_city_tree():
    return Entity("City Tree", assets.IMG_TREE_CITY, 0.675, health=25, solid=True, hitbox_size=Vec(55, 170),
                  death_func=tree_loot)

def new_winter_tree():
    return Entity("Winter Tree", assets.IMG_TREE_WINTER, 0.675, health=25, solid=True, hitbox_size=Vec(30, 320),
                  death_func=tree_loot)

def new_rock():
    return Entity("Rock", assets.IMG_ROCK, 1, solid=True, hitbox_size=Vec(85, 50))

def new_street_light():
    return Entity("Street Light", assets.IMG_STREET_LIGHT, 0.675, solid=True, hitbox_size=Vec(25, 140),
                  death_func=None)


def new_dungeon(entrance, dungeon_world, enemy_sets):
    door = Portal("Door", assets.IMG_DOOR, 0.8, to_entity=entrance) # Exiting the door sends player outside the dungeon
    dungeon_world.add(Vec(dungeon_world.size.x/2, -60), door)

    entrance.to_entity = door  # Set dungeon destination to the door inside the dungeon

    chosen_set = random.choice(enemy_sets)

    for i in range(chosen_set[0]): # 0 index is amount to spawn
        dungeon_world.add(Vec(dungeon_world.size.x/2, dungeon_world.size.y), chosen_set[1]())  # 1 index is the type of enemy

    return entrance


def new_brawler():
    return AIEntity("Brawler", assets.IMG_BRAWLER, 0.3, 0.5, ENEMY, 6, 1, 600, 0.1, 750, 175, death_func=brawler_loot)

def new_cold_brawler():
    return AIEntity("Brawler", assets.IMG_BRAWLER_COLD, 0.3, 0.5, ENEMY, 6, 1, 600, 0.1, 750, 175, death_func=brawler_loot)

def new_brawler_boss():
    boss = AIEntity("Brawler Boss", assets.IMG_BRAWLER_BOSS, 0.5, 0.6, ENEMY, 50, 3, 2000, 0.035, 1000, 225,
                    hitbox_size=Vec(128, 128), death_func=brawler_boss_loot)
    boss.take_knockback = False
    return boss

def new_ranger():
    return RangedAIEntity("Ranger", assets.IMG_RANGER, 0.25, speed=0.4, team=ENEMY, health=4, damage=1, sight_range=700,
                          follow_weight=0.08, atk_interval=2000, retreat_range=350, weapon_func=arrow_shot,
                          death_func=ranger_loot, hitbox_size=Vec(64, 64))

def new_ranger_boss():
    return RangedAIEntity("Ranger Boss", assets.IMG_RANGER_BOSS, 0.4, speed=0.5, team=ENEMY, health=40, damage=1, sight_range=800,
                          follow_weight=0.05, atk_interval=1000, retreat_range=350, weapon_func=arrow_shot,
                          death_func=ranger_boss_loot, hitbox_size=Vec(100, 100))

def new_boomer():
    return RangedAIEntity("Boomer", assets.IMG_BOOMER, 0.3, 0.25, ENEMY, 8, 1, 400, 0.05, 3000, 250,
                          weapon_func=grenade_shot, death_func=boomer_loot, hitbox_size=Vec(70, 70))

def new_zoomer():
    return RangedAIEntity("Zoomer", assets.IMG_ZOOMER, 0.3, speed=0.55, team=ENEMY, health=6, damage=2, sight_range=300,
                          follow_weight=0.05, atk_interval=300, retreat_range=200,
                          weapon_func=single_shot, death_func=zoomer_loot, hitbox_size=Vec(70, 70))

def new_car():
    car = AIEntity("Car", assets.IMG_CAR_FRONT, 0.5, 0.5, ENEMY, health=14, damage=2, sight_range=300, follow_weight=0.1,
                    atk_interval=5000, retreat_range=400, death_func=car_loot)

    car.right_image = assets.IMG_CAR_SIDE
    car.left_image = pygame.transform.flip(car.right_image, True, False)
    return car

def new_cooler():
    return RangedAIEntity("Cooler", assets.IMG_COOLER, 0.4, speed=0.45, team=ENEMY, health=8, damage=1, sight_range=400,
                          follow_weight=0.05, atk_interval=6000, retreat_range=300, weapon_func=freeze_ray_shot,
                          death_func=cooler_loot, hitbox_size=Vec(80, 80))

def new_freezer():
    return RangedAIEntity("Freezer", assets.IMG_FREEZER, 0.7, speed=0.5, team=ENEMY, health=40, damage=1, sight_range=400,
                          follow_weight=0.03, atk_interval=4500, retreat_range=400, weapon_func=freeze_ray_shot,
                          death_func=freezer_loot, hitbox_size=Vec(140, 170))


def new_ally_troop():
    return RangedAIEntity("Troop", assets.IMG_TROOP, 0.275, 0.4, ALLY, 8, 1, sight_range=600, follow_weight=0.05,
                          atk_interval=1500, retreat_range=350, weapon_func=single_shot, hitbox_size=Vec(64, 64))


def new_apple_item():
    return Item("Apple", assets.IMG_APPLE, 0.25, lambda: player.heal(10), condition=player.can_heal)

def new_dmg_up_item():
    return Item("Dmg Up", assets.IMG_DMG_UP, 0.25, lambda: player.raise_damage_multiplier(0.5))

def new_shield_item():
    return Item("Shield", assets.IMG_SHIELD, 0.25, lambda: player.raise_max_health(10))


def new_shotgun_item():
    return Item("Shotgun", assets.IMG_SHOTGUN, 0.25, lambda: gain_powerup(shotgun))

def new_arrows_item():
    return Item("Arrows", assets.IMG_ARROWS, 0.25, lambda: gain_powerup(arrows))

def new_grenade_item():
    return Item("Grenade", assets.IMG_GRENADE, 0.25, lambda: gain_powerup(grenade))

def new_freeze_ray_item():
    return Item("Freeze Ray", assets.IMG_FREEZE_RAY, 0.25, lambda: gain_powerup(freeze_ray))

def new_speed_item():
    return Item("Speed Shoes", assets.IMG_SPEED_SHOES, 0.25, lambda: gain_powerup(speed_shoes))

def new_metalsuit_item():
    return Item("Metalsuit", assets.IMG_METALSUIT, 0.25, lambda: gain_powerup(metalsuit))

def new_invis_item():
    return Item("Invis", assets.IMG_PLAYER_INVIS, 0.25, lambda: gain_powerup(invis))

def new_troops_item():
    return Item("Troops", assets.IMG_TROOP, 0.18, lambda: increase_troops())#current_world.add(player.pos - Vec(0, 5), new_ally()))

def increase_troops(num=1):
    global placeable_troops
    assets.play_sound(assets.SFX_COLLECT)
    placeable_troops += num


def new_bullet(parent, team, direction, Range):
    return Projectile("Bullet", assets.IMG_PROJECTILE_BULLET, 1, 1.25, team, None, 2, direction, Range, parent=parent,
                      death_func=spawn_poof, blockable=True)

def single_shot(world, parent, team, direction):
    assets.play_sound(assets.random_shoot_sfx(), parent.pos, player.pos)
    world.add(parent.pos, new_bullet(parent, team, direction, 500))

def shotgun_shot(world, parent, team, direction):
    assets.play_sound(assets.SFX_SHOOT_SG, parent.pos, player.pos)
    total_spread = 35
    count = 3
    current_angle = -total_spread/2
    for i in range(count):
        new_direction = Vec.polar(1, current_angle - direction.angle())
        world.add(parent.pos, new_bullet(parent, team, new_direction, 250))
        world.add(parent.pos, new_bullet(parent, team, new_direction, 250))
        current_angle += total_spread / (count - 1)

def arrow_shot(world, parent, team, direction):
    assets.play_sound(assets.SFX_SHOOT_ARROW, parent.pos, player.pos)
    arrow = Projectile("Arrow", assets.IMG_PROJECTILE_ARROW, 0.75, 1.8, team, None, 2, direction, 650, parent=parent, death_func=spawn_poof, blockable=False)
    world.add(parent.pos, arrow)

def grenade_shot(world, parent, team, direction):
    assets.play_sound(assets.SFX_SHOOT_GRENADE, parent.pos, player.pos)
    g = Projectile("Grenade", assets.IMG_GRENADE, 0.2, 1, team, None, 3, direction, 400, parent=parent,
                   death_func=spawn_explosion, blockable=True)
    world.add(parent.pos, g)

def freeze_ray_shot(world, parent, team, direction):
    assets.play_sound(assets.SFX_SHOOT_GRENADE, parent.pos, player.pos)
    s = Projectile("Freeze Ray Shot", assets.IMG_PROJECTILE_SNOWFLAKE, 0.4, 1.5, team, None, 2, direction, 400, parent=parent,
                   death_func=spawn_frozen_cloud, blockable=True)
    world.add(parent.pos, s)

def spawn_grave(self, world, team):
    world.add(self.pos, Entity("Grave", assets.IMG_GRAVE, 0.35, health=50, team=team, solid=True, death_func=spawn_explosion))

def spawn_explosion(self, world, team):
    assets.play_sound(assets.SFX_BOOM, self.pos, player.pos)
    explosion = Projectile("Explosion", assets.IMG_EXPLOSION, 0.45, 0.3, team, None, 2, self.vel, 1000, blockable=False, rotate=False)
    explosion.lifetime = 200
    world.add(self.pos, explosion)

def freeze(self, other):
    if other.speed > 0: # Only freeze entities that can move
        other.frozen_timer = 3000

def spawn_frozen_cloud(self, world, team):
    assets.play_sound(assets.SFX_FREEZE, self.pos, player.pos)
    cloud = Projectile("Frozen Cloud", assets.IMG_FROZEN_CLOUD, 0.6, 0.3, team, None, 1, self.vel, 1000,
                       blockable=False, rotate=False, collide_func=freeze)
    cloud.lifetime = 400
    world.add(self.pos, cloud)

def spawn_poof(self, world, team):
    poof = Entity("Poof", assets.IMG_POOF, 1, 0.01, NEUTRAL)
    poof.lifetime = 100
    poof.rotate(random.randint(0, 360))
    world.add(self.pos, poof)
    #world.add(self.pos, Projectile("Poof", assets.IMG_POOF, 0.25, 0.75, NEUTRAL, None, 0, self.vel, 20, blockable=False, parent=self, rotate=False))


def drop_item(pos, item, world):
    world.add(pos + Vec.polar(35, random.randint(0, 360)), item)
    item.keep_in_bounds(world)

def tree_loot(self, world, team):
    if random.randint(0, 1):
        drop_item(self.pos, new_apple_item(), world)

def brawler_loot(self, world, team):
    if random.random() < 0.25:
        loot = random.choice((new_shotgun_item, new_speed_item))
        drop_item(self.pos, loot(), world)
    if random.random() < 0.1:
        drop_item(self.pos, new_troops_item(), world)

def ranger_loot(self, world, team):
    if random.random() < 0.25:
        loot = random.choice((new_arrows_item, new_invis_item, new_apple_item))
        drop_item(self.pos, loot(), world)
    if random.random() < 0.1:
        drop_item(self.pos, new_troops_item(), world)

def boomer_loot(self, world, team):
    spawn_explosion(self, world, team)
    if random.random() < 0.2:
        loot = random.choice((new_grenade_item,))
        drop_item(self.pos, loot(), world)
    if random.random() < 0.2:
        drop_item(self.pos, new_troops_item(), world)

def zoomer_loot(self, world, team):
    spawn_explosion(self, world, team)
    if random.random() < 0.15:
        loot = random.choice((new_metalsuit_item, new_shield_item))
        drop_item(self.pos, loot(), world)
    if random.random() < 0.2:
        drop_item(self.pos, new_troops_item(), world)

def car_loot(self, world, team):
    spawn_explosion(self, world, team)
    if random.random() < 0.3:
        drop_item(self.pos, new_metalsuit_item(), world)
    if random.random() < 0.1:
        drop_item(self.pos, new_troops_item(), world)

def brawler_boss_loot(self, world, team):
    loot = random.choice((new_shield_item, new_dmg_up_item))
    drop_item(self.pos, loot(), world)

def ranger_boss_loot(self, world, team):
    drop_item(self.pos, new_arrows_item(), world)
    drop_item(self.pos, new_invis_item(), world)
    drop_item(self.pos, new_apple_item(), world)

def cooler_loot(self, world, team):
    if random.random() < 0.5:
        drop_item(self.pos, new_freeze_ray_item(), world)
    if random.random() < 0.1:
        drop_item(self.pos, new_troops_item(), world)

def freezer_loot(self, world, team):
    drop_item(self.pos, new_freeze_ray_item(), world)
    drop_item(self.pos, new_metalsuit_item(), world)

Globals.cursor_img = assets.IMG_CURSOR_TARGET


def draw_cursor(surface):
    size = Vec(58, 58)
    cursor = pygame.transform.scale(Globals.cursor_img, size.tuple())
    pos = MOUSE_POS

    if Globals.cursor_img == assets.IMG_CURSOR_ARROW:
        pos = Vec(MOUSE_POS + size/2)

    rect = util.rect_center(pos, size)
    surface.blit(cursor, rect)



class Player(Entity):
    def __init__(self, name, image, image_scale, speed, team, health, death_func=None, hurt_func=None):
        super().__init__(name, image, image_scale, team, health, death_func=death_func)
        self.speed = speed
        self.hurt_func = hurt_func
        self.is_player = True
        self.damage_multiplier = 1

    def update(self, world, player):
        super().update(world, player)
        if self.shake_timer <= 0 and powerups[metalsuit] <= 0 and powerups[invis] <= 0:
            self.set_image(assets.IMG_PLAYER_ALIVE)

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

    def collide(self, other, world):
        global interact
        super().collide(other, world)

        if isinstance(other, Portal):
            if interact:
                new_world = other.destination_world()
                new_position = other.destination_position()

                if new_world is not None:
                    # Go to the portal's destination world and position
                    set_world(new_world)
                if new_position is not None:
                    self.pos = new_position
                self.keep_in_bounds(new_world)
            interact = False


    def hurt(self, amount, world):
        super().hurt(amount, world)
        self.shake_timer = 150
        deplete_powerup(metalsuit, amount*500)
        if powerups[metalsuit] <= 0 and powerups[invis] <= 0:
            self.set_image(assets.IMG_PLAYER_OW)

    def heal(self, amount):
        self.health += amount
        self.health = min(self.health, self.max_health)
        assets.play_sound(assets.SFX_EAT)

    def can_heal(self):
        return self.health < self.max_health

    def raise_max_health(self, amount):
        self.max_health += amount
        assets.play_sound(assets.SFX_BUFF)

    def raise_damage_multiplier(self, amount):
        self.damage_multiplier += amount
        #print(self.damage_multiplier)
        assets.play_sound(assets.SFX_BUFF)


def set_world(new_world):
    global current_world

    if player in current_world.entities:
        current_world.remove(player)

        # Switch music if new world's song is different. Else, continue the old song
        if new_world.music != current_world.music:
            new_world.start_music()

        current_world = new_world
        new_world.add(Vec(new_world.size/2), player)



class Powerup:
    def __init__(self, name, image, default_amount):
        self.name = name
        self.image = util.scale_image(image, 0.25)
        self.default_amount = default_amount
        self.current_max = default_amount

# Add time/uses from powerup
def gain_powerup(powerup, amount=None):
    if amount is None:
        amount = powerup.default_amount
    powerups[powerup] += amount
    assets.play_sound(assets.SFX_COLLECT)
    #powerups[powerup] = min(powerups[powerup], powerup.default_amount)
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
    elif key == pygame.K_QUOTE:
        current_world.add(mouse_world_pos, new_car())
    elif key == pygame.K_h:
        current_world.add(mouse_world_pos, new_ally_troop())
    elif key == pygame.K_t:
        current_world.add(mouse_world_pos, new_ranger_boss())
    elif key == pygame.K_y:
        current_world.add(mouse_world_pos, new_zoomer())
    elif key == pygame.K_u:
        current_world.add(mouse_world_pos, new_cooler())
    elif key == pygame.K_i:
        current_world.add(mouse_world_pos, new_freezer())

    elif key == pygame.K_1:
        current_world.add(mouse_world_pos, new_apple_item())
    elif key == pygame.K_2:
        current_world.add(mouse_world_pos, new_shield_item())
    elif key == pygame.K_3:
        current_world.add(mouse_world_pos, new_dmg_up_item())

    elif key == pygame.K_4:
        current_world.add(mouse_world_pos, new_shotgun_item())
    elif key == pygame.K_5:
        current_world.add(mouse_world_pos, new_arrows_item())
    elif key == pygame.K_6:
        current_world.add(mouse_world_pos, new_speed_item())
    elif key == pygame.K_7:
        current_world.add(mouse_world_pos, new_metalsuit_item())
    if key == pygame.K_8:
        current_world.add(mouse_world_pos, new_grenade_item())
    if key == pygame.K_9:
        current_world.add(mouse_world_pos, new_invis_item())
    elif key == pygame.K_0:
        current_world.add(mouse_world_pos, new_troops_item())
    elif key == pygame.K_MINUS:
        current_world.add(mouse_world_pos, new_freeze_ray_item())

    elif key == pygame.K_v:
        Globals.debug_mode = not Globals.debug_mode
    elif key == pygame.K_c:
        Globals.show_overlay = not Globals.show_overlay

    elif key == pygame.K_b:
        if current_world in worlds:
            index = worlds.index(current_world) - 1
            index = util.wraparound(index, 0, len(worlds) - 1)
            set_world(worlds[index])
        else:
            set_world(worlds[0])

    elif key == pygame.K_n:
        if current_world in worlds:
            index = worlds.index(current_world) + 1
            index = util.wraparound(index, 0, len(worlds) - 1)
            set_world(worlds[index])
        else:
            set_world(worlds[0])


running = True

if __name__ == "__main__":
    while running:
        restart = False
        frames = 0


        shotgun = Powerup("Shotgun", assets.IMG_SHOTGUN, 12000)
        arrows = Powerup("Arrows", assets.IMG_ARROWS, 15000)
        grenade = Powerup("Grenade", assets.IMG_GRENADE, 15000)
        freeze_ray = Powerup("Freeze Ray", assets.IMG_FREEZE_RAY, 10000)
        speed_shoes = Powerup("Speed", assets.IMG_SPEED_SHOES, 10000)
        invis = Powerup("Invis", assets.IMG_PLAYER_INVIS, 8000)
        metalsuit = Powerup("Metalsuit", assets.IMG_METALSUIT, 10000)

        # Amount of time/uses left for each powerup
        powerups = {
            shotgun: 0,
            arrows: 0,
            grenade: 0,
            freeze_ray: 0,
            speed_shoes: 0,
            metalsuit: 0,
            invis: 0,
        }

        last_shoot_time = 0
        last_shotgun_time = 0
        last_arrow_time = 0
        last_grenade_time = 0
        last_freeze_ray_time = 0

        placeable_troops = 3


        worlds = []

        overworld = World("Overworld", Vec(2500, 2500), (220, 200, 140), (85, 175, 95), music=assets.MUSIC_OVERWORLD)
        worlds.append(overworld)

        city = World("Cityworld", Vec(2500, 2500), (100, 200, 150), (175, 175, 175))#image=assets.IMG_BG_CITY)
        worlds.append(city)

        frostland = World("Frostland", Vec(2500, 3000), (200, 240, 250), (150, 220, 230))
        worlds.append(frostland)

        forest = World("Forestworld", Vec(2250, 2250), (13, 46, 37), (38, 75, 60), dark=True, music=assets.MUSIC_FOREST)
        worlds.append(forest)

        island = World("Island", Vec(3000, 1500), (45, 149, 180), (195, 179, 94))
        worlds.append(island)

        caveworld = World("Caveworld", Vec(1400, 2000), (10, 10, 10), (40, 40, 40), dark=True, solid_border=True, music=assets.MUSIC_CAVE)
        worlds.append(caveworld)


        current_world = overworld
        current_world.start_music()


        player_speed = 0.65
        player = Player("Player", assets.IMG_PLAYER_ALIVE, 0.28, player_speed, ALLY, 20, death_func=spawn_grave)
        overworld.add(overworld.size/2, player)


        cave_entrance = Portal("Cave", assets.IMG_CAVE, 1, solid=True, hitbox_size=Vec(260, 140),
                               hover_message="Enter Cave? (SPACE)")
        overworld.add(Vec(2000, 2000), cave_entrance)

        for i in range(12):
            overworld.add(overworld.rand_pos(), new_rock())

        overworld.add_spawner(Spawner(8000, new_tree, max_num=12, center_spread=1.25, pre_spawned=12))
        overworld.add_spawner(Spawner(5000, new_brawler, max_num=9, max_spawn=3))
        #overworld.add_spawner(Spawner(10000, new_ranger, max_num=3))
        overworld.add_spawner(Spawner(45000, new_brawler_boss, max_num=1))

        for i in range(5):
            size = Vec(random.randint(700, 1250), random.randint(750, 1250))
            entrance = Portal("House", assets.IMG_HOUSE, 0.9, hitbox_size=Vec(160, 220), solid=True)
            house_world = World("House world #" + str(i), size, (100, 55, 36), (185, 153, 110), solid_border=True)
            enemy_sets = ((4, new_brawler), (3, new_ranger), (3, new_boomer), (1, new_brawler_boss), (1, new_ranger_boss))
            overworld.add_dungeon(overworld.rand_pos(), new_dungeon(entrance, house_world, enemy_sets))


        for i in range(8):
            city.add(overworld.rand_pos(), new_street_light())
        for i in range(5):
            entrance = Portal("Office", assets.IMG_OFFICE, 1, hitbox_size=Vec(150, 185), solid=True)
            size = Vec(random.randint(600, 800), random.randint(600, 800))
            office_world = World("Office world #" + str(i), size, (91, 108, 120), (191, 180, 147), solid_border=True)
            enemy_sets = ((4, new_brawler), (3, new_ranger), (3, new_boomer), (1, new_brawler_boss), (1, new_ranger_boss), (2, new_zoomer))
            city.add_dungeon(city.rand_pos(), new_dungeon(entrance, office_world, enemy_sets))

        #city_world.add_spawner(Spawner(0, new_office, max_num=10, pre_spawned=10))
        city.add_spawner(Spawner(0, new_city_tree, max_num=8, pre_spawned=8))
        city.add_spawner(Spawner(0, new_car, max_num=3, pre_spawned=3))


        frostland.add_spawner(Spawner(6000, new_winter_tree, max_num=6, center_spread=2, pre_spawned=10))
        frostland.add_spawner(Spawner(5000, new_cold_brawler, max_num=6, max_spawn=2))
        frostland.add_spawner(Spawner(7500, new_cooler, max_num=3, max_spawn=1))
        frostland.add_spawner(Spawner(20000, new_freezer, max_num=2, max_spawn=1))


        for i in range(8):
            forest.add(forest.rand_pos(), new_rock())
        forest.add_spawner(Spawner(6000, new_ranger, max_num=4, pre_spawned=2))
        forest.add_spawner(Spawner(3000, new_ranger_boss, max_num=2, pre_spawned=0))
        forest.add_spawner(Spawner(5000, new_winter_tree, max_num=20, pre_spawned=20))

        cave_exit = Portal("Cave Exit", assets.IMG_CAVE_EXIT, 1.25, solid=False,
                           hover_message="Exit Cave? (SPACE)", to_entity=cave_entrance)
        caveworld.add(Vec(700, -80), cave_exit)
        # Reference cave entrances's destination to the cave exit because now the exit is defined
        #cave_entrance.to_world = cave_world
        cave_entrance.to_entity = cave_exit

        caveworld.add_spawner(Spawner(3000, new_brawler_boss, max_num=4, pre_spawned=1))


        for i in range(5):
            entrance = Portal("Igloo", assets.IMG_IGLOO, 0.85, hitbox_size=Vec(185, 185), solid=True)
            size = Vec(random.randint(500, 700), random.randint(500, 700))
            igloo_world = World("Igloo #" + str(i), size, (200, 240, 250), (150, 220, 230), solid_border=True)
            enemy_sets = ((4, new_cold_brawler), (3, new_ranger), (3, new_boomer), (1, new_brawler_boss), (1, new_ranger_boss),
                          (2, new_zoomer), (3, new_cooler), (1, new_freezer))
            frostland.add_dungeon(frostland.rand_pos(), new_dungeon(entrance, igloo_world, enemy_sets))


        while not restart:
            frames += 1
            Globals.delta_time = clock.tick(Globals.FPS)

            keys_pressed = pygame.key.get_pressed()
            interact = False
            mouse_down = False
            MOUSE_POS = Vec(pygame.mouse.get_pos())
            MOUSE_WORLD_POS = world_pos(MOUSE_POS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Exited")
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:
                        if placeable_troops > 0:
                            current_world.add(MOUSE_WORLD_POS, new_ally_troop())
                            placeable_troops -= 1

                    elif event.button == 1:
                        mouse_down = True
                        if MOUSE_POS.x < 55 and MOUSE_POS.y < 60:
                            Globals.sound_on = not Globals.sound_on

                        elif player.health > 0:
                            powerups[invis] = 0


                elif event.type == pygame.KEYDOWN:
                    debug(event.key, MOUSE_WORLD_POS)
                    if event.key == pygame.K_SPACE:
                        interact = True
                    if event.key == pygame.K_r:
                        restart = True
                    if event.key == pygame.K_m:
                        Globals.sound_on = not Globals.sound_on
                        if Globals.sound_on:
                            current_world.start_music()
                        else:
                            pygame.mixer.music.pause()
                    
                elif event.type == pygame.VIDEORESIZE:
                    Globals.SIZE = Vec(event.size)
                    overlay = pygame.Surface(event.size).convert_alpha()

            if player.health > 0 and pygame.mouse.get_pressed(3)[0]:
                standard_gun = True

                if powerups[shotgun] > 0:
                    standard_gun = False
                    if pygame.time.get_ticks() - last_shotgun_time > 400:
                        shotgun_shot(current_world, player, ALLY, MOUSE_WORLD_POS - player.pos)
                        deplete_powerup(shotgun, 750)  # Deplete powerups extra when they are used
                        last_shotgun_time = pygame.time.get_ticks()

                if powerups[arrows] > 0:
                    standard_gun = False
                    if pygame.time.get_ticks() - last_arrow_time > 250:
                        arrow_shot(current_world, player, ALLY, MOUSE_WORLD_POS - player.pos)
                        deplete_powerup(arrows, 500)
                        last_arrow_time = pygame.time.get_ticks()

                if powerups[grenade] > 0:
                    standard_gun = False
                    if pygame.time.get_ticks() - last_grenade_time > 400:
                        grenade_shot(current_world, player, ALLY, MOUSE_WORLD_POS - player.pos)
                        deplete_powerup(grenade, 1000)
                        last_grenade_time = pygame.time.get_ticks()

                if powerups[freeze_ray] > 0:
                    standard_gun = False
                    if pygame.time.get_ticks() - last_freeze_ray_time > 400:
                        freeze_ray_shot(current_world, player, ALLY, MOUSE_WORLD_POS - player.pos)
                        deplete_powerup(freeze_ray, 1000)
                        last_freeze_ray_time = pygame.time.get_ticks()

                if standard_gun and pygame.time.get_ticks() - last_shoot_time > 250:
                    single_shot(current_world, player, ALLY, MOUSE_WORLD_POS - player.pos)
                    last_shoot_time = pygame.time.get_ticks()


            # Destroy dungeons whose enemies have been defeated
            for dungeon in current_world.dungeons:
                if len(dungeon.destination_world().enemies) == 0:
                    dungeon.world.remove(dungeon)
                    current_world.dungeons.remove(dungeon)
                    spawn_explosion(dungeon, dungeon.world, team=player)


            # Automatically deplete powerups as time goes on
            deplete_powerup(shotgun, Globals.delta_time)
            deplete_powerup(grenade, Globals.delta_time)
            deplete_powerup(arrows, Globals.delta_time)
            deplete_powerup(freeze_ray, Globals.delta_time)
            deplete_powerup(invis, Globals.delta_time)
            deplete_powerup(metalsuit, Globals.delta_time)

            # Speed up with speed shoes but slow down with metalsuit
            if powerups[speed_shoes] > 0:
                if powerups[metalsuit] > 0:
                    player.speed = player_speed * 1.25
                else:
                    player.speed = player_speed * 1.4
                deplete_powerup(speed_shoes, Globals.delta_time)
            else:
                if powerups[metalsuit] > 0:
                    player.speed = player_speed * 0.8
                else:
                    player.speed = player_speed


            if powerups[invis] > 0:
                player.set_image(assets.IMG_PLAYER_INVIS)
            elif powerups[metalsuit] > 0:
                player.set_image(assets.IMG_PLAYER_METALSUIT)
                player.invincible = True
                player.take_knockback = False
            else:
                player.invincible = False
                player.take_knockback = True

            if powerups[metalsuit] <= 0 and powerups[invis] <= 0:
                if player.current_image is not assets.IMG_PLAYER_OW and player.current_image is not assets.IMG_PLAYER_DEAD:
                    player.set_image(assets.IMG_PLAYER_ALIVE)


            player.control(keys_pressed)

            for s in current_world.spawners:
                s.update(current_world)

            for e in current_world.entities:
                e.update(current_world, player)

            for e in current_world.entities:
                for other in current_world.entities:
                    if e is not other and e.colliding(other):
                        e.collide(other, current_world)
                        e.last_collisions.add(other)
                    else:
                        e.last_collisions.discard(other)

                if not e.alive:
                    current_world.remove(e)

            if current_world.dark:
                # Overlay transparent background to make some worlds darker
                overlay.fill((0, 0, 0, 70))
            else:
                overlay.fill((0, 0, 0, 0))

            # Render the game's foreground layer
            window.fill(current_world.outer_color)
            blit_pos = -player.pos + Globals.SIZE/2
            current_world.render(window, blit_pos)

            current_world.entities.sort(key = lambda e: e.pos.y + e.size.y/2)
            for e in current_world.entities:
                e.render(window, overlay, screen_pos(Vec(e.hitbox().center)))

            # Render overlay layer
            if Globals.show_overlay:
                stats = [
                    "# Existing Troops: " + str(len(current_world.allies)),
                    "# Placeable Troops: " + str(placeable_troops) + "  (Right click)",
                    "Position: " + str(player.pos.rounded()),
                    "World: " + current_world.name,
                    "Damage Multiplier: * " + str(round(player.damage_multiplier, 1)),
                    "Health: " + str(max(0, round(player.health))) + "/" + str(max(0, round(player.max_health))),
                ]

                if Globals.debug_mode:
                    stats.append("# Entities: " + str(len(current_world.entities)))
                    stats.append("FPS: " + str(round(clock.get_fps(), 1)))

                util.draw_bar(overlay, Vec(115, Globals.SIZE.y - 35 * 6 - 6), Vec(200, 33),
                              player.health / player.max_health, (80, 130, 255), (0, 0, 0), center=False)

                stat_y = Globals.SIZE.y - 15  # - 35
                for stat in stats:
                    stat_y -= 35
                    util.write(overlay, stat, assets.MAIN_FONT, 34, Vec(10, stat_y), (255, 255, 255))

                if player.health <= 0:
                    util.write(overlay, "Press R to restart", assets.MAIN_FONT, 45, Globals.SIZE/2 + Vec(0, 100), (255, 255, 255),
                               center=True)
                x = 0
                y = 0
                for powerup in powerups:
                    if powerups[powerup] > 0:
                        image_size =  powerup.image.get_width()/2
                        image_pos = Vec(Globals.SIZE.x - 95 + image_size/2, 5 + image_size/2) + (Vec(-x * 80, y * 110))
                        overlay.blit(powerup.image, image_pos.tuple())
                        timer_value = min(powerups[powerup] / powerup.current_max, 1)
                        util.draw_bar(overlay, image_pos + Vec(35, 85), Vec(50, 6), timer_value, (255, 255, 255),
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
                overlay.blit(sound_icon, (0, 0))

            draw_cursor(overlay)

            window.blit(overlay, (0, 0))
            pygame.display.flip()
