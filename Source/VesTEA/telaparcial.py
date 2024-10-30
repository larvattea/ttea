import pygame
from pygame import display
import numpy as np
from pygame import font
import ui
import image
from VesTEA.config import Config
from VesTEA.botao import Botao
import random

#se for executar de outra pasta, precisa de:
#import os
#os.chdir(os.path.dirname(os.path.abspath(__file__)))

class TelaParcial():
    def __init__(self, desafio):
        self.tamanho = 800, 600
        self.area_desafio = 800, 125
        self.area_jogo = 800, 475
        self.tilesize = 25
        self.superficie = display.set_mode(
            size=self.tamanho,
            display=0
        )
        display.set_caption(
            'VesTEA'
        )
        self.superficie.fill((238, 236, 225))
        
        #pega superficie
        self.display_surface = pygame.display.get_surface()
        
        ###############################
        #PARTE SUPERIOR
        ###############################
        # carrega fundo
        self.fundo_desafio = pygame.image.load('VesTEA/images/space.jpg').convert_alpha()
        self.fundo_desafio = pygame.transform.scale(self.fundo_desafio, self.area_desafio)
        self.display_surface.blit(self.fundo_desafio,(0,0))

        # carrega frases desafio 
        fonte = font.SysFont('opensans', 40)
        texto_fase = fonte.render(
            f"Fase : {desafio.fase}",
            True,
            (250, 250, 250)
        )
        self.display_surface.blit(texto_fase, (20, 25))
        texto_nivel = fonte.render(
            f"Nivel : {desafio.nivel}",
            True,
            (250, 250, 250)
        )
        self.display_surface.blit(texto_nivel, (20, 55))
        texto_desafio = fonte.render(
            f"Desafio : {desafio.jogada} de 3",
            True,
            (250, 250, 250)
        )
        self.display_surface.blit(texto_desafio, (20, 85))

        
        #prepara desafio
        #!!!!!!!!!!!!!!!!!
        #verifica quantas imagens devem ser mostradas pela fase e prepara posições
        if desafio.fase == 1:
            posicoes = np.array([
            (350,10)
            ])
        elif desafio.fase == 2:
            posicoes = np.array([
            (250,10),
            (450,10),
            ])    
        elif desafio.fase == 3:
            posicoes = np.array([
            (300,10),
            (475,10),
            (650,10),
            ])    
        #inicia contadora de posicao
        posicao_atual = 0

        ###############################
        #PARTE INFERIOR
        ###############################
        #carrega imagens padrão
        self.inicio_img = pygame.image.load('Assets/vestea/imgs/inicio.png').convert_alpha()
        self.inicio_img = pygame.transform.scale(self.inicio_img, (2*self.tilesize, 2*self.tilesize))
        self.parede_img = pygame.image.load('Assets/vestea/imgs/tijolo.jpg').convert_alpha()
        self.parede_img = pygame.transform.scale(self.parede_img, (self.tilesize, self.tilesize))
        self.paredeatingida_img = pygame.image.load('Assets/vestea/imgs/tijoloAtingido.jpg').convert_alpha()
        self.paredeatingida_img = pygame.transform.scale(self.paredeatingida_img, (self.tilesize, self.tilesize))
        
        #carrega imagens vestimentas
        self.roupacerta_img = pygame.image.load('Assets/vestea/imgs/roupas/'+desafio.roupa_certa.nome).convert_alpha()
        self.roupacerta_img = pygame.transform.scale(self.roupacerta_img, (self.tilesize*4, self.tilesize*4))
        self.roupaerrada_img = pygame.image.load('Assets/vestea/imgs/roupas/'+desafio.roupa_errada.nome).convert_alpha()
        self.roupaerrada_img = pygame.transform.scale(self.roupaerrada_img, (self.tilesize*4, self.tilesize*4))
        if desafio.nivel >= 6:
            self.roupacoringa_img = pygame.image.load('Assets/vestea/imgs/roupas/'+desafio.roupa_coringa.nome).convert_alpha()
            self.roupacoringa_img = pygame.transform.scale(self.roupacoringa_img, (self.tilesize*4, self.tilesize*4))
        mapa = desafio.labirinto
        #print(desafio.labirinto)
        #self.display_surface.blit(self.topo_img,(0,0))
        #self.display_surface.blit(self.jogo_img,(0,100))
        
        #posiciona imagens conforme mapa (-3 por causa do topo reservado para o desafio . se mudar o tamanho, vai mudar esse valor)
        #for col in range (16):
        for col in range (32):
            #for row in range (3,12):
            for row in range (5,24):
                imagem = ''
                if mapa[row-5,col] == 2 or mapa[row-5,col] == '2':# é o inicio do ponto inicial
                    imagem = self.inicio_img
                if imagem != '':
                    self.display_surface.blit(imagem,(col*self.tilesize,row*self.tilesize))    



