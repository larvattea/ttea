import pygame as pg

from udescjoinvilletteagames.kartea.util import KarteaPathConfig


class Target(pg.sprite.Sprite):

    def __init__(self):
        pg.sprite.Sprite.__init__(self)

        self.image = pg.image.load(
            KarteaPathConfig.game_image("vehicle//carro.png")
        )
        self.rect = pg.Rect((10, 20, 30, 30))

    def draw(self, screen):
        screen.blit(self.image, self.rect)
