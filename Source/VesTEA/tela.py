import pygame
from pygame import display
import numpy as np
from pygame import font
import ui
import image
from VesTEA.config import Config
from VesTEA.botao import Botao
from VesTEA import arquivo as arq
import random
import settings

#se for executar de outra pasta, precisa de:
#import os
#os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Tela():
    def __init__(self, desafio, status):
        #status de tela: 
        # 1 = só hud e posição inicial
        # 2 = 1 + desafio
        # 3 = 2 + roupas e labirinto
        # 4 = 3 - labirinto
        # 5 = 4 - roupa errada
        self.status = status
        self.desafio = desafio
        self.tamanho = 800, 600
        self.area_desafio = 800, 125
        self.area_jogo = 800, 475
        self.tilesize = 25
        self.superficie = settings.obter_superficie(self.tamanho)
        display.set_caption(
            'VesTEA'
        )
        self.superficie.fill(arq.get_V_FUNDO())
        
        #pega superficie
        self.display_surface = pygame.display.get_surface()
        
        ###############################
        #PARTE SUPERIOR
        ###############################
        # carrega fundo
        self.fundo_desafio = image.carregar_alpha('VesTEA/images/space.jpg', self.area_desafio)
        self.display_surface.blit(self.fundo_desafio,(0,0))

        #se hud estiver habilitado
        if arq.get_V_HUD():
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
        self.mostraDesafio()

        ###############################
        #PARTE INFERIOR
        ###############################
        #carrega imagens padrão
        self.inicio_img = image.carregar_alpha('Assets/vestea/imgs/inicio.png', (2*self.tilesize, 2*self.tilesize))
        self.parede_img = image.carregar_alpha(f'Assets/vestea/imgs/tijolo{arq.get_V_TIJOLO()}.jpg', (self.tilesize, self.tilesize))
        self.paredeatingida_img = image.carregar_alpha('Assets/vestea/imgs/tijoloAtingido.jpg', (self.tilesize, self.tilesize))
        
        #carrega imagens vestimentas
        self.roupacerta_img = image.carregar_alpha('Assets/vestea/imgs/roupas/'+desafio.roupa_certa.nome, (self.tilesize*4, self.tilesize*4), copia=True)
        self.roupaerrada_img = image.carregar_alpha('Assets/vestea/imgs/roupas/'+desafio.roupa_errada.nome, (self.tilesize*4, self.tilesize*4), copia=True)
        if desafio.nivel >= 6:
            self.roupacoringa_img = image.carregar_alpha('Assets/vestea/imgs/roupas/'+desafio.roupa_coringa.nome, (self.tilesize*4, self.tilesize*4), copia=True)
        mapa = desafio.labirinto
        #print(desafio.labirinto)
        #self.display_surface.blit(self.topo_img,(0,0))
        #self.display_surface.blit(self.jogo_img,(0,100))
        
        #posiciona imagens conforme mapa (-5 por causa do topo reservado para o desafio . se mudar o tamanho, vai mudar esse valor)
        #for col in range (16):
        for col in range (32):
            #for row in range (3,12):
            for row in range (5,24):
                imagem = ''
                if (mapa[row-5,col] == 2 or mapa[row-5,col] == '2') and self.status != 4 and self.status != 5:# é o inicio do ponto inicial
                    imagem = self.inicio_img
                elif self.status >=3:

                    if (mapa[row-5,col] == 1 or mapa[row-5,col] == '1') and self.status == 3:# é a parede
                        imagem = self.parede_img
                    elif (mapa[row-5,col] == 11 or mapa[row-5,col] == '11') and self.status == 3:# é a parede já atingida
                        imagem = self.paredeatingida_img
                    
                    elif mapa[row-5,col] == 3 or mapa[row-5,col] == '3':# é o inicio da roupa certa
                        imagem = self.roupacerta_img
                        self.roupacerta_pos = (col*self.tilesize,row*self.tilesize)
                    elif (mapa[row-5,col] == 4 or mapa[row-5,col] == '4') and self.status < 5:# é o inicio da roupa errada
                        imagem = self.roupaerrada_img
                        self.roupaerrada_pos = (col*self.tilesize,row*self.tilesize)
                    elif (mapa[row-5,col] == 5  or mapa[row-5,col] == '5') and (desafio.nivel >= 11 or (desafio.nivel >= 6 and self.status<5)):# é o inicio da roupa coringa
                        imagem = self.roupacoringa_img
                        self.roupacoringa_pos = (col*self.tilesize,row*self.tilesize)
                if imagem != '':
                    self.display_surface.blit(imagem,(col*self.tilesize,row*self.tilesize))    



    def mostraDesafio(self):
        #verifica quantas imagens devem ser mostradas pela fase e prepara posições
        posicoes = np.array([
        (425,10),
        (550,10),
        (675,10),
        ])    
        #inicia contadora de posicao
        posicao_atual = 0

        if self.status >= 2:
            #mostra as imagens do desafio
            if self.desafio.corpo >0: 
                self.desafio_corpo = image.carregar_alpha(f'Assets/vestea/imgs/desafios/Corpo{self.desafio.corpo}.png', (self.tilesize*4, self.tilesize*4))
                self.display_surface.blit(self.desafio_corpo,posicoes[posicao_atual])
                posicao_atual += 1
            if self.desafio.clima >0: 
                if self.desafio.roupa_certa.clima == 3:
                    numClima = random.randint(1,2)
                else:
                    numClima = self.desafio.clima
                self.desafio_clima = image.carregar_alpha(f'Assets/vestea/imgs/desafios/Clima{numClima}.png', (self.tilesize*4, self.tilesize*4))
                self.display_surface.blit(self.desafio_clima,posicoes[posicao_atual])
                posicao_atual += 1
            if self.desafio.local >0: 
                self.desafio_local = image.carregar_alpha(f'Assets/vestea/imgs/desafios/Local{self.desafio.local}.jpg', (self.tilesize*4, self.tilesize*4))
                self.display_surface.blit(self.desafio_local,posicoes[posicao_atual])
