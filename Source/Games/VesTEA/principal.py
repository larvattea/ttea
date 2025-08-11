import pygame
from pygame import display, event, font
from pygame.image import load
from pygame.locals import K_SPACE, KEYUP, QUIT
from pygame.sprite import Group, GroupSingle, groupcollide
from pygame.time import Clock
from pygame.transform import scale
from VesTEA import botao
from VesTEA.inimigo import Inimigo
from VesTEA.jogador import Jogador

#se for executar de outra pasta, precisa de:
#import os
#os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Jogo():
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
            'Ship Shoot'
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

        #self.fundo_inicio = scale(
        #    load('images/title_background.jpg'),
        #    self.tamanho
        #)

    def novo_jogo(self):
        self.grupo_inimigos = Group()
        self.grupo_tiros = Group()
        self.jogador = Jogador(self)
        self.grupo_jogador = GroupSingle(self.jogador) #permite draw
        self.grupo_inimigos.add(Inimigo(self))

        self.mortes = 0
        self.round = 0
    
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
                            self.jogador.atirar()

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
                    self.novo_jogo()
                    self.estado=1
                if self.botao_sair.criar(self.superficie):
                    #print('EXIT')
                    self.esta_rodando = False


            elif self.estado==1:
                self.clock.tick(120)  # FPS

                if self.round % 120 == 0:
                    if self.mortes < 20:
                        self.grupo_inimigos.add(Inimigo(self))
                    for i in range(int(self.mortes / 20)):
                        self.grupo_inimigos.add(Inimigo(self))

                # Espaço dos eventos
                if groupcollide(self.grupo_tiros, self.grupo_inimigos, True, True):
                    self.mortes += 1

                # Espaço do display
                self.superficie.blit(self.fundo, (0, 0))

                fonte_tiros = self.fonte.render(
                    f'Tiros: {15 - len(self.jogador.tiros)}',
                    True,
                    (255, 255, 255)
                )

                self.superficie.blit(fonte_tiros, (20, 20))

                fonte_mortes = self.fonte.render(
                        f'Mortes: {self.mortes}',
                        True,
                        (255, 255, 255)
                )

                self.superficie.blit(fonte_mortes, (20, 70))

                self.grupo_jogador.draw(self.superficie)
                self.grupo_inimigos.draw(self.superficie)
                self.grupo_tiros.draw(self.superficie)

                self.grupo_jogador.update()
                self.grupo_inimigos.update()
                self.grupo_tiros.update()

                self.round += 1

            elif self.estado==2:
                self.superficie.fill((202, 150, 150))

                deu_ruim = self.fonte_destaque.render(
                    'Você perdeu!',
                    True,
                    (255, 255, 255)
                )
                self.superficie.blit(deu_ruim, (50, 100))

                fonte_mortes = self.fonte.render(
                        f'Mortes: {self.mortes}',
                        True,
                        (255, 255, 255)
                )

                self.superficie.blit(fonte_mortes, (20, 20))
                
                if self.botao_inicio.criar(self.superficie):
                    #print('RESTART')
                    self.novo_jogo()
                    self.estado=1
                if self.botao_sair.criar(self.superficie):
                    #print('EXIT')
                    self.esta_rodando = False

            display.update()


g = Jogo()
#g.novo_jogo()
g.rodar()

#print("saiu")
pygame.quit()
exit()


