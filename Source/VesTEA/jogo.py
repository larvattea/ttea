import pygame
import numpy as np
from VesTEA.desafio import Desafio
from VesTEA.tela import Tela
from VesTEA.telaparcial import TelaParcial
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

class Jogo():
    def __init__(self, superficie, fase, nivel):
        self.jogando = True
        self.fase = fase
        self.nivel = nivel
        #mensuram nível
        self.jogada = 1
        self.pontos = 0
        self.colisoes = 0
        #controlam ajuda
        self.ultimaPosicao = [-9999,-9999]
        self.tempoSemMovimento = datetime.datetime.now()
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


    def carregaDados(self):
        #mensuram nível
        Config.som_inicio.play()
        if self.jogada == 1:
            self.pontos = 0
            self.totalAcertos = 0
            self.totalColisoes = 0
            self.totalTempo = datetime.datetime.now()
            self.totalAjudas = 0
            self.trofeu = 2
        self.tempoSemMovimento = 0    
        self.colisoes = 0
        self.ajuda = False
        self.desafio = Desafio(self.fase, self.nivel, self.jogada)
        self.estado += 1
        self.ultimaPosicao = [-9999,-9999]
         
    
    def carregaTelaJogo(self):
        self.tela = Tela(self.desafio, 1)
        #inserindo captura do jogador
        self.cap.load_camera()
        self.cap.frame = self.jogador.scan_feets(self.cap.frame)
        x,y = self.jogador.get_feet_center()
        #print("Jogador em: ",x," - ",y)
        pygame.draw.circle(self.superficie, (255,255,0), [x,y-90],15)
        self.posicaoJogador = self.desafio.detectaColisao(x,y)
        print("Jogador em: ",self.posicaoJogador)
        #print(self.posicaoJogador == '2' or self.posicaoJogador == '22')
        if self.posicaoJogador == '2' or self.posicaoJogador == '22':
            #self.posicaoJogador = '99'
            #print("Jogador em: ",self.posicaoJogador)
            #mostrar só desafio     
            self.tela = Tela(self.desafio, 2)
            display.update()
            self.tempoSemMovimento = datetime.datetime.now() 
            #print(f"Tempo parado 1:{(datetime.datetime.now() - self.tempoSemMovimento).seconds} segundos")
            pygame.time.delay(3000)   
            #mostrar labirinto e roupas
            #print(f"Tempo parado 2:{(datetime.datetime.now() - self.tempoSemMovimento).seconds} segundos")
            self.tela = Tela(self.desafio, 3)
            display.update()
            pygame.time.delay(2000)
            self.cap.load_camera()
            self.estado += 1

    def carregaPartida(self):
        #self.posicaoJogador = '99'
        self.tela = Tela(self.desafio, 3)
        #print("Jogador 2 em: ",self.posicaoJogador)
        self.cap.load_camera()
        self.cap.frame = self.jogador.scan_feets(self.cap.frame)
        x,y = self.jogador.get_feet_center()
        #print("Jogador em: ",x," - ",y)
        pygame.draw.circle(self.superficie, (255,255,0), [x,y-90],15)
        self.posicaoJogador = self.desafio.detectaColisao(x,y)
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
        self.tela = Tela(self.desafio, 3)
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
            pygame.draw.rect(self.tela.roupacerta_img, (0,255,0), (0, 0, 100, 100),10)
            certo_rect = self.tela.roupacerta_img.get_rect(topleft = self.tela.roupacerta_pos)
            self.superficie.blit(self.tela.roupacerta_img, certo_rect)
        #senão, entra em pausa    
        elif ((datetime.datetime.now() - self.tempoSemMovimento).seconds > 10):
            self.jogando = False
            
        #print("Jogador em: ",x,"-",y)
        pygame.draw.circle(self.superficie, (255,255,0), [x,y-90], 15)
        self.posicaoJogador = self.desafio.detectaColisao(x,y)
        if self.posicaoJogador == '3' or self.posicaoJogador == '33' or self.posicaoJogador == '4' or self.posicaoJogador == '44':
            self.estado += 1
        if self.desafio.nivel >= 6:  
            if self.posicaoJogador == '5' or self.posicaoJogador == '55':
                self.estado += 1
        if self.posicaoJogador == '1':
            self.acoesColisao(x,y)

    def verificaResultado(self):
        #some o labirinto
        self.tela = Tela(self.desafio, 4)
        #desenha retangulo na roupa certa
        pygame.draw.rect(self.tela.roupacerta_img, (0,255,0), (0, 0, 100, 100),10)
        certo_rect = self.tela.roupacerta_img.get_rect(topleft = self.tela.roupacerta_pos)
        self.superficie.blit(self.tela.roupacerta_img, certo_rect)
        #desenha retangulo na roupa errada
        pygame.draw.rect(self.tela.roupaerrada_img, (255,0,0), (0, 0, 100, 100),10)
        erro_rect = self.tela.roupaerrada_img.get_rect(topleft = self.tela.roupaerrada_pos)
        self.superficie.blit(self.tela.roupaerrada_img, erro_rect)
        #desenha retangulo na roupa coringa
        if self.desafio.roupa_coringa != "":
            if self.desafio.nivel>=11:    
                pygame.draw.rect(self.tela.roupacoringa_img, (0,255,0), (0, 0, 100, 100),10)
            else:
                pygame.draw.rect(self.tela.roupacoringa_img, (255,0,0), (0, 0, 100, 100),10)
            coringa_rect = self.tela.roupacoringa_img.get_rect(topleft = self.tela.roupacoringa_pos)
            self.superficie.blit(self.tela.roupacoringa_img, coringa_rect)
        
        ######logica antiga de verificação de avanço/volta
        #if self.posicaoJogador == 3 or self.posicaoJogador == 33: 
        #    self.acoesAvancaNivel()
        #elif self.posicaoJogador == 4 or self.posicaoJogador == 44:
        #    self.acoesVoltaNivel()
        ######logica nova de verificacao de avanço/volta
        ##calcula pontuação
        #se acertou sem ajuda, 10 ptos, se acertou om ajuda 5 pts    
        if self.posicaoJogador == '3' or self.posicaoJogador == '33': 
            Config.som_acerto.play()
            self.totalAcertos += 1
            if self.ajuda == False:
                self.pontos += 10    
            else: 
                self.pontos += 5    
        elif self.desafio.nivel >= 11 and (self.posicaoJogador == '5' or self.posicaoJogador == '55'): 
            Config.som_acerto.play()
            self.totalAcertos += 1
            if self.ajuda == False:
                self.pontos += 10    
            else: 
                self.pontos += 5  
        elif self.posicaoJogador == '4' or self.posicaoJogador == '44':
            Config.som_erro.play()
        #display.update()
        #soma pontos por não colidir        
        self.pontos += 10 - self.colisoes
        display.update()
        pygame.time.delay(2500)
        self.estado += 1

    def exibeRoupasCertas(self):
        #some roupa errada
        self.tela = Tela(self.desafio, 5)   
        #desenha retangulo na roupa certa
        pygame.draw.rect(self.tela.roupacerta_img, (0,255,0), (0, 0, 100, 100),10)
        certo_rect = self.tela.roupacerta_img.get_rect(topleft = self.tela.roupacerta_pos)
        self.superficie.blit(self.tela.roupacerta_img, certo_rect)
        #desenha retangulo na roupa coringa se for certa
        if self.desafio.roupa_coringa != "":
            if self.desafio.nivel>=11:    
                pygame.draw.rect(self.tela.roupacoringa_img, (0,255,0), (0, 0, 100, 100),10)
                coringa_rect = self.tela.roupacoringa_img.get_rect(topleft = self.tela.roupacoringa_pos)
                self.superficie.blit(self.tela.roupacoringa_img, coringa_rect)
        display.update()
        pygame.time.delay(3000)
        self.cap.load_camera()
        self.estado += 1

    def finalizaJogada(self):
        #some roupa errada
        self.tela = Tela(self.desafio, 6)   
        #desenha retangulo na roupa certa
        pygame.draw.rect(self.tela.roupacerta_img, (0,255,0), (0, 0, 100, 100),10)
        certo_rect = self.tela.roupacerta_img.get_rect(topleft = self.tela.roupacerta_pos)
        self.superficie.blit(self.tela.roupacerta_img, certo_rect)
        #desenha retangulo na roupa coringa se for certa
        if self.desafio.roupa_coringa != "":
            if self.desafio.nivel>=11:    
                pygame.draw.rect(self.tela.roupacoringa_img, (0,255,0), (0, 0, 100, 100),10)
                coringa_rect = self.tela.roupacoringa_img.get_rect(topleft = self.tela.roupacoringa_pos)
                self.superficie.blit(self.tela.roupacoringa_img, coringa_rect)
        #se for terceira jogada, exibe tela de resultado
        if self.jogada == 3 :
            Config.som_trofeu.play()
            print("Pontos jogada 3 = ",self.pontos)
            self.totalTempo = datetime.datetime.now() - self.totalTempo
            self.jogada = 1
            self.posicaoJogador = 0
            if self.pontos <=20:
                self.trofeu = 1
            elif self.pontos >= 40:
                self.trofeu = 3
            self.jogando = False
        #senão, se jogador não estiver no ponto inicial, verifica sua posição    
        elif self.posicaoJogador != '2' and self.posicaoJogador != '22':
            #inserindo captura do jogador
            self.cap.load_camera()
            self.cap.frame = self.jogador.scan_feets(self.cap.frame)
            x,y = self.jogador.get_feet_center()
            #print("Jogador em: ",x," - ",y)
            pygame.draw.circle(self.superficie, (255,255,0), [x,y-90],15)
            self.posicaoJogador = self.desafio.detectaColisao(x,y)
        #se jogador voltar pro ponto inicial
        else:
            #se for jogada 1 ou 2, troca pra seguinte
            print("Pontos jogada ",self.jogada," = ",self.pontos)
            self.jogada += 1
            self.posicaoJogador = '0'
            pygame.time.delay(1000)
            self.estado = 1      
        display.update()

    def acoesAvancaNivel(self):
        
        print('avança')
        if self.nivel<15:
            self.nivel += 1
        elif self.nivel==15 and self.fase <3:
            self.fase += 1
            self.nivel = 1
    
    def acoesVoltaNivel(self):
        print('Volta')
        
        if self.nivel == 1 and self.fase >1:
            self.fase -= 1
            self.nivel = 15
        elif self.nivel > 1:
            self.nivel -= 1    

    def acoesColisao(self, x, y):
        Config.som_erro.play()
        print('Bateu na parede')
        #pintar o quadrado
        self.desafio.labirinto = self.desafio.mudaParedeAtingida(x,y,self.desafio.labirinto)
        #se ainda não tem 10 colisoes, soma mais uma     
        if self.colisoes < 10:    
            self.colisoes += 1
            self.totalColisoes += 1
        

    def carregaTelaPausa(self):
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
            self.estado = 2 #para reiniciar o jogo no mesmo desafio, mas do começo
            self.jogando = True
        

    def carregaTelaFeedback(self):
        self.superficie.fill((238, 236, 225))
        trofeu = image.load(f"VesTEA/images/trofeu{self.trofeu}.png")
        image.draw(self.superficie, trofeu, (0, 0))        
        ui.draw_text(self.superficie, "Feedback", (450, 100), (38, 61, 39), font=pygame.font.Font(None, 25),
                         shadow=False)
        ui.draw_text(self.superficie, "Quantidade", (650, 100), (38, 61, 39), font=pygame.font.Font(None, 25),
                         shadow=False)

        ui.draw_text(self.superficie, "Tempo", (450, 130), (38, 61, 39), font=pygame.font.Font(None, 25),
                         shadow=False)
        ui.draw_text(self.superficie, str(self.totalTempo).split(".")[0], (650, 130), (38, 61, 39), font=pygame.font.Font(None, 25),
                         shadow=False)

        ui.draw_text(self.superficie, "Pontuação (%)", (450, 160), (38, 61, 39), font=pygame.font.Font(None, 25),
                         shadow=False)
        ui.draw_text(self.superficie, str(round(self.pontos*100/60, 2)), (650, 160), (38, 61, 39), font=pygame.font.Font(None, 25),
                         shadow=False)

        ui.draw_text(self.superficie, "Roupas certas", (450, 190), (38, 61, 39), font=pygame.font.Font(None, 25),
                         shadow=False)
        ui.draw_text(self.superficie, f"{self.totalAcertos} de 3", (650, 190), (38, 61, 39), font=pygame.font.Font(None, 25),
                         shadow=False)

        ui.draw_text(self.superficie, "Ajudas", (450, 220), (38, 61, 39), font=pygame.font.Font(None, 25),
                         shadow=False)
        ui.draw_text(self.superficie, f"{self.totalAjudas}", (650, 220), (38, 61, 39), font=pygame.font.Font(None, 25),
                         shadow=False)

        ui.draw_text(self.superficie, "Paredes Colididas", (450, 250), (38, 61, 39), font=pygame.font.Font(None, 25),
                         shadow=False)
        ui.draw_text(self.superficie, str(self.totalColisoes), (650, 250), (38, 61, 39), font=pygame.font.Font(None, 25),
                         shadow=False)

        self.imagem_inicio = pygame.image.load('VesTEA/images/button_jogar.png').convert_alpha()
        self.botao_inicio = Botao(350, 450, self.imagem_inicio, 1)
        if self.botao_inicio.criar(self.superficie):
            #print('START')
            if self.trofeu == 1:
                self.acoesVoltaNivel()
            elif self.trofeu == 3:
                self.acoesAvancaNivel()
            self.jogando = True             
            self.posicaoJogador = '0'
            self.estado = 1 #para reiniciar o jogo no desafio desejado
            
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
                #print("Carregando tela...")
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
                self.carregaTelaFeedback()
            else:
                #print("Pausa...")
                self.carregaTelaPausa()
        
            
        
            
        