from constants import water_image_name
from main_classes import ElementSprite


class Water(ElementSprite):
    def __init__(self, *args, **kwargs):
        super().__init__(water_image_name, *args, **kwargs)
