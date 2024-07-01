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

class Jogo():
    def __init__(self, superficie):
        self.jogando = True
        self.fase = 0
        self.nivel = 0
        self.jogada = 0
        self.estado = 1
        #captura do jogador
        self.cap = Camera()
        #self.cap.load_camera()
        self.jogador = Jogador()
        self.superficie = superficie


    def carregaDados(self):
        self.fase = 1
        self.nivel = 1
        self.jogada = 1
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

    def verificaResultado(self):
        if self.posicaoJogador == 3 or self.posicaoJogador == 33: 
            print('acerto mizeravi')
        elif self.posicaoJogador == 4 or self.posicaoJogador == 44:
            print('errrrou')

    def verificaFimNivel(self):
        return True

    def carregaTelaPausa(self):
        self.superficie.fill((50, 50, 255))

        #self.superficie.blit(self.fundo_inicio, (0, 0))
        
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

            elif self.estado == 6:    
                #carrega carrega pós-nível (exibir resultado e decidir próximo nível)
                print("Carregando fim de nível...")
                self.verificaFimNivel()

        elif self.jogando == False:    
            #pausa
            print("Pausa...")
            self.carregaTelaPausa()
        
            
        
            
        