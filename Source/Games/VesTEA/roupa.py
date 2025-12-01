import pygame
from pygame.image import load
from pygame.sprite import Sprite


class Roupa:
    def __init__(self, roupa, posicao):
        self.nome = roupa[0]
        self.corpo = roupa[1]
        self.clima = roupa[2]
        self.local = self.getLocais(roupa)
        self.posicao = posicao  # posicao dela no roupas.csv

    def getLocais(self, roupa):
        locais = roupa.copy()
        locais.pop(0)  # remove nome
        locais.pop(0)  # remove corpo
        locais.pop(0)  # remove clima
        return locais  # retorna só locais
