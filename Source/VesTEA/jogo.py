import pygame
import numpy as np
from VesTEA.desafio import Desafio
from VesTEA.tela import Tela
from VesTEA.jogador import Jogador
from camera import Camera
from pygame import event
from pygame.locals import KEYUP, K_SPACE
from pygame import font
from VesTEA import botao
from pygame import display

class Jogo():
    def __init__(self, superficie):
        self.jogando = True
        self.fase = 1
        self.nivel = 1
        self.jogada = 1
        self.estado = 1
        #captura do jogador
        self.cap = Camera()
        #self.cap.load_camera()
        self.jogador = Jogador()
        self.superficie = superficie


    def carregaDados(self):
        self.desafio = Desafio(self.fase, self.nivel)
        self.estado += 1 
    
    def carregaTelaJogo(self):
        self.estado += 1

    def carregaPartida(self):
        self.estado += 1

    def gerenciaJogo(self):
        self.tela = Tela(self.desafio)
        #inserindo captura do jogador
        self.cap.load_camera()
        self.cap.frame = self.jogador.scan_feets(self.cap.frame)
        x, y = self.jogador.get_feet_center()
        #print("Jogador em: ",x,"-",y)
        pygame.draw.circle(self.superficie, (255,255,0), [x,y-20], 15)
        self.posicaoJogador = self.desafio.detectaColisao(x,y)
        if self.posicaoJogador == 3 or self.posicaoJogador == 33 or self.posicaoJogador == 4 or self.posicaoJogador == 44:
            self.estado += 1
        if self.posicaoJogador == 1:
            self.acoesColisao(x,y)

    def verificaResultado(self):
        pygame.draw.rect(self.tela.roupacerta_img, (0,255,0), (0, 0, 100, 100),10)
        certo_rect = self.tela.roupacerta_img.get_rect(topleft = self.tela.roupacerta_pos)
        self.superficie.blit(self.tela.roupacerta_img, certo_rect)
        pygame.draw.rect(self.tela.roupaerrada_img, (255,0,0), (0, 0, 100, 100),10)
        erro_rect = self.tela.roupaerrada_img.get_rect(topleft = self.tela.roupaerrada_pos)
        self.superficie.blit(self.tela.roupaerrada_img, erro_rect)
        display.update()
        pygame.time.delay(5000)   
        if self.posicaoJogador == 3 or self.posicaoJogador == 33: 
            self.acoesAcerto()
        elif self.posicaoJogador == 4 or self.posicaoJogador == 44:
            self.acoesErro()
        print('passou atraso do resultado') 
        self.estado = 1    

    def acoesAcerto(self):
        print('acerto mizeravi')
        if self.fase <3:
            self.fase += 1
    
    def acoesErro(self):
        print('Errou')
        if self.fase >1:
            self.fase -= 1

    def acoesColisao(self, x, y):
        print('Bateu na parede')
        #pintar o quadrado
        self.desafio.labirinto = self.desafio.mudaParedeAtingida(x,y,self.desafio.labirinto)
            #mudar pra outro valor no mapa, pq aí não colide de novo no mesmo local
        #aguardar sair
        self.posicaoJogador
        

    def carregaTelaPausa(self):
        self.superficie.fill((50, 50, 255))

        titulo = font.SysFont('comicsans', 80).render(
            'Pausa',
            True,
            (255, 165, 0)
        )
        self.superficie.blit(titulo, (190, 180))
        
        self.imagem_inicio = pygame.image.load('VesTEA/images/button_inicio.png').convert_alpha()
        self.botao_inicio = botao.Botao(350, 450, self.imagem_inicio, 0.8)
        if self.botao_inicio.criar(self.superficie):
            #print('START')
            self.estado = 2 #para reiniciar o jogo no mesmo desafio, mas do começo
            self.jogando = True
        

    def update(self):
        if self.jogando == True:
            
            if self.estado == 99:
                print('teste')
                
                
            if self.estado == 1:
                #carrega dados
                print("Carregando dados...")
                self.carregaDados()

            elif self.estado == 2:    
                #carrega tela
                print("Carregando tela...")
                self.carregaTelaJogo()

            elif self.estado == 3:    
                #carrega inicio da partida
                print("Carregando partida...")
                self.carregaPartida()

            elif self.estado == 4:    
                #carrega jogada (movimento, colisão...)
                #print("Jogando...")
                self.gerenciaJogo()
            
            elif self.estado == 5:    
                #carrega pós jogada (ações de acerto/erro e próx jogada ou fim de nível)
                print("Carregando resultado...")
                self.verificaResultado()

        elif self.jogando == False:    
            #pausa
            print("Pausa...")
            self.carregaTelaPausa()
        
            
        
            
        