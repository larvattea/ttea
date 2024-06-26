import pygame
from pygame import display
import numpy as np


#se for executar de outra pasta, precisa de:
#import os
#os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Tela():
    def __init__(self, desafio):
        self.tamanho = 800, 600
        self.area_desafio = 800, 150
        self.area_jogo = 800, 450
        self.tilesize = 50
        self.superficie = display.set_mode(
            size=self.tamanho,
            display=0
        )
        display.set_caption(
            'VesTEA'
        )
        self.superficie.fill((50, 50, 255))

        #pega superficie
        self.display_surface = pygame.display.get_surface()
        
        ###############################
        #PARTE SUPERIOR
        ###############################
        # carrega fundo
        self.fundo_desafio = pygame.image.load('VesTEA/images/space.jpg').convert_alpha()
        self.fundo_desafio = pygame.transform.scale(self.fundo_desafio, self.area_desafio)
        self.display_surface.blit(self.fundo_desafio,(0,0))

         #prepara desafio
        #!!!!!!!!!!!!!!!!!
        #verifica quantas imagens devem ser mostradas pela fase e prepara posições
        if desafio.fase == 1:
            posicoes = np.array([
            (350,25)
            ])
        elif desafio.fase == 2:
            posicoes = np.array([
            (250,25),
            (450,25),
            ])    
        elif desafio.fase == 3:
            posicoes = np.array([
            (150,25),
            (350,25),
            (550,25),
            ])    
        #inicia contadora de posicao
        posicao_atual = 0
        #mostra as imagens do desafio
        if desafio.corpo == 1: 
            self.desafio_corpo = pygame.image.load(f'Assets/vestea/imgs/desafios/Corpo{desafio.corpo}.png').convert_alpha()
            self.desafio_corpo = pygame.transform.scale(self.desafio_corpo, (self.tilesize*2, self.tilesize*2))
            self.display_surface.blit(self.desafio_corpo,posicoes[posicao_atual])
            posicao_atual += 1
        if desafio.clima == 1: 
            self.desafio_clima = pygame.image.load(f'Assets/vestea/imgs/desafios/Clima{desafio.clima}.png').convert_alpha()
            self.desafio_clima = pygame.transform.scale(self.desafio_clima, (self.tilesize*2, self.tilesize*2))
            self.display_surface.blit(self.desafio_clima,posicoes[posicao_atual])
            posicao_atual += 1
        if desafio.local == 1: 
            self.desafio_local = pygame.image.load(f'Assets/vestea/imgs/desafios/Local{desafio.local}.jpg').convert_alpha()
            self.desafio_local = pygame.transform.scale(self.desafio_local, (self.tilesize*2, self.tilesize*2))
            self.display_surface.blit(self.desafio_local,posicoes[posicao_atual])

        ###############################
        #PARTE INFERIOR
        ###############################
        #carrega imagens padrão
        self.inicio_img = pygame.image.load('Assets/vestea/imgs/inicio.png').convert_alpha()
        self.inicio_img = pygame.transform.scale(self.inicio_img, (2*self.tilesize, self.tilesize))
        self.parede_img = pygame.image.load('Assets/vestea/imgs/tijolo.jpg').convert_alpha()
        self.parede_img = pygame.transform.scale(self.parede_img, (self.tilesize, self.tilesize))
        
        #carrega imagens vestimentas
        self.roupacerta_img = pygame.image.load('Assets/vestea/imgs/roupas/'+desafio.roupa_certa.nome).convert_alpha()
        self.roupacerta_img = pygame.transform.scale(self.roupacerta_img, (self.tilesize*2, self.tilesize*2))
        self.roupaerrada_img = pygame.image.load('Assets/vestea/imgs/roupas/'+desafio.roupa_errada.nome).convert_alpha()
        self.roupaerrada_img = pygame.transform.scale(self.roupaerrada_img, (self.tilesize*2, self.tilesize*2))
        mapa = desafio.labirinto
        
        #self.display_surface.blit(self.topo_img,(0,0))
        #self.display_surface.blit(self.jogo_img,(0,100))
        
        #posiciona imagens conforme mapa (-3 por causa do topo reservado para o desafio . se mudar o tamanho, vai mudar esse valor)
        for col in range (16):
            for row in range (3,12):
                imagem = ''
                if mapa[row-3,col] == 1:
                    imagem = self.parede_img
                elif mapa[row-3,col] == 2:
                    imagem = self.inicio_img
                elif mapa[row-3,col] == 3:
                    imagem = self.roupacerta_img
                elif mapa[row-3,col] == 4:
                    imagem = self.roupaerrada_img
                if imagem != '':
                    self.display_surface.blit(imagem,(col*self.tilesize,row*self.tilesize))



