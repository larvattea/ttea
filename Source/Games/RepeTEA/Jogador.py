import pygame 
from geometry import Circle


class Player(Circle):
    def __init__(self, color, radius, pos): 
        super().__init__(color, radius, pos)
        self.width = 0

    def move(self, key): 

        if key == pygame.K_UP:
            self.y-=1
        if key == pygame.K_DOWN:
            self.y+=1
        if key == pygame.K_RIGHT:
            self.x += 1
        if key == pygame.K_LEFT:
            self.x -= 1        
        



    