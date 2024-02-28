import csv
import os

import pygame

from EarthClasses import Earth
from FireClasses import BurningFire
from constants import FPS, fire_image_name, water_image_name
from main_classes import StaticSpriteGroup, NewSprite


TWO_PLAYERS = False

G = 2
JUMP_SPEED = 30
PLAYER_SIZE = 50

GOR_ALT = 2
MAX_VERT_SPEED = 30
MAX_GOR_SPEED = 30
BLAST_MAX_VERT_SPEED = 100
BLAST_MAX_GOR_SPEED = 100

BOUNCE = 0.25
BLAST_BOUNCE = 0.8

BTN_CREATE_LEVEL = 1
BTN_START_GAME = 2

folder_with_levels = "levels"
SEP = os.sep


def create_fire(screen, event, sprites):
    fire = BurningFire(screen, (event.pos[0], event.pos[1]), sprites)


def create_earth(screen, event, sprites, size):
    earth = Earth(screen, (event.pos[0], event.pos[1]), sprites, size)


def create_water(screen, event, sprites):
    pass


class ObjectWithPhysics(NewSprite):
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

    def set_char_s(self, vx=None, vy=None, ax=None, ay=None, max_vx=None, max_vy=None):
        orig_char_s = [self.vx, self.vy, self.ax, self.ay, self.max_vx, self.max_vy]
        new_char_s = [vx, vy, ax, ay, max_vx, max_vy]
        for i in range(len(new_char_s)):
            if (new_char_s[i] is None):
                new_char_s[i] = orig_char_s[i]

        self.vx, self.vy, self.ax, self.ay, self.max_vx, self.max_vy = new_char_s

    def move_check(self, blocker: pygame.sprite.Group):
        self.can_move_y = self.is_possible_to_move(0, self.vy + self.ay, blocker)
        self.can_move_x = self.is_possible_to_move(self.vx + self.ax, 0, blocker)
        d = -5
        f = self.is_possible_to_move(self.vx + self.ax, d, blocker)
        if (f and not self.can_move_x):
            self.can_move_x = f
            self.y += d

        if (not self.can_move_y):
            self.vy = self.vy * -1 * self.bounce

        if (not self.can_move_x):
            self.vx = self.vx * -1 * self.bounce

    def is_possible_to_move(self, dx, dy, blocker: pygame.sprite.Group):
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

        super().update()


class Blast(ObjectWithPhysics):
    def __init__(self, image_name, screen, cords, epicentre, group=None, size=None):
        super().__init__(image_name, screen, cords, group, size)
        self.image_name = image_name
        self.x, self.y = cords
        self.ex, self.ey = epicentre

        self.max_vx, self.max_vy = BLAST_MAX_GOR_SPEED, BLAST_MAX_VERT_SPEED
        self.bounce = BLAST_BOUNCE

        self.count_speed()
        self.count_params()

    def count_params(self):
        if (self.size > 60):
            self.bounces = None
        elif (self.size < 30):
            self.bounces = 0
        else:
            self.bounces = self.size // 10

    def count_speed(self):
        self.speed = (100 - self.size) / 2
        dx, dy = self.x - self.ex, self.y - self.ey
        gyp = (dx ** 2 + dy ** 2) ** 0.5
        k = self.speed / gyp
        self.vx, self.vy = k * dx, k * dy

    def move_check(self, blocker: pygame.sprite.Group):
        super().move_check(blocker)

        if (not self.can_move_y or not self.can_move_x):
            self.bounces -= 1

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)

        if (self.bounces == -1):
            self.remove(self.groups()[0])



class Player(ObjectWithPhysics):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_name = args[0]
        self.screen = args[1]
        self.x, self.y = args[2]
        self.size = args[4]

        self.jumping = False

        self.blast_size_extremes = (self.size * 0.2, self.size * 0.8)
        self.blast_size = self.blast_size_extremes[0]
        self.blasts = pygame.sprite.Group()

        self.joystick = None
        self.addicted_sprites = pygame.sprite.Group()
        self.eyes = NewSprite("eyes.png", self.screen, (self.x, self.y), self.addicted_sprites, self.size)
        self.cursor = NewSprite(self.image_name, self.screen, (self.x, self.y), self.addicted_sprites, self.blast_size)

    def blast(self):
        blast = Blast(self.image_name, self.screen, (self.cursor.x, self.cursor.y), (self.x, self.y), self.blasts, self.blast_size)

    def add_joystick(self, joystick):
        self.joystick = joystick

    def jump(self):
        if (not self.jumping):
            self.vy = -JUMP_SPEED
            self.jumping = True

    def move_check(self, blocker: pygame.sprite.Group):
        super().move_check(blocker)
        
        if (not self.can_move_y):
            self.jumping = False

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)

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

        self.eyes.x, self.eyes.y = self.x, self.y

        self.addicted_sprites.update()
        self.addicted_sprites.draw(self.screen)
        self.blasts.draw(self.screen)
        self.blasts.update()


class Game:
    def __init__(self):
        pygame.init()
        size = 1280, 720
        self.screen = pygame.display.set_mode(size)
        self.clock = pygame.time.Clock()

        if (TWO_PLAYERS):
            pygame.joystick.init()

            if (pygame.joystick.get_count() == 0):
                print("Please, connect controller/joystick/gamepad")
                pygame.quit()
                return
            else:
                self.joy = pygame.joystick.Joystick(0)

        self.running = True

        self.start_screen()
        # self.game()

    def choose_level(self):
        levels = map(lambda s: s[:-4], os.listdir(folder_with_levels))

        buttons = ButtonGroup(self.screen)
        font = 50

        for i, level in enumerate(levels):
            lvl_btn = Button((level, (0, 0, 0), (255, 255, 255), font),
                                  (10, 10 + i * font), buttons, lambda: self.game(level))

        running = True
        while (running and self.running):
            keys = pygame.event.get()
            mods = pygame.key.get_mods()
            for event in keys:
                if (event.type == pygame.QUIT):
                    running = False
                    self.left_game()
                if(event.type == pygame.MOUSEBUTTONDOWN):
                    buttons.check_event(event)

            self.screen.fill((255, 255, 255))

            buttons.draw()
            buttons.update()
            pygame.display.flip()

    def load_level(self, level_name, sprites):
        with open(f"{folder_with_levels}{SEP}{level_name}.csv") as f:
            reader = csv.reader(f, delimiter=';', lineterminator='\n')
            for i, row in enumerate(reader):
                if (row):
                    row = list(map(int, row))
                    sprite = Earth(self.screen, (row[0], row[1]), sprites, row[2])

    def handle_p1_event(self, event: pygame.event.Event):
        if (event.type == pygame.KEYDOWN):
            match event.key:
                # case pygame.K_1:
                #     self.creating_f = create_fire
                # case pygame.K_2:
                #     self.creating_f = create_earth
                # case pygame.K_3:
                #     self.creating_f = create_water

                case pygame.K_w:
                    self.player1.jump()
                case pygame.K_d:
                    self.player1.set_char_s(ax=GOR_ALT)
                case pygame.K_a:
                    self.player1.set_char_s(ax=-GOR_ALT)

        if (event.type == pygame.KEYUP):
            match event.key:
                case pygame.K_w:
                    pass
                case pygame.K_d:
                    self.player1.set_char_s(vx=0, ax=0)
                case pygame.K_a:
                    self.player1.set_char_s(vx=0, ax=0)
        if (event.type == pygame.MOUSEBUTTONDOWN):
            if (event.button == 1):
                self.player1.blast()

            # if (self.creating_f == create_earth):
            #     earth = Earth(self.screen, (event.pos[0], event.pos[1]), ground)
            # else:
            #     self.creating_f(self.screen, event, self.player1.addicted_sprites)

    def handle_p2_event(self, event: pygame.event.Event):
        if (event.type == pygame.JOYHATMOTION):
            match (event.value[1]):
                case 1:
                    self.player2.jump()
                case -1:
                    pass
                case 0:
                    pass

            match (event.value[0]):
                case 1:
                    self.player2.set_char_s(ax=GOR_ALT)
                case -1:
                    self.player2.set_char_s(ax=-GOR_ALT)
                case 0:
                    self.player2.set_char_s(vx=0, ax=0)

    def game(self, level_name=None):
        self.creating_f = create_earth
        self.players = pygame.sprite.Group()
        self.player1 = Player(fire_image_name, self.screen, (400, 300), self.players, PLAYER_SIZE)
        self.player2 = Player(water_image_name, self.screen, (800, 300), self.players, PLAYER_SIZE)
        if (TWO_PLAYERS):
            self.player2.add_joystick(self.joy)

        ground = pygame.sprite.Group()
        if (level_name is not None):
            self.load_level(level_name, ground)

        while (self.running):
            keys = pygame.event.get()
            mods = pygame.key.get_mods()
            for event in keys:
                if (event.type == pygame.QUIT):
                    self.left_game()

                self.handle_p1_event(event)
                self.handle_p2_event(event)

            self.screen.fill((255, 255, 255))

            for player in self.players.sprites():
                player.move_check(ground)
                for blast in player.blasts.sprites():
                    blast.move_check(ground)

            self.players.draw(self.screen)
            self.players.update()
            ground.draw(self.screen)
            ground.update()
            pygame.display.flip()
            self.clock.tick(FPS)

    def creating_level(self):
        self.creating_f = create_earth
        ground = pygame.sprite.Group()

        # d = size // 2
        d = 0
        size = 50
        other_sprites = pygame.sprite.Group()
        indication = Earth(self.screen, pygame.mouse.get_pos(), other_sprites, size)

        running = True

        while (running and self.running):
            keys = pygame.event.get()
            mods = pygame.key.get_mods()
            for event in keys:
                if (event.type == pygame.QUIT):
                    running = False
                    self.left_game()
                if (event.type == pygame.KEYDOWN):
                    match event.key:
                        case pygame.K_1:
                            self.creating_f = create_fire
                        case pygame.K_2:
                            self.creating_f = create_earth
                        case pygame.K_3:
                            self.creating_f = create_water
                        case pygame.K_s:
                            if (mods & pygame.KMOD_CTRL):
                                self.save_level(ground)
                                running = False
                if (event.type == pygame.MOUSEWHEEL):
                    d = 5
                    size += event.y * d
                    if (size < 0):
                        size -= event.y * d

                if (event.type == pygame.MOUSEBUTTONDOWN):
                    if (event.button != 5 and event.button != 4):
                        f = True
                        for sprite in ground.sprites():
                            if (sprite.del_if_mouse_clicked(event)):
                                f = False
                        if (f):
                            if (self.creating_f == create_earth):
                                earth = Earth(self.screen, (event.pos[0] + d, event.pos[1] + d), ground, size)
                            # else:
                            #     self.creating_f(self.screen, event, self.player1.addicted_sprites)

            self.screen.fill((255, 255, 255))

            ground.draw(self.screen)
            ground.update()

            indication.change_size(size)

            indication.x, indication.y = map(lambda x: x + d, list(pygame.mouse.get_pos()))
            other_sprites.draw(self.screen)
            other_sprites.update()

            pygame.display.flip()
            self.clock.tick(FPS)

        self.start_screen()

    def save_level(self, saved: pygame.sprite.Group):
        name = input()
        while (f"{name}.csv" in os.listdir(folder_with_levels)):
            name = input("Name already exists\n")

        file_name = f"{folder_with_levels}{SEP}{name}.csv"
        open(file_name, mode='w').close()

        with open(file_name, mode='w') as f:
            writer = csv.writer(f, delimiter=';', lineterminator='\n')
            for obj in saved:
                writer.writerow([obj.x, obj.y, obj.rect.width])

    def left_game(self):
        self.running = False
        pygame.quit()

    def start_screen(self):
        buttons = ButtonGroup(self.screen)
        create_level = Button(("Create level", (0, 0, 0), (255, 255, 255), 50),
                              (0, 0), buttons, self.creating_level)
        start_game = Button(("Start game", (0, 0, 0), (255, 255, 0), 50),
                            (0, 50), buttons, self.choose_level)

        is_in_menu = True
        running = True

        while (self.running and is_in_menu and running):
            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    self.left_game()
                if(event.type == pygame.MOUSEBUTTONDOWN):
                    running = False
                    buttons.check_event(event)

            self.screen.fill((255, 255, 255))

            buttons.draw()
            buttons.update()
            pygame.display.flip()
            self.clock.tick(FPS)


class Button(pygame.sprite.Sprite):
    def __init__(self, text_args, cords, group, func):
        super().__init__(group)
        self.method_if_triggered = func
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
        if(event.type == pygame.MOUSEBUTTONDOWN):
            if (self.rect.collidepoint(event.pos)):
                self.method_if_triggered()


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


def collide_by_circle(first: NewSprite, second: NewSprite):
    dx, dy = abs(first.x - second.x), abs(first.y - second.y)
    d = (dx ** 2 + dy ** 2) ** 0.5
    if (d <= first.circle_radius + second.circle_radius):
        return True
    return False


def collide_by_circle_and_rect(first: NewSprite, second: NewSprite):
    dx, dy = abs(first.x - second.x), abs(first.y - second.y)
    d = (dx ** 2 + dy ** 2) ** 0.5
    if (d <= first.circle_radius + second.circle_radius):
        return True
    return False


if __name__ == "__main__":
    game = Game()
