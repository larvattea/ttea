import pygame
from pygame.image import load
import numpy as np


class Desafio():
    def __init__(self, fase, nivel):
        super().__init__()

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
            [4,9,0,0,0,0,0,0,0,0,0,0,0,0,3,9],
            [9,9,1,0,0,0,0,0,0,0,0,0,0,1,9,9],
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
        