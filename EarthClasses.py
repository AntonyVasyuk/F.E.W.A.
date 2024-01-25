from random import randint

import pygame

from constants import FPS, earth_image_name
from main_classes import Particle, ParticlesSource


class ScatteringEarth(ParticlesSource):
    def __init__(self, *args, **kwargs):
        super().__init__(earth_image_name, *args, **kwargs)
        self.particles_borning_v = 40

    def born_particle(self, args):
        # args[0] = (20, 20)
        FallingEarth(*args)


class FallingEarth(Particle):
    def __init__(self, max_size=None, *args, **kwargs):
        # self.max_size = max_size
        self.frames_to_live = randint(800, 1000)
        self.vert_v = -(self.frames_to_live // 10)
        super().__init__(max_size, earth_image_name, *args, **kwargs)

    def update(self, *args, **kwargs):
        d = (self.frames_to_live - self.age) / self.frames_to_live

        self.image = pygame.transform.scale_by(self.image, d)

        self.rect = self.image.get_rect()
        self.y -= int(self.vert_v / FPS)
        # self.x += randint(-1, 1)

        self.age += 1
        super().update()
