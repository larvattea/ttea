import pygame
from pygame.image import load
from pygame.sprite import Sprite


class Tiro(Sprite):
    def __init__(self, x, y, player_width, screen_width):
        super().__init__()

        self.screen_width = screen_width
        self.image = load("VesTEA/images/tiro.png")
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect(center=(player_width, y))

    def update(self):
        self.rect.x += 1

        if self.rect.x > self.screen_width:
            self.kill()
