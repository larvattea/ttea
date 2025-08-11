import pygame as pg
from udescjoinvilleiputil.pathconfig import PathConfig


class Target(pg.sprite.Sprite): 
    
    def __init__(self): 
        pg.sprite.Sprite.__init__(self)

        self.image =  pg.image.load(PathConfig.kartea_image("car.png"))
        self.rect = pg.Rect((10,20,30,30))


    def draw(self, screen): 
        screen.blit(self.image, self.rect)
    