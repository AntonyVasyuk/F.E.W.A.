from constants import earth_image_name
from main_classes import ElementSprite


class Earth(ElementSprite):
    def __init__(self, *args, **kwargs):
        super().__init__(earth_image_name, *args, **kwargs)
