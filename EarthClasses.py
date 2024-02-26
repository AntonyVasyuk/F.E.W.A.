from random import randint

import pygame

from constants import FPS, earth_image_name
from main_classes import Element, load_image


class Earth(Element):
    def __init__(self, screen, pos, group, size=None):
        super().__init__(earth_image_name, screen, pos, group)
        if (size is not None):
            self.change_size(size)

    def change_size(self, size):
        w_new, h_new = size, size
        self.image = load_image(earth_image_name, -1)
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
