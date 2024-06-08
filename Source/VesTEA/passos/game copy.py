from random import randint
import pygame
from pygame import font
from pygame import display
from pygame.image import load
from pygame.transform import scale
from pygame.sprite import Sprite, Group, GroupSingle, groupcollide
from pygame import event
from pygame.locals import QUIT, KEYUP, K_SPACE
from pygame.time import Clock
import botao

#se for executar de outra pasta, precisa de:
#import os
#os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Jogo:
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
            'Dá Hadouken, Ryu!'
        )

        #create button instances
        self.imagem_inicio = pygame.image.load('images/button_inicio.png').convert_alpha()
        self.imagem_sair = pygame.image.load('images/button_sair.png').convert_alpha()
        self.botao_inicio = botao.Button(30, 450, self.imagem_inicio, 0.8)
        self.botao_sair = botao.Button(600, 450, self.imagem_sair, 0.8)
        
        self.fundo = scale(
            load('images/space.jpg'),
            self.tamanho
        )

        self.fundo_inicio = scale(
            load('images/title_background.jpg'),
            self.tamanho
        )

    def novo_jogo(self):
        self.grupo_inimigos = Group()
        self.grupo_tiros = Group()
        self.jogador = Jogador(self.grupo_tiros, self)
        self.grupo_jogador = GroupSingle(self.jogador)
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
                #self.superficie.fill((202, 150, 150))

                self.superficie.blit(self.fundo_inicio, (0, 0))
                
                titulo = self.fonte_destaque.render(
                    'Dá Hadouken, Ryu!',
                    True,
                    (200, 0, 0)
                )
                self.superficie.blit(titulo, (50, 250))
                
                if self.botao_inicio.draw(self.superficie):
                    #print('START')
                    self.novo_jogo()
                    self.estado=1
                if self.botao_sair.draw(self.superficie):
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
                
                if self.botao_inicio.draw(self.superficie):
                    #print('RESTART')
                    self.novo_jogo()
                    self.estado=1
                if self.botao_sair.draw(self.superficie):
                    #print('EXIT')
                    self.esta_rodando = False

            display.update()


class Jogador(Sprite):
    def __init__(self, tiros, jogo):
        super().__init__()

        self.jogo = jogo
        self.image = load('images/Ryu.png')
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect()
        self.tiros = tiros
        self.velocidade = 2

    def atirar(self):
        if len(self.tiros) < 15:
            self.tiros.add(
                Tiro(*self.rect.center, self.rect.x+self.rect.width, self.jogo.tamanho[0])
            )

    def update(self):
        keys = pygame.key.get_pressed()

        tiros_fonte = self.jogo.fonte.render(
            f'Tiros: {15 - len(self.tiros)}',
            True,
            (255, 255, 255)
        )
        self.jogo.superficie.blit(tiros_fonte, (20, 20))

        if keys[pygame.K_LEFT] and self.rect.x>0:
            self.rect.x -= self.velocidade
        if keys[pygame.K_RIGHT] and self.rect.x<400:
            self.rect.x += self.velocidade
        if keys[pygame.K_UP] and self.rect.y>0:
            self.rect.y -= self.velocidade
        if keys[pygame.K_DOWN] and self.rect.y<self.jogo.tamanho[1]-self.rect.height:
            self.rect.y += self.velocidade


class Tiro(Sprite):
    def __init__(self, x, y, player_width, screen_width):
        super().__init__()

        self.screen_width = screen_width
        self.image = load('images/hadouken.png')
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect(
            center=(player_width, y)
        )

    def update(self):
        self.rect.x += 1

        if self.rect.x > self.screen_width:
            self.kill()


class Inimigo(Sprite):
    def __init__(self, jogo):
        super().__init__()

        self.jogo = jogo
        self.image = load('images/alvo.png')
        self.rect = self.image.get_rect(
            center=(self.jogo.tamanho[0], randint(20, 580))
        )

    def update(self):
        self.rect.x -= 1

        if self.rect.x == 0:
            #print("morreu")
            self.kill()
            self.jogo.estado = 2

g = Jogo()
#g.novo_jogo()
g.rodar()

#print("saiu")
pygame.quit()
exit()


