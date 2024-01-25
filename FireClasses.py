from random import randint

import pygame

from constants import FPS, fire_image_name
from main_classes import Particle, ParticlesSource


class BurningFire(ParticlesSource):
    def __init__(self, *args, **kwargs):
        super().__init__(fire_image_name, *args, **kwargs)

    def born_particle(self, args):
        FlyingFire(*args)


class FlyingFire(Particle):
    def __init__(self, max_size=None, *args, **kwargs):
        self.vert_v = randint(100, 300)
        super().__init__(max_size, fire_image_name, *args, **kwargs)

    def update(self, *args, **kwargs):
        d = (self.frames_to_live - self.age) / self.frames_to_live
        self.image = pygame.transform.smoothscale_by(self.image, d)

        self.rect = self.image.get_rect()
        self.y -= int(self.vert_v / FPS)
        self.x += randint(-1, 1)

        self.age += 1
        super().update()
