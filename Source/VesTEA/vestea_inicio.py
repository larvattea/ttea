import pygame
from pygame import font
from pygame import display
from pygame.image import load
from pygame.transform import scale
from pygame import event
from pygame.locals import QUIT, KEYUP, K_SPACE, K_UP, K_DOWN, K_RIGHT, K_LEFT
from pygame.time import Clock

#from VesTEA.pose_tracking import PoseTracking

from VesTEA import botao
from VesTEA.jogo import Jogo


#se for executar de outra pasta, precisa de:
#import os
#os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Vestea():
    def __init__(self):
        pygame.init()
        self.esta_rodando = True
        self.estado = 0
        self.tamanho = 800, 600
        self.clock = Clock()
        self.fonte = font.SysFont('opensans', 40)
        self.fonte_destaque = font.SysFont('opensans', 80)

        self.superficie = display.set_mode(
            size=self.tamanho,
            display=0
        )
        display.set_caption(
            'VesTEA'
        )

       
        self.fundo = scale(
            load('VesTEA/images/space.jpg'),
            self.tamanho
        )

        self.jogo = Jogo(self.superficie)
                
        #self.fundo_inicio = scale(
        #    load('images/title_background.jpg'),
        #    self.tamanho
        #)

    def novo_jogo(self):
        #self.grupo_inimigos = Group()
        #self.grupo_tiros = Group()
        #self.jogador = Jogador(self)
        #self.grupo_jogador = GroupSingle(self.jogador) #permite draw
        #self.grupo_inimigos.add(Inimigo(self))

        self.mortes = 0
        #self.round = 0
    
    def rodar(self):
        #loop do jogo
        while self.esta_rodando:
            #print(evento)
            for evento in event.get():  # Events
                if evento.type == QUIT:
                    #print("clicou em fechar")
                    self.esta_rodando = False
                if self.estado==1:
                    if evento.type == KEYUP:
                        if evento.key == K_SPACE:
                            self.jogo.jogando = not self.jogo.jogando
                        elif evento.key == K_UP:#passou de fase
                            print('UP')
                            self.jogo.posicaoJogador = 3
                            self.jogo.estado += 1
                        elif evento.key == K_DOWN:#retroagiu a fase
                            self.jogo.posicaoJogador = 4
                            self.jogo.estado += 1
                        elif evento.key == K_RIGHT:#se posicionou no inicio
                            self.jogo.posicaoJogador = 2
                            self.jogo.estado += 1
                        elif evento.key == K_LEFT:#bateu na parede
                            #self.jogo.posicaoJogador = 1
                            self.jogo.acoesColisao(175,225)

            # Loop de eventos
            #TELA INICIAL
            if self.estado==0:    
                self.superficie.fill((238, 236, 225))
                #CRIA TÍTULO
                titulo = self.fonte_destaque.render(
                    'VesTEA',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(titulo, (300, 60))
                
                #CRIA BOTÕES
                self.imagem_jogar = pygame.image.load('VesTEA/images/button_jogar.png').convert_alpha()
                self.botao_jogar = botao.Botao(322, 160, self.imagem_jogar, 1)
                self.imagem_tutorial = pygame.image.load('VesTEA/images/button_tutorial.png').convert_alpha()
                self.botao_tutorial = botao.Botao(298, 250, self.imagem_tutorial, 1)
                self.imagem_opcoes = pygame.image.load('VesTEA/images/button_opcoes.png').convert_alpha()
                self.botao_opcoes = botao.Botao(407, 340, self.imagem_opcoes, 1)
                self.imagem_personalizar = pygame.image.load('VesTEA/images/button_personalizar.png').convert_alpha()
                self.botao_personalizar = botao.Botao(407, 430, self.imagem_personalizar, 1)
                self.imagem_sair = pygame.image.load('VesTEA/images/button_sair.png').convert_alpha()
                self.botao_sair = botao.Botao(339, 520, self.imagem_sair, 1)
        
                #TEXTOS
                texto_opcoes = self.fonte.render(
                    'Jogo configurado',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(texto_opcoes, (50, 365))
                texto_personalizar = self.fonte.render(
                    'Jogador: Vestea',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(texto_personalizar, (50, 445))
                
                
                if self.botao_jogar.criar(self.superficie):
                    #print('START')
                    #self.novo_jogo()
                    self.estado=1
                if self.botao_tutorial.criar(self.superficie):
                    print('NÃO IMPLEMENTADO')
                if self.botao_opcoes.criar(self.superficie):
                    print('NÃO IMPLEMENTADO')
                if self.botao_personalizar.criar(self.superficie):
                    print('NÃO IMPLEMENTADO')
                if self.botao_sair.criar(self.superficie):
                    #print('EXIT')
                    self.esta_rodando = False

            #JOGO
            elif self.estado==1:
                #self.jogo.jogando = True
                self.jogo.update()
                #print(self.estado,' e ',self.jogo.estado)
            display.update()


g = Vestea()
#g.novo_jogo()
g.rodar()

#print("saiu")
pygame.quit()
exit()


