import pygame
from pygame.image import load
import numpy as np


class Desafio():
    def __init__(self, fase, nivel):
        super().__init__()
        self.tilesize = 50
        self.fase = fase
        self.nivel = nivel
        self.labirinto = self.getLabirinto()
        self.corpo = self.getCorpo()
        self.clima = self.getClima()
        self.local = self.getLocal()
        self.roupa_certa = self.getRoupaCerta()
        self.roupa_errada = self.getRoupaErrada()

    def getLabirinto(self):
        return np.array([
            [4,44,0,0,0,0,0,0,0,0,0,0,0,0,3,33],
            [44,44,1,0,0,0,0,0,0,0,0,0,0,1,33,33],
            [0,0,1,0,0,0,0,1,1,0,0,0,0,1,0,0],
            [0,0,1,1,1,0,0,0,0,0,0,1,1,1,0,0],
            [0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1],
            [0,0,0,0,0,0,0,2,9,0,0,0,0,0,0,0],
        ])

    def getCorpo(self):
        return 1

    def getClima(self):
        return 1

    def getLocal(self):
        return 1

    def getRoupaCerta(self):
        return 'saia1.jpg'

    def getRoupaErrada(self):
        return 'camisa2.jpg'

    #captura onde o jogador está no labirinto
    def detectaColisao(self, x, y):
        y = y-150    
        lin = int(np.floor(x / 50))
        col = int(np.floor(y / 50))
        print(lin,col)
        if (0 <= lin <= 8) and (0 <= col <= 15):
            #retorna simbolo onde o jogador está
            return(self.labirinto[lin,col])
        else:
            #retorna -1 pois está fora do labirinto
            print('fora do labirinto')
            return -1

    
        
        