import pygame
import numpy as np
from VesTEA.desafiotutorial import DesafioTutorial
from VesTEA.telatutorial import TelaTutorial
from VesTEA.jogador import Jogador
from camera import Camera
from pygame import event
from pygame.locals import KEYUP, K_SPACE
from pygame import font
from pygame import display
from VesTEA.config import Config
import ui
import image
from VesTEA.botao import Botao
from VesTEA import arquivo as arq
import datetime

class Tutorial():
    def __init__(self, superficie):
        self.jogando = True
        self.nivel = 1
        #mensuram nível
        self.colisoes = 0
        #controlam ajuda
        self.ultimaPosicao = [-9999,-9999]
        self.tempoSemMovimento = 0
        self.ajuda = False
        #para o fluxo do jogo
        self.estado = 1
        #captura do jogador
        self.cap = Camera()
        self.jogador = Jogador()
        self.superficie = superficie
        #total de um nivel
        self.totalAcertos = 0
        self.totalColisoes = 0
        self.totalTempo = 0
        self.totalAjudas = 0
        self.trofeu = 2
        self.emoji = ""
        self.erro = pygame.image.load(f'Assets/vestea/imgs/erro.png').convert_alpha()
        self.erro = pygame.transform.scale(self.erro, (100, 100))


    def carregaDados(self):
        #mensuram nível
        Config.som_inicio.play()
        self.totalTempo = datetime.datetime.now()
        self.tempoSemMovimento = datetime.datetime.now()    
        self.colisoes = 0
        self.ajuda = False
        self.desafioTutorial = DesafioTutorial(self.nivel)
        self.estado += 1
        self.ultimaPosicao = [-9999,-9999]
    
    def carregaTelaTutorialJogo(self):
        self.telaTutorial = TelaTutorial(self.desafioTutorial, 1)
        #inserindo captura do jogador
        self.cap.load_camera()
        self.cap.frame = self.jogador.scan_feets(self.cap.frame)
        x,y = self.jogador.get_feet_center()
        #print("Jogador em: ",x," - ",y)
        pygame.draw.circle(self.superficie, (255,255,0), [x,y-90],15)
        self.posicaoJogador = self.desafioTutorial.detectaColisao(x,y)
        #print("Jogador em: ",self.posicaoJogador)
        print(self.posicaoJogador == '2' or self.posicaoJogador == '22')
        if self.posicaoJogador == '2' or self.posicaoJogador == '22':
            #self.posicaoJogador = '99'
            #print("Jogador em: ",self.posicaoJogador)
            #mostrar só desafioTutorial     
            self.telaTutorial = TelaTutorial(self.desafioTutorial, 2)
            display.update()
            self.tempoSemMovimento = datetime.datetime.now() 
            #print(f"Tempo parado 1:{(datetime.datetime.now() - self.tempoSemMovimento).seconds} segundos")
            pygame.time.delay(3000)   
            #mostrar labirinto e roupas
            #print(f"Tempo parado 2:{(datetime.datetime.now() - self.tempoSemMovimento).seconds} segundos")
            self.telaTutorial = TelaTutorial(self.desafioTutorial, 3)
            display.update()
            pygame.time.delay(2000)
            self.cap.load_camera()
            self.estado += 1

    def carregaPartida(self):
        #self.posicaoJogador = '99'
        self.telaTutorial = TelaTutorial(self.desafioTutorial, 3)
        #print("Jogador 2 em: ",self.posicaoJogador)
        self.cap.load_camera()
        self.cap.frame = self.jogador.scan_feets(self.cap.frame)
        x,y = self.jogador.get_feet_center()
        #print("Jogador em: ",x," - ",y)
        pygame.draw.circle(self.superficie, (255,255,0), [x,y-90],15)
        self.posicaoJogador = self.desafioTutorial.detectaColisao(x,y)
        #print("Jogador 2.5 em: ",self.posicaoJogador)
        display.update()
        #se o jogador ainda estiver na posição inicial, começa a partida
        if self.posicaoJogador == '2' or self.posicaoJogador == '22': 
            #print("Jogador 3 em: ",self.posicaoJogador)
            #print(f"Tempo parado 3:{(datetime.datetime.now() - self.tempoSemMovimento).seconds} segundos")
            Config.som_vez_do_jogador_1.play()
            pygame.time.delay(500)   
            Config.som_vez_do_jogador_2.play()
            self.jogador = Jogador()
            self.estado += 1
        
        
    def gerenciaJogo(self):
        self.telaTutorial = TelaTutorial(self.desafioTutorial, 3)
        #inserindo captura do jogador
        self.cap.load_camera()
        self.cap.frame = self.jogador.scan_feets(self.cap.frame)
        x, y = self.jogador.get_feet_center()
        #verifica se precisa de ajuda
        #print(f"Tempo parado:{(datetime.datetime.now() - self.tempoSemMovimento).seconds} segundos")
        #se ainda não atualizou ultima posição ou se jogador se moveu mais que 25px para qualquer direção, atualiza última posição
        if (self.ultimaPosicao == [-9999,-9999] or (x > self.ultimaPosicao[0] + 25 or x < self.ultimaPosicao[0] - 25 or y > self.ultimaPosicao[1] + 25 or y < self.ultimaPosicao[1] - 25)):
            self.ultimaPosicao = [x,y] 
            self.tempoSemMovimento = datetime.datetime.now()            
        #senão, se passou mais do que 5 segundos e ainda não teve ajuda, dá ajuda
        elif ((datetime.datetime.now() - self.tempoSemMovimento).seconds > 5 and (datetime.datetime.now() - self.tempoSemMovimento).seconds < 10):
            #se ainda está false, toca som e muda ajuda pra true (pra tocar som uma vez apenas)
            if self.ajuda == False:
                Config.som_ajuda.play()
                self.ajuda = True
                self.totalAjudas += 1
            #destaca imagem roupa certa
            pygame.draw.rect(self.telaTutorial.roupacerta_img, (0,255,0), (0, 0, 100, 100),10)
            certo_rect = self.telaTutorial.roupacerta_img.get_rect(topleft = self.telaTutorial.roupacerta_pos)
            self.superficie.blit(self.telaTutorial.roupacerta_img, certo_rect)
            
        #print("Jogador em: ",x,"-",y)
        pygame.draw.circle(self.superficie, (255,255,0), [x,y-90], 15)
        self.posicaoJogador = self.desafioTutorial.detectaColisao(x,y)
        if self.posicaoJogador == '3' or self.posicaoJogador == '33' or self.posicaoJogador == '4' or self.posicaoJogador == '44':
            self.estado += 1
        if self.posicaoJogador == '1':
            self.acoesColisao(x,y)

    def verificaResultado(self):
        #some o labirinto
        self.telaTutorial = TelaTutorial(self.desafioTutorial, 4)
        #desenha retangulo na roupa certa
        pygame.draw.rect(self.telaTutorial.roupacerta_img, (0,255,0), (0, 0, 100, 100),10)
        certo_rect = self.telaTutorial.roupacerta_img.get_rect(topleft = self.telaTutorial.roupacerta_pos)
        self.superficie.blit(self.telaTutorial.roupacerta_img, certo_rect)
        #desenha retangulo na roupa errada
        if self.nivel == 3:
            pygame.draw.rect(self.telaTutorial.roupaerrada_img, (255,0,0), (0, 0, 100, 100),10)
            erro_rect = self.telaTutorial.roupaerrada_img.get_rect(topleft = self.telaTutorial.roupaerrada_pos)
            self.superficie.blit(self.telaTutorial.roupaerrada_img, erro_rect)
        #se acertou ou errou...    
        if self.posicaoJogador == '3' or self.posicaoJogador == '33':
            self.emoji = pygame.image.load(f'Assets/vestea/imgs/feliz.webp').convert_alpha()
            self.emoji = pygame.transform.scale(self.emoji, (self.telaTutorial.tilesize*4, self.telaTutorial.tilesize*4)) 
            Config.som_acerto.play()
            self.totalAcertos += 1
        elif self.posicaoJogador == '4' or self.posicaoJogador == '44':
            self.emoji = pygame.image.load(f'Assets/vestea/imgs/triste.webp').convert_alpha()
            self.emoji = pygame.transform.scale(self.emoji, (self.telaTutorial.tilesize*4, self.telaTutorial.tilesize*4))
            self.superficie.blit(self.erro,self.telaTutorial.roupaerrada_pos) 
            Config.som_erro.play()
        #display.update()
        display.update()
        pygame.time.delay(2500)
        self.estado += 1

    def exibeRoupasCertas(self):
        #some roupa errada
        self.telaTutorial = TelaTutorial(self.desafioTutorial, 5)   
        #desenha emoji na tela
        self.superficie.blit(self.emoji,(275,10)) 
        #desenha retangulo na roupa certa
        pygame.draw.rect(self.telaTutorial.roupacerta_img, (0,255,0), (0, 0, 100, 100),10)
        certo_rect = self.telaTutorial.roupacerta_img.get_rect(topleft = self.telaTutorial.roupacerta_pos)
        self.superficie.blit(self.telaTutorial.roupacerta_img, certo_rect)
        display.update()
        pygame.time.delay(3000)
        self.cap.load_camera()
        self.estado += 1

    def finalizaJogada(self):
        #some roupa errada
        self.telaTutorial = TelaTutorial(self.desafioTutorial, 6)   
        #desenha emoji na tela
        self.superficie.blit(self.emoji,(275,10)) 
        #desenha retangulo na roupa certa
        pygame.draw.rect(self.telaTutorial.roupacerta_img, (0,255,0), (0, 0, 100, 100),10)
        certo_rect = self.telaTutorial.roupacerta_img.get_rect(topleft = self.telaTutorial.roupacerta_pos)
        self.superficie.blit(self.telaTutorial.roupacerta_img, certo_rect)
        #se for terceira jogada, exibe telaTutorial de resultado
        if self.totalAcertos == 3 :
            Config.som_trofeu.play()
            self.totalTempo = datetime.datetime.now() - self.totalTempo
            self.posicaoJogador = 0
            self.jogando = False
        #senão, se jogador não estiver no ponto inicial, verifica sua posição    
        elif self.posicaoJogador != '2' and self.posicaoJogador != '22':
            #inserindo captura do jogador
            self.cap.load_camera()
            self.cap.frame = self.jogador.scan_feets(self.cap.frame)
            x,y = self.jogador.get_feet_center()
            #print("Jogador em: ",x," - ",y)
            pygame.draw.circle(self.superficie, (255,255,0), [x,y-90],15)
            self.posicaoJogador = self.desafioTutorial.detectaColisao(x,y)
        #se jogador voltar pro ponto inicial
        else:
            #se for nivel 1 ou 2, troca pra seguinte
            if self.nivel <3:
                self.nivel += 1
            self.posicaoJogador = '0'
            pygame.time.delay(1000)
            self.estado = 1      
        display.update()
        
    def acoesColisao(self, x, y):
        Config.som_erro.play()
        print('Bateu na parede')
        #pintar o quadrado
        self.desafioTutorial.labirinto = self.desafioTutorial.mudaParedeAtingida(x,y,self.desafioTutorial.labirinto)
        #se ainda não tem 10 colisoes, soma mais uma     
        if self.colisoes < 10:    
            self.colisoes += 1
            self.totalColisoes += 1
        

    def carregaTelaTutorialPausa(self):
        self.superficie.fill((50, 50, 255))

        titulo = font.SysFont('comicsans', 80).render(
            'Pausa',
            True,
            (255, 165, 0)
        )
        self.superficie.blit(titulo, (190, 180))
        
        self.imagem_inicio = pygame.image.load('VesTEA/images/button_jogar.png').convert_alpha()
        self.botao_inicio = Botao(350, 450, self.imagem_inicio, 1)
        if self.botao_inicio.criar(self.superficie):
            #print('START')
            self.tempoSemMovimento = 0    
            self.colisoes = 0
            self.ajuda = False
            self.ultimaPosicao = [-9999,-9999]
            self.estado = 2 #para reiniciar o jogo no mesmo desafioTutorial, mas do começo
            self.jogando = True
        

    def carregaTelaTutorialFeedback(self):
        self.superficie.fill((238, 236, 225))
        trofeu = image.load(f"VesTEA/images/trofeu3.png")
        image.draw(self.superficie, trofeu, (0, 0))        
        ui.draw_text(self.superficie, "Feedback", (450, 100), (38, 61, 39), font=pygame.font.Font(None, 25),
                         shadow=False)
        ui.draw_text(self.superficie, "Quantidade", (650, 100), (38, 61, 39), font=pygame.font.Font(None, 25),
                         shadow=False)

        ui.draw_text(self.superficie, "Tempo", (450, 130), (38, 61, 39), font=pygame.font.Font(None, 25),
                         shadow=False)
        ui.draw_text(self.superficie, str(self.totalTempo).split(".")[0], (650, 130), (38, 61, 39), font=pygame.font.Font(None, 25),
                         shadow=False)

        ui.draw_text(self.superficie, "Roupas certas", (450, 170), (38, 61, 39), font=pygame.font.Font(None, 25),
                         shadow=False)
        ui.draw_text(self.superficie, f"{self.totalAcertos} de 3", (650, 170), (38, 61, 39), font=pygame.font.Font(None, 25),
                         shadow=False)

        ui.draw_text(self.superficie, "Ajudas", (450, 210), (38, 61, 39), font=pygame.font.Font(None, 25),
                         shadow=False)
        ui.draw_text(self.superficie, f"{self.totalAjudas}", (650, 210), (38, 61, 39), font=pygame.font.Font(None, 25),
                         shadow=False)

        ui.draw_text(self.superficie, "Paredes Colididas", (450, 250), (38, 61, 39), font=pygame.font.Font(None, 25),
                         shadow=False)
        ui.draw_text(self.superficie, str(self.totalColisoes), (650, 250), (38, 61, 39), font=pygame.font.Font(None, 25),
                         shadow=False)

        self.imagem_inicio = pygame.image.load('VesTEA/images/button_jogar.png').convert_alpha()
        self.botao_inicio = Botao(350, 450, self.imagem_inicio, 1)
        if self.botao_inicio.criar(self.superficie):
            self.posicaoJogador = '0'
            self.cap.close_camera()
            self.estado = 99 #para voltar ao menu
            self.jogando = True             
            
    def update(self):
        if self.jogando == True:
            
            if self.estado == 99:
                print('volta pro menu')
                
                
            if self.estado == 1:
                #carrega dados
                print("Carregando dados...")
                self.carregaDados()

            elif self.estado == 2:    
                #carrega telaTutorial
                #print("Carregando telaTutorial...")
                self.carregaTelaTutorialJogo()

            elif self.estado == 3:    
                #carrega inicio da partida
                print("Carregando partida...")
                self.carregaPartida()

            elif self.estado == 4:    
                #carrega jogada (movimento, colisão...)
                #print("Jogando...")
                self.gerenciaJogo()
            
            elif self.estado == 5:    
                #carrega pós jogada 
                print("Carregando resultado...")
                self.verificaResultado()

            elif self.estado == 6:    
                #exibe roupas certas
                print("Exibe roupas certas...")
                self.exibeRoupasCertas()

            elif self.estado == 7:    
                #executa pós jogada (ações de acerto/erro e próx jogada ou fim de nível)
                print("Trocando a jogada...")
                self.finalizaJogada()                

        elif self.jogando == False:    
            #pausa
            if self.estado == 7:  
                self.carregaTelaTutorialFeedback()
            else:
                #print("Pausa...")
                self.carregaTelaTutorialPausa()
        
            
        
            
        