import pygame

from EarthClasses import Earth
from FireClasses import BurningFire
from constants import FPS, fire_image_name
from main_classes import StaticSpriteGroup, NewSprite


G = 2
JUMP_SPEED = 30

GOR_ALT = 3
MAX_VERT_SPEED = 30
MAX_GOR_SPEED = 30

BTN_CREATE_LEVEL = 1
BTN_START_GAME = 2


def create_fire(screen, event, sprites):
    fire = BurningFire(screen, (event.pos[0], event.pos[1]), sprites)

def create_earth(screen, event, sprites):
    earth = Earth(screen, (event.pos[0], event.pos[1]), sprites)

def create_water(screen, event, sprites):
    pass


class Player(NewSprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.screen = args[1]
        self.x, self.y = args[2]

        self.max_vx, self.max_vy = MAX_GOR_SPEED, MAX_VERT_SPEED
        self.vx, self.vy = 0, 0
        self.ax, self.ay = 0, G

        self.can_move_y = True
        self.can_move_x = True

        self.jumping = False

        self.addicted_sprites = StaticSpriteGroup((self.x, self.y))
        self.eyes = NewSprite("eyes.png", self.screen, (self.x, self.y), self.addicted_sprites)

    def set_char_s(self, new_char_s):
        orig_char_s = [self.vx, self.vy, self.ax, self.ay, self.max_vx, self.max_vy]
        for i in range(len(new_char_s)):
            if (new_char_s[i] is None):
                new_char_s[i] = orig_char_s[i]

        self.vx, self.vy, self.ax, self.ay, self.max_vx, self.max_vy = new_char_s

    def jump(self):
        if (not self.jumping):
            self.vy = -JUMP_SPEED
            self.jumping = True

    def move_check(self, blocker: pygame.sprite.Group):
        self.can_move_y = self.is_possible_to_move(0, self.vy + self.ay, blocker)
        self.can_move_x = self.is_possible_to_move(self.vx + self.ax, 0, blocker)
        if (not self.can_move_y):
            self.jumping = False
            self.vy = self.vy * -1 * 0.25

        if (not self.can_move_x):
            self.vx = self.vx * -1 * 0.25

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

        self.addicted_sprites.set_cords((self.x, self.y))
        self.addicted_sprites.update()
        self.addicted_sprites.draw(self.screen)

        super().update()


class Game:
    def __init__(self):
        pygame.init()
        size = 1280, 720
        self.screen = pygame.display.set_mode(size)
        self.clock = pygame.time.Clock()
        self.running = True

        self.start_screen()
        # self.game()

    def game(self):
        self.creating_f = create_earth
        self.players = pygame.sprite.Group()
        self.player1 = Player(fire_image_name, self.screen, (400, 300), self.players)
        self.ground = pygame.sprite.Group()

        while (self.running):
            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    self.left_game()
                if (event.type == pygame.KEYDOWN):
                    match event.key:
                        case pygame.K_1:
                            self.creating_f = create_fire
                        case pygame.K_2:
                            self.creating_f = create_earth
                        case pygame.K_3:
                            self.creating_f = create_water

                        case pygame.K_w:
                            self.player1.jump()
                        case pygame.K_d:
                            self.player1.set_char_s([None, None, GOR_ALT, None, None, None])
                        case pygame.K_a:
                            self.player1.set_char_s([None, None, -GOR_ALT, None, None, None])

                if (event.type == pygame.KEYUP):
                    match event.key:
                        case pygame.K_w:
                            pass
                        case pygame.K_d:
                            self.player1.set_char_s([0, None, 0, None, None, None])
                        case pygame.K_a:
                            self.player1.set_char_s([0, None, 0, None, None, None])
                if (event.type == pygame.MOUSEBUTTONDOWN):
                    if (self.creating_f == create_earth):
                        earth = Earth(self.screen, (event.pos[0], event.pos[1]), self.ground)
                    else:
                        self.creating_f(self.screen, event, self.player1.addicted_sprites)

            self.screen.fill((255, 255, 255))

            for player in self.players.sprites():
                player.move_check(self.ground)

            self.players.draw(self.screen)
            self.players.update()
            self.ground.draw(self.screen)
            self.ground.update()
            pygame.display.flip()
            self.clock.tick(FPS)

    def creating_level(self):
        self.creating_f = create_earth
        self.ground = pygame.sprite.Group()

        while (self.running):
            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    self.left_game()
                if (event.type == pygame.KEYDOWN):
                    match event.key:
                        case pygame.K_1:
                            self.creating_f = create_fire
                        case pygame.K_2:
                            self.creating_f = create_earth
                        case pygame.K_3:
                            self.creating_f = create_water

                if (event.type == pygame.MOUSEBUTTONDOWN):
                    f = True
                    for sprite in self.ground.sprites():
                        if (sprite.del_if_mouse_clicked(event)):
                            f = False
                    if (f):
                        if (self.creating_f == create_earth):
                            earth = Earth(self.screen, (event.pos[0], event.pos[1]), self.ground)
                        # else:
                        #     self.creating_f(self.screen, event, self.player1.addicted_sprites)

            self.screen.fill((255, 255, 255))

            self.ground.draw(self.screen)
            self.ground.update()
            pygame.display.flip()
            self.clock.tick(FPS)

            try:
                pass
            except Exception as ex:
                print(ex)

    def left_game(self):
        self.running = False
        pygame.quit()

    def start_screen(self):
        buttons = ButtonGroup(self.screen)
        create_level = Button(("Create level", (0, 0, 0), (255, 255, 255), 50),
                              (0, 0), buttons, self.creating_level)
        start_game = Button(("Start game", (0, 0, 0), (255, 255, 0), 50),
                            (0, 50), buttons, self.game)

        is_in_menu = True

        while (self.running and is_in_menu):
            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    self.left_game()
                if(event.type == pygame.MOUSEBUTTONDOWN):
                    buttons.check_event(event)

            self.screen.fill((255, 255, 255))

            buttons.draw(self.screen)
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

    def draw(self, surface):
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
