import json
import os

import pygame

from EarthClasses import Earth
from FireClasses import Fire
from WaterClasses import Water
from constants import FPS, fire_image_name, water_image_name, earth_image_name
from main_classes import ElementSprite, NewSprite

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

TWO_PLAYERS = False

G = 60 / FPS  # Free-falling altitude
JUMP_SPEED = 900 / FPS  # Vertical speed on jump
FRAMES_CAN_JUMP = 10
PLAYER_SIZE = 50
PLAYER_MASS = 1000
AVG_GET = 0.1  # How much mass get if players is touching

HOR_ALT = 60 / FPS  # Horizontal altitude

MAX_VERT_SPEED = 1000 / FPS
MAX_GOR_SPEED = 1000 / FPS
BLAST_MAX_VERT_SPEED = 3000 / FPS
BLAST_MAX_HOR_SPEED = 3000 / FPS

FRAMES_TO_RELOAD = FPS / 3  # Frames between blasts

BLAST_GET = 0.3  # How much mass player need to blast
BLAST_MAX_SIZE = 40
BLAST_MIN_SIZE = 10
GROWING_SPEED = 0.5  # Blast growing speed
HIT_COOLDOWN = FPS / 2

BOUNCE = 0.25
BLAST_BOUNCE = 0.8

folder_with_levels = "levels"
SEP = os.sep
mass_ind_file_name = "mass.png"


def place_obj(Obj, screen, cords, sprites, size=None):
    obj = Obj(screen, cords, sprites, size)


class ObjectWithPhysics(ElementSprite):  # Class of object that follows physics laws
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_name = args[0]
        self.screen = args[1]
        self.x, self.y = args[2]
        self.size = args[4]

        self.max_vx, self.max_vy = MAX_GOR_SPEED, MAX_VERT_SPEED
        self.vx, self.vy = 0, 0
        self.ax, self.ay = 0, G

        self.can_move_y = True
        self.can_move_x = True

        self.bounce = BOUNCE

        self.mass = self.size

    def set_char_s(self, vx=None, vy=None, ax=None, ay=None, max_vx=None, max_vy=None):  # Change speed or altitude
        orig_char_s = [self.vx, self.vy, self.ax, self.ay, self.max_vx, self.max_vy]
        new_char_s = [vx, vy, ax, ay, max_vx, max_vy]
        for i in range(len(new_char_s)):
            if (new_char_s[i] is None):
                new_char_s[i] = orig_char_s[i]

        self.vx, self.vy, self.ax, self.ay, self.max_vx, self.max_vy = new_char_s

    def move_check(self, blocker: pygame.sprite.Group):  # Checking can it move to the next position
        self.can_move_y = self.is_possible_to_move(0, self.vy + self.ay, blocker)
        self.can_move_x = self.is_possible_to_move(self.vx + self.ax, 0, blocker)
        d = -5
        f = self.is_possible_to_move(self.vx + self.ax, d, blocker)
        if (f and not self.can_move_x):
            self.can_move_x = f
            self.y += d

        if (not self.can_move_y):  # There is implementation of bounce from surfaces
            self.vy = self.vy * -1 * self.bounce

        if (not self.can_move_x):
            self.vx = self.vx * -1 * self.bounce

    def is_possible_to_move(self, dx, dy, blocker: pygame.sprite.Group):  # Check actually the next position
        self.rect.x += dx
        self.rect.y += dy
        collide_with = []
        for sprite in blocker:
            if pygame.sprite.collide_rect(self, sprite):
                collide_with.append(sprite)
        self.rect.x -= dx
        self.rect.y -= dy
        if (collide_with):
            return False
        else:
            return True

    def update(self, *args, **kwargs):
        if (self.can_move_x):
            self.vx += self.ax
            if (abs(self.vx) >= self.max_vx):
                self.vx -= self.ax
            self.x += self.vx

        if (self.can_move_y):
            self.vy += self.ay
            if (abs(self.vy) >= self.max_vy):
                self.vy -= self.ay

            self.y += self.vy

        if (self.mass <= 0):
            self.annigilation()

        super().update()

    def annigilation(self):  # What if objects is not existing?
        self.remove(self.groups()[0])


def avg(obj1: ObjectWithPhysics, obj2: ObjectWithPhysics, k):
    avg = ((obj1.mass + obj2.mass) // 2) * k
    return avg


def get_first(obj1: ObjectWithPhysics, obj2: ObjectWithPhysics):
    obj2.mass -= obj1.mass
    obj1.mass = 0


def throw_from_epicentre_to_point(epicentre, point, speed):  # Changing objects x and y speed multipliers for simulating
    ex, ey = epicentre  # object shot from epicentre to point with given speed
    x, y = point
    dx, dy = x - ex, y - ey
    gyp = (dx ** 2 + dy ** 2) ** 0.5
    k = speed / gyp
    vx, vy = k * dx, k * dy
    return vx, vy


class Blast(ObjectWithPhysics):  # Class of the flying object, that shot from players
    def __init__(self, image_name, screen, cords, epicentre, group=None, size=None):
        super().__init__(image_name, screen, cords, group, size)
        self.image_name = image_name
        self.x, self.y = cords
        self.ex, self.ey = epicentre

        self.max_vx, self.max_vy = BLAST_MAX_HOR_SPEED, BLAST_MAX_VERT_SPEED
        self.bounce = BLAST_BOUNCE

        self.count_speed()
        self.count_params()

    def count_params(self):  # Count number of bounces depend on size
        if (self.size < BLAST_MIN_SIZE + 5):
            self.bounces = 0
        else:
            self.bounces = self.size // 5

    def count_speed(self):
        self.speed = (100 - self.size) / 2
        self.vx, self.vy = throw_from_epicentre_to_point((self.ex, self.ey), (self.x, self.y), self.speed)

    def move_check(self, blocker: pygame.sprite.Group):
        super().move_check(blocker)

        if ((not self.can_move_y or not self.can_move_x) and self.bounces is not None):
            self.bounces -= 1

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)

        if (self.bounces == -1 or not (0 < self.x < SCREEN_WIDTH) or not (0 < self.y < SCREEN_HEIGHT)):
            if (self.groups()):
                self.remove(self.groups()[0])


class Player(ObjectWithPhysics):  # Class of player: jumping, blasting, running, etc.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_name = args[0]
        self.screen = args[1]
        self.x, self.y = args[2]
        self.size = args[4]

        self.jumping = False
        self.jump_reloading = FRAMES_CAN_JUMP

        self.blast_size_extremes = (BLAST_MIN_SIZE, BLAST_MAX_SIZE)
        self.blast_size = self.blast_size_extremes[0]
        self.blasts = pygame.sprite.Group()
        self.frames_to_reload = FRAMES_TO_RELOAD
        self.reloading = self.frames_to_reload

        self.hit_reloading = HIT_COOLDOWN

        self.joystick = None
        self.addicted_sprites = pygame.sprite.Group()
        self.eyes = ElementSprite("eyes.png", self.screen, (self.x, self.y), self.addicted_sprites, self.size)
        self.cursor = ElementSprite(self.image_name, self.screen, (self.x, self.y), self.addicted_sprites,
                                    self.blast_size)

        self.mass = PLAYER_MASS

    def blast(self):
        if (self.reloading == 0):
            blast = Blast(self.image_name, self.screen, (self.cursor.x, self.cursor.y), (self.x, self.y), self.blasts,
                          self.blast_size)
            blast.vx += self.vx
            blast.vy += self.vy
            self.mass -= self.blast_size * BLAST_GET
            self.blast_size = BLAST_MIN_SIZE
            self.reloading = self.frames_to_reload

    def add_joystick(self, joystick):
        self.joystick = joystick

    def jump(self):
        if (not self.jumping):
            self.vy = -JUMP_SPEED
            self.jump_reloading = FRAMES_CAN_JUMP

    def move_check(self, blocker: pygame.sprite.Group):
        super().move_check(blocker)

        if (not self.can_move_y):
            self.jumping = False
        else:
            if (self.jump_reloading > 0):
                self.jumping = True

    def hit_check(self, blasts: pygame.sprite.Group, player):
        for blast in blasts.sprites():
            if (collide_by_circle(self, blast)):
                get_first(blast, self)

        if (self.hit_reloading == 0):
            if (collide_by_circle(self, player)):
                self.mass -= avg(self, player, AVG_GET)
                self.vx, self.vy = throw_from_epicentre_to_point((player.x, player.y), (self.x, self.y), 10)
                self.hit_reloading = HIT_COOLDOWN

    def charge(self):
        if (self.blast_size < BLAST_MAX_SIZE):
            self.blast_size += GROWING_SPEED

    def annigilation(self):
        pass

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)

        if (self.reloading > 0):
            self.reloading -= 1

        if (self.hit_reloading > 0):
            self.hit_reloading -= 1

        if (self.jump_reloading > 0):
            self.jump_reloading -= 1

        if (self.joystick is not None):
            g_a2, g_a3 = self.joystick.get_axis(2), self.joystick.get_axis(3)
            small_gyp = (g_a2 ** 2 + g_a3 ** 2) ** 0.5
            if (-0.1 < small_gyp < 0.1):
                small_gyp = 1
            r = self.size * 0.75
            dx, dy = (r / small_gyp) * g_a2, (r / small_gyp) * g_a3
            self.cursor.x, self.cursor.y = self.x + dx, self.y + dy
        else:
            g_a2, g_a3 = pygame.mouse.get_pos()[0] - self.x, pygame.mouse.get_pos()[1] - self.y
            small_gyp = (g_a2 ** 2 + g_a3 ** 2) ** 0.5
            if (-0.1 < small_gyp < 0.1):
                small_gyp = 1
            r = self.size * 0.75
            dx, dy = (r / small_gyp) * g_a2, (r / small_gyp) * g_a3
            self.cursor.x, self.cursor.y = self.x + dx, self.y + dy

        self.cursor.change_size(self.blast_size)

        self.eyes.x, self.eyes.y = self.x, self.y

        self.addicted_sprites.update()
        self.blasts.update()

        if (not (0 < self.x < SCREEN_WIDTH) or not (0 < self.y < SCREEN_HEIGHT)):
            self.mass = 0

    def draw_mod(self):
        self.addicted_sprites.draw(self.screen)
        self.blasts.draw(self.screen)


class MassIndicator(NewSprite):
    def __init__(self, player, *args, **kwargs):
        super().__init__(mass_ind_file_name, *args, **kwargs)
        self.player = player

        if (player.image_name == fire_image_name):
            self.color = "#ED1C24"
        else:
            self.color = "#1CA8ED"

        self.value = self.player.mass

    def draw_indication(self):
        rect = pygame.rect.Rect(self.rect.x + 8, self.rect.y + 8, self.value, 40)
        pygame.draw.rect(self.screen, self.color, rect)

    def update(self, *args, **kwargs):
        self.draw_indication()
        self.value = int(self.player.mass / 3.42)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        if (TWO_PLAYERS):
            pygame.joystick.init()

            if (pygame.joystick.get_count() == 0):
                print("Please, connect controller/joystick/gamepad")
                pygame.quit()
                return
            else:
                self.joy = pygame.joystick.Joystick(0)

        self.start_screen()

    def choose_level(self):
        levels = list(map(lambda s: s[:-5], os.listdir(folder_with_levels)))

        buttons = ButtonGroup(self.screen)
        font = 50

        for i in range(len(levels)):
            btn = Button((levels[i], (0, 0, 0), (255, 255, 255), font),
                         (SCREEN_WIDTH // 2, 100 + i * font), buttons, self.game, i)
            btn.rect.x -= btn.rect.width // 2

        running = True
        while (running):
            keys = pygame.event.get()
            mods = pygame.key.get_mods()
            for event in keys:
                if (event.type == pygame.QUIT):
                    running = False
                    self.left_game()
                if (event.type == pygame.MOUSEBUTTONUP):
                    buttons.check_event(event)

            self.screen.fill((255, 255, 255))

            buttons.draw()
            buttons.update()
            pygame.display.flip()

    def load_level(self, level_name, sprites, pl1, pl2):
        with open(f"{folder_with_levels}{SEP}{level_name}.json") as f:
            from_save = json.load(f)
            for obj in from_save:
                type = obj["type"]
                x, y, size = map(int, [obj["x"], obj["y"], obj["size"]])
                if type == earth_image_name:
                    sprite = Earth(self.screen, (x, y), sprites, size)
                if type == fire_image_name:
                    pl1.x, pl1.y = x, y
                if type == water_image_name:
                    pl2.x, pl2.y = x, y

    def handle_p1_event(self, event: pygame.event.Event):
        player = self.player1
        if (event.type == pygame.KEYDOWN):
            match event.key:
                # case pygame.K_1:
                #     self.obj_to_create = create_fire
                # case pygame.K_2:
                #     self.obj_to_create = create_earth
                # case pygame.K_3:
                #     self.obj_to_create = create_water

                case pygame.K_w:
                    player.jump()
                case pygame.K_d:
                    player.set_char_s(ax=HOR_ALT)
                case pygame.K_a:
                    player.set_char_s(ax=-HOR_ALT)

        if (event.type == pygame.KEYUP):
            match event.key:
                case pygame.K_w:
                    pass
                case pygame.K_d:
                    player.set_char_s(vx=0, ax=0)
                case pygame.K_a:
                    player.set_char_s(vx=0, ax=0)

        if (event.type == pygame.MOUSEBUTTONUP):
            if (event.button == 1):
                player.blast()

            # if (self.obj_to_create == create_earth):
            #     earth = Earth(self.screen, (event.pos[0], event.pos[1]), ground)
            # else:
            #     self.obj_to_create(self.screen, event, self.player1.addicted_sprites)

    def handle_p2_event(self, event: pygame.event.Event):
        player = self.player2
        if (event.type == pygame.JOYHATMOTION):
            match (event.value[1]):
                case 1:
                    player.jump()
                case -1:
                    pass
                case 0:
                    pass

            match (event.value[0]):
                case 1:
                    player.set_char_s(ax=HOR_ALT)
                case -1:
                    player.set_char_s(ax=-HOR_ALT)
                case 0:
                    player.set_char_s(vx=0, ax=0)

        if (event.type == pygame.JOYBUTTONUP):
            if (event.button == 5):
                player.blast()

    def game(self, level_i):
        self.players = pygame.sprite.Group()
        self.player1 = Player(fire_image_name, self.screen, (400, 300), self.players, PLAYER_SIZE)
        self.player2 = Player(water_image_name, self.screen, (800, 300), self.players, PLAYER_SIZE)
        if (TWO_PLAYERS):
            self.player2.add_joystick(self.joy)

        indicators = pygame.sprite.Group()
        self.mass1 = MassIndicator(self.player1, self.screen, (50, 50), indicators)
        self.mass2 = MassIndicator(self.player2, self.screen, (SCREEN_WIDTH - 350, 50), indicators)

        ground = pygame.sprite.Group()
        level_name = list(map(lambda s: s[:-5], os.listdir(folder_with_levels)))[level_i]
        if (level_name is not None):
            self.load_level(level_name, ground, self.player1, self.player2)

        running = True

        while (running):
            keys = pygame.event.get()
            mods = pygame.key.get_mods()
            for event in keys:
                if (event.type == pygame.QUIT):
                    running = False
                    self.left_game()

                self.handle_p1_event(event)
                self.handle_p2_event(event)

            if (1 in pygame.mouse.get_pressed()):
                self.player1.charge()

            if (TWO_PLAYERS and self.joy.get_button(5)):
                self.player2.charge()

            self.player1.hit_check(self.player2.blasts, self.player2)
            self.player2.hit_check(self.player1.blasts, self.player1)

            self.screen.fill((255, 255, 255))

            for player in self.players.sprites():
                player.move_check(ground)
                for blast in player.blasts.sprites():
                    blast.move_check(ground)

            self.players.update()
            self.players.draw(self.screen)
            for player in self.players.sprites():
                player.draw_mod()

            if (self.player1.mass <= 0):
                self.restart(self.player2)

            if (self.player2.mass <= 0):
                self.restart(self.player1)

            ground.draw(self.screen)
            ground.update()

            indicators.update()
            indicators.draw(self.screen)

            # blocker = ground
            # for block in blocker.sprites():
            #     print("***")
            #     pygame.draw.circle(self.screen, "#000000", (block.x, block.y), block.circle_radius)

            pygame.display.flip()
            self.clock.tick(FPS)

    def restart(self, player):
        buttons = ButtonGroup(self.screen)

        if (player.image_name == fire_image_name):
            color = "#ED1C24"
            congratulations = "1"
        else:
            color = "#1CA8ED"
            congratulations = "2"

        btn = Button((f"Player {congratulations} wins!", color, (255, 255, 255), 100),
                     (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), buttons)
        btn.rect.x -= btn.rect.width // 2
        btn = Button(("Press to restart", (0, 0, 0), (255, 255, 255), 50),
                     (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100), buttons, self.start_screen)
        btn.rect.x -= btn.rect.width // 2

        running = True

        while (running):
            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    running = False
                    self.left_game()
                if (event.type == pygame.MOUSEBUTTONUP):
                    buttons.check_event(event)

            self.screen.fill((255, 255, 255))

            buttons.draw()
            buttons.update()
            pygame.display.flip()
            self.clock.tick(FPS)

    def creating_level(self):
        self.obj_to_create = Earth
        ground = pygame.sprite.Group()

        # d = size // 2
        d = 0
        size = 50
        other_sprites = pygame.sprite.Group()
        indication = Earth(self.screen, pygame.mouse.get_pos(), other_sprites, size)

        is_new = input("Create new map? (N if no)\n") != 'N'
        if (not is_new):
            name = input("Which map to edit?\n")
            self.load_map(name, ground)

        start = None
        end = None

        running = True

        while (running):
            keys = pygame.event.get()
            mods = pygame.key.get_mods()
            for event in keys:
                if (event.type == pygame.QUIT):
                    running = False
                    self.left_game()
                if (event.type == pygame.KEYDOWN):
                    match event.key:
                        case pygame.K_1:
                            self.obj_to_create = Earth
                            indication.image_name = earth_image_name
                            indication.change_size(indication.size)
                        case pygame.K_2:
                            self.obj_to_create = Fire
                            indication.image_name = fire_image_name
                            indication.change_size(indication.size)
                        case pygame.K_3:
                            self.obj_to_create = Water
                            indication.image_name = water_image_name
                            indication.change_size(indication.size)
                        case pygame.K_4:
                            self.obj_to_create = Earth
                            indication.image_name = earth_image_name
                            indication.change_size(indication.size)

                        case pygame.K_s:
                            if (mods & pygame.KMOD_CTRL):
                                self.save_level(ground)
                                running = False

                    if (event.key == pygame.K_4):
                        start = -1
                    else:
                        start = None
                        end = None

                if (event.type == pygame.MOUSEWHEEL):
                    d = 5
                    size += event.y * d
                    if (size <= 0):
                        size -= event.y * d

                if (event.type == pygame.MOUSEBUTTONDOWN):
                    if (event.button != 5 and event.button != 4):
                        f = True
                        for sprite in ground.sprites():
                            if (sprite.del_if_mouse_clicked(event)):
                                f = False
                        if (f):
                            place_obj(self.obj_to_create, self.screen, (event.pos[0], event.pos[1]), ground,
                                      size)

                        if (start == -1):
                            start = pygame.mouse.get_pos()

                if (event.type == pygame.MOUSEBUTTONUP):
                    if (event.button != 5 and event.button != 4):
                        if (start is not None and start != -1):
                            end = pygame.mouse.get_pos()

            if (start is not None and start != -1):
                if (end is not None):
                    dx, dy = end[0] - start[0], end[1] - start[1]
                    dist = (dx ** 2 + dy ** 2) ** 0.5
                    n = int(dist / size)
                    for i in range(1, n + 1):
                        place_obj(self.obj_to_create, self.screen, (start[0] + i * (dx / n), start[1] + i * (dy / n)),
                                  ground,
                                  size)
                    start = -1
                    end = None

            self.screen.fill((255, 255, 255))

            ground.draw(self.screen)
            ground.update()

            indication.change_size(size)

            indication.x, indication.y = list(pygame.mouse.get_pos())
            other_sprites.update()
            other_sprites.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

        self.start_screen()

    def load_map(self, level_name, sprites):
        with open(f"{folder_with_levels}{SEP}{level_name}.json") as f:
            from_save = json.load(f)
            for obj in from_save:
                type = obj["type"]
                x, y, size = map(int, [obj["x"], obj["y"], obj["size"]])
                if type == earth_image_name:
                    obj = Earth
                if type == fire_image_name:
                    obj = Fire
                if type == water_image_name:
                    obj = Water

                place_obj(obj, self.screen, (x, y), sprites, size)

    def save_level(self, saved: pygame.sprite.Group):
        name = input("Enter name of the level\n")
        rewrite = False
        while (f"{name}.json" in os.listdir(folder_with_levels) and not rewrite):
            rewrite = input("Name already exists. Rewrite? (Y/n)\n") == 'Y'
            if (not rewrite):
                name = input("Enter new name\n")

        file_name = f"{folder_with_levels}{SEP}{name}.json"
        open(file_name, mode='w').close()

        with open(file_name, mode='w') as f:
            for_save = []
            for obj in saved:
                for_save.append({
                    "x": obj.x,
                    "y": obj.y,
                    "size": obj.rect.width,
                    "type": obj.image_name})

            json.dump(for_save, f)

    def left_game(self):
        pygame.quit()

    def start_screen(self):
        buttons = ButtonGroup(self.screen)
        btn = Button(("Start game", (0, 200, 0), (255, 255, 255), 50),
                     (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), buttons, self.choose_level)
        btn.rect.x -= btn.rect.width // 2
        btn = Button(("Create level", (0, 0, 0), (255, 255, 255), 50),
                     (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50), buttons, self.creating_level)
        btn.rect.x -= btn.rect.width // 2

        running = True

        while (running):
            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    running = False
                    self.left_game()
                if (event.type == pygame.MOUSEBUTTONUP):
                    buttons.check_event(event)

            self.screen.fill((255, 255, 255))

            buttons.draw()
            buttons.update()
            pygame.display.flip()
            self.clock.tick(FPS)


class Button(pygame.sprite.Sprite):
    def __init__(self, text_args, cords, group, func=None, i=None):
        super().__init__(group)
        self.method_if_triggered = func
        self.i = i
        self.text = text_args[0]
        self.font_color = text_args[1]
        self.bgd_color = text_args[2]
        self.font_size = text_args[3]
        self.font = pygame.font.Font(None, self.font_size)
        self.rendered = self.font.render(self.text, True, self.font_color, self.bgd_color)
        self.rect = self.rendered.get_rect()
        self.rect.x, self.rect.y = cords

    def blit(self, screen):
        screen.blit(self.rendered, (self.rect.x, self.rect.y))

    def update(self, *args, **kwargs):
        if (self.rect.collidepoint(pygame.mouse.get_pos())):
            self.rendered = self.font.render(self.text, True, self.bgd_color, self.font_color)
        else:
            self.rendered = self.font.render(self.text, True, self.font_color, self.bgd_color)

    def check_event(self, event: pygame.event.Event):
        if (self.rect.collidepoint(event.pos)):
            if (self.method_if_triggered is not None):
                if (self.i is None):
                    self.method_if_triggered()
                else:
                    self.method_if_triggered(self.i)


class ButtonGroup(pygame.sprite.Group):
    def __init__(self, screen):
        super().__init__()
        self.screen = screen

    def draw(self):
        for button in self.sprites():
            button.blit(self.screen)

    def update(self, *args, **kwargs):
        for button in self.sprites():
            button.update()

    def check_event(self, event: pygame.event.Event):
        for button in self.sprites():
            button.check_event(event)


def collide_by_circle(first: ElementSprite, second: ElementSprite):
    dx, dy = abs(first.x - second.x), abs(first.y - second.y)
    d = (dx ** 2 + dy ** 2) ** 0.5
    if (d <= first.circle_radius + second.circle_radius):
        return True
    return False


def collide_by_circle_and_rect(first: ElementSprite, second: ElementSprite):
    dx, dy = abs(first.x - second.x), abs(first.y - second.y)
    d = (dx ** 2 + dy ** 2) ** 0.5
    if (d <= first.circle_radius + second.circle_radius):
        return True
    return False


if __name__ == "__main__":
    game = Game()
    print("***")
