import pygame

from EarthClasses import ScatteringEarth
from FireClasses import BurningFire
from constants import FPS, fire_image_name
from main_classes import StaticSpriteGroup, NewSprite


class Player(NewSprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.screen = args[1]
        self.x, self.y = args[2]
        self.particle_sprites = StaticSpriteGroup((self.x, self.y))

        self.vx, self.vy = 0, 0

    def set_speed(self, vx=None, vy=None):
        if (vx is None):
            vx = self.vx
        if (vy is None):
            vy = self.vy

        self.vx, self.vy = vx, vy

    def update(self, *args, **kwargs):
        self.x += self.vx
        self.y += self.vy
        self.particle_sprites.move(self.vx, self.vy)
        self.particle_sprites.update()
        self.particle_sprites.draw(self.screen)
        super().update()



def create_fire(screen, event, sprites):
    fire = BurningFire(screen, (event.pos[0], event.pos[1]), sprites)

def create_earth(screen, event, sprites):
    earth = ScatteringEarth(screen, (event.pos[0], event.pos[1]), sprites)

def create_water(screen, event, sprites):
    pass

def create_air(screen, event, sprites):
    pass


class Game:
    def __init__(self):
        pygame.init()
        size = 800, 600
        screen = pygame.display.set_mode(size)

        creating_f = create_fire
        players = pygame.sprite.Group()
        player1 = Player(fire_image_name, screen, (400, 300), players)
        running = True
        clock = pygame.time.Clock()
        while (running):
            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    running = False
                if (event.type == pygame.KEYDOWN):
                    match event.key:
                        case pygame.K_1:
                            creating_f = create_fire
                        case pygame.K_2:
                            creating_f = create_earth
                        case pygame.K_3:
                            creating_f = create_water
                        case pygame.K_4:
                            creating_f = create_air

                        case pygame.K_UP:
                            player1.set_speed(None, -10)
                        case pygame.K_DOWN:
                            player1.set_speed(None, 10)
                        case pygame.K_RIGHT:
                            player1.set_speed(10, None)
                        case pygame.K_LEFT:
                            player1.set_speed(-10, None)

                if (event.type == pygame.KEYUP):
                    match event.key:
                        case pygame.K_UP:
                            player1.set_speed(None, 0)
                        case pygame.K_DOWN:
                            player1.set_speed(None, 0)
                        case pygame.K_RIGHT:
                            player1.set_speed(0, None)
                        case pygame.K_LEFT:
                            player1.set_speed(0, None)
                if (event.type == pygame.MOUSEBUTTONDOWN):
                    creating_f(screen, event, player1.particle_sprites)

            screen.fill((255, 255, 255))

            players.draw(screen)
            players.update()
            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
