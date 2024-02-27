from random import randint

import pygame

from constants import FPS, earth_image_name
from main_classes import Element, load_image


class Earth(Element):
    def __init__(self, *args, **kwargs):
        super().__init__(earth_image_name, *args, **kwargs)

    def del_if_mouse_clicked(self, event: pygame.event.Event):
        if (event.type == pygame.MOUSEBUTTONDOWN):
            if (self.rect.collidepoint(event.pos)):
                self.remove(self.groups()[0])
                return True
            return False
