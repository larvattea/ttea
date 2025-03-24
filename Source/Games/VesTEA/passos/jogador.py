import pygame 

from pygame.image import load 

from pygame.sprite import Sprite 

from tiro import Tiro   

class Jogador(Sprite): 

    def __init__(self, jogo): 

        super().__init__() 

  

        self.jogo = jogo 

        self.image = load('images/aviao.png') 

        self.image = pygame.transform.scale(self.image, (100, 100)) 

        self.rect = self.image.get_rect() 
        self.velocidade = 2         
        self.tiros = jogo.grupo_tiros 
    def update(self): 

        keys = pygame.key.get_pressed() 

  

        if keys[pygame.K_LEFT] and self.rect.x>0: 

            self.rect.x -= self.velocidade 

        if keys[pygame.K_RIGHT] and self.rect.x<400: 

            self.rect.x += self.velocidade 

        if keys[pygame.K_UP] and self.rect.y>0: 

            self.rect.y -= self.velocidade 

        if keys[pygame.K_DOWN] and self.rect.y<self.jogo.tamanho[1]-self.rect.height: 

            self.rect.y += self.velocidade 

    def atirar(self): 

        if len(self.tiros) < 15: 

            self.tiros.add( 

                Tiro(*self.rect.center, self.rect.x+self.rect.width, self.jogo.tamanho[0]) 

            )             