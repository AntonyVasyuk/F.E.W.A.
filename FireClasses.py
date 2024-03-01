from random import randint

import pygame

from constants import FPS, fire_image_name
from main_classes import ElementSprite


class Fire(ElementSprite):
    def __init__(self, *args, **kwargs):
        super().__init__(fire_image_name, *args, **kwargs)


# class BurningFire(ParticlesSource):
#     def __init__(self, *args, **kwargs):
#         super().__init__(fire_image_name, *args, **kwargs)
#         self.left_change = 20
#         self.right_change = 50
#         self.changing_size()
#
#     def born_particle(self, args):
#         FlyingFire(self, *args)
#
#
# class FlyingFire(Particle):
#     def __init__(self, parent: BurningFire, *args, **kwargs):
#         self.parent = parent
#         self.vert_v = randint(100, 300)
#         super().__init__(fire_image_name, *args, **kwargs)
#         self.left_change = int(self.parent.rect.width * 0.6)
#         self.right_change = int(self.parent.rect.width * 0.9)
#         self.changing_size()
#
#     def update(self, *args, **kwargs):
#         d = (self.frames_to_live - self.age) / self.frames_to_live
#         self.image = pygame.transform.scale_by(self.image, d)
#
#         self.rect = self.image.get_rect()
#         self.y -= int(self.vert_v / FPS)
#         self.vert_v += randint(1, 20)
#         self.x += randint(-1, 1)
#
#         self.age += 1
#         super().update()
