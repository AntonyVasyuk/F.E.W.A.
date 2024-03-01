from random import randint

import pygame

from constants import SEP


def load_image(name, colorkey=None):
    fullname = f"data{SEP}{name}"
    image = pygame.image.load(fullname)
    image = image.convert()
    if (colorkey is not None):
        if (colorkey == -1):
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


LEFT_CHANGE = 50  # in %
RIGHT_CHANGE = 75
d = 1


class NewSprite(pygame.sprite.Sprite):
    def __init__(self, image_name, screen, cords, group=None):
        super().__init__(group)
        self.screen = screen

        self.image_name = image_name
        self.image_default = load_image(image_name, -1)
        self.image = self.image_default.copy()

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = cords


class ElementSprite(pygame.sprite.Sprite):
    def __init__(self, image_name, screen, cords, group=None, size=None):
        super().__init__(group)
        self.screen = screen
        if (size is not None):
            self.size = size
        else:
            self.size = 100

        self.image_name = image_name
        self.image_default = load_image(image_name, -1)
        self.image = self.image_default.copy()
        self.change_size(self.size)

        self.rect = self.image.get_rect()
        self.circle_radius = self.rect.height // 2
        self.x, self.y = cords[0], cords[1]

    def update(self, *args, **kwargs):
        self.rect.x, self.rect.y = self.x - self.rect.width // 2, self.y - self.rect.height // 2

    def change_size(self, size):
        w_new, h_new = size, size
        self.image = load_image(self.image_name, -1)
        self.image = pygame.transform.scale(self.image, (w_new, h_new))
        self.rect = self.image.get_rect()
        self.circle_radius = self.rect.height // 2
        super().update(self)

    def del_if_mouse_clicked(self, event: pygame.event.Event):
        if (event.type == pygame.MOUSEBUTTONDOWN):
            if (self.rect.collidepoint(event.pos)):
                self.remove(self.groups()[0])
                return True
            return False


# class Particle(ElementSprite):
#     def __init__(self, *args, **kwargs):
#         self.frames_to_live = randint(200, 400)
#         self.age = 0
#         super().__init__(*args, **kwargs)
#
#     def update(self, *args, **kwargs):
#         if (self.age == self.frames_to_live):
#             self.remove(self.groups()[0])
#
#         super().update()
#
#
# class ParticlesSource(ElementSprite):
#     def __init__(self, *args, **kwargs):
#         self.particles = pygame.sprite.Group()
#         self.particles_borning_v = 35  # it's 1 born for {self.particles_borning_v} frames
#         self.count = self.particles_borning_v
#         super().__init__(*args, **kwargs)
#         # print(self.image.get_size())
#
#     def update(self, *args, **kwargs):
#         super().update()
#         if (self.count == self.particles_borning_v):
#             self.born_particle([self.screen, (self.x, self.y), self.particles])
#             self.count = 0
#             self.particles_borning_v = randint(20, 40)
#         self.particles.draw(self.screen)
#         self.particles.update()
#         self.count += 1
#
#
# class StaticSpriteGroup(pygame.sprite.Group):
#     def __init__(self, cords):
#         super().__init__()
#         self.x, self.y = cords
#
#     def set_cords(self, cords):
#         dx, dy = cords[0] - self.x, cords[1] - self.y
#         self.x, self.y = cords
#         for sprite in self.sprites():
#             sprite.x += dx
#             sprite.y += dy
#
#     # def update(self, *args, **kwargs):
#     #     for sprite in self.sprites():
#     #         sprite.x = self.x
#     #         sprite.y = self.y
#     #     super().update()
