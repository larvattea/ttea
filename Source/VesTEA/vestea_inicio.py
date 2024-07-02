import pygame
from pygame import font
from pygame import display
from pygame.image import load
from pygame.transform import scale
from pygame import event
from pygame.locals import QUIT, KEYUP, K_SPACE, K_UP, K_DOWN, K_RIGHT
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
        self.fonte = font.SysFont('comicsans', 50)
        self.fonte_destaque = font.SysFont('comicsans', 80)

        self.superficie = display.set_mode(
            size=self.tamanho,
            display=0
        )
        display.set_caption(
            'VesTEA'
        )

        #create button instances
        self.imagem_inicio = pygame.image.load('VesTEA/images/button_inicio.png').convert_alpha()
        self.imagem_sair = pygame.image.load('VesTEA/images/button_sair.png').convert_alpha()
        self.botao_inicio = botao.Botao(30, 450, self.imagem_inicio, 0.8)
        self.botao_sair = botao.Botao(600, 450, self.imagem_sair, 0.8)
        
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
                        elif evento.key == K_UP:
                            print('UP')
                            self.jogo.posicaoJogador = 3
                            self.jogo.estado += 1
                        elif evento.key == K_DOWN:
                            self.jogo.posicaoJogador = 4
                            self.jogo.estado += 1
                        elif evento.key == K_RIGHT:
                            self.jogo.posicaoJogador = 2
                            self.jogo.estado += 1

            # Loop de eventos
            if self.estado==0:    
                self.superficie.fill((50, 50, 255))

                #self.superficie.blit(self.fundo_inicio, (0, 0))
                
                titulo = self.fonte_destaque.render(
                    'Ship Shoot',
                    True,
                    (255, 165, 0)
                )
                self.superficie.blit(titulo, (190, 180))
                
                if self.botao_inicio.criar(self.superficie):
                    #print('START')
                    #self.novo_jogo()
                    self.estado=1
                if self.botao_sair.criar(self.superficie):
                    #print('EXIT')
                    self.esta_rodando = False


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


