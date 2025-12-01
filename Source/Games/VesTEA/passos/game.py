import os
from random import randint

import botao
import pygame
from pygame import display, event, font
from pygame.image import load
from pygame.locals import K_SPACE, KEYUP, QUIT
from pygame.sprite import Group, GroupSingle, Sprite, groupcollide
from pygame.time import Clock
from pygame.transform import scale

os.chdir(os.path.dirname(os.path.abspath(__file__)))

pygame.init()

tamanho = 800, 600
fonte = font.SysFont("comicsans", 50)
fonte_perdeu = font.SysFont("comicsans", 100)

superficie = display.set_mode(size=tamanho, display=0)
display.set_caption("Coffee Shooter")

fundo = scale(load("images/space.jpg"), tamanho)


class Jogador(Sprite):
    def __init__(self, tiros):
        super().__init__()

        self.image = load("images/Ryu.png")
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect()
        self.tiros = tiros
        self.velocidade = 2
        print(self.rect)

    def atirar(self):
        if len(self.tiros) < 15:
            self.tiros.add(
                Tiro(*self.rect.center, self.rect.x + self.rect.width)
            )

    def update(self):
        keys = pygame.key.get_pressed()

        tiros_fonte = fonte.render(
            f"Tiros: {15 - len(self.tiros)}", True, (255, 255, 255)
        )
        superficie.blit(tiros_fonte, (20, 20))

        if keys[pygame.K_LEFT] and self.rect.x > 0:
            self.rect.x -= self.velocidade
        if keys[pygame.K_RIGHT] and self.rect.x < 400:
            self.rect.x += self.velocidade
        if keys[pygame.K_UP] and self.rect.y > 0:
            self.rect.y -= self.velocidade
        if keys[pygame.K_DOWN] and self.rect.y < tamanho[1] - self.rect.height:
            self.rect.y += self.velocidade


class Tiro(Sprite):
    def __init__(self, x, y, wid):
        super().__init__()

        self.image = load("images/hadouken.png")
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect(center=(wid, y))

    def update(self):
        self.rect.x += 1

        if self.rect.x > tamanho[0]:
            self.kill()


class Virus(Sprite):
    def __init__(self):
        super().__init__()

        self.image = load("images/alvo.png")
        self.rect = self.image.get_rect(center=(800, randint(20, 580)))

    def update(self):
        global estado
        self.rect.x -= 1

        if self.rect.x == 0:
            self.kill()
            estado = 2


grupo_inimigos = Group()
grupo_tiros = Group()
jogador = Jogador(grupo_tiros)
grupo_duno = GroupSingle(jogador)

grupo_inimigos.add(Virus())

clock = Clock()
mortes = 0
round = 0
estado = 0

while True:
    print(estado)
    for evento in event.get():  # Events
        if evento.type == QUIT:
            pygame.quit()
        if estado == 1:
            if evento.type == KEYUP:
                if evento.key == K_SPACE:
                    jogador.atirar()

    # Loop de eventos
    if estado == 2:
        superficie.fill((202, 150, 150))

        deu_ruim = fonte_perdeu.render("Você perdeu!", True, (255, 255, 255))
        superficie.blit(deu_ruim, (50, 100))

        fonte_mortes = fonte.render(f"Mortes: {mortes}", True, (255, 255, 255))

        superficie.blit(fonte_mortes, (20, 20))

        start_img = pygame.image.load("images/start_btn.png").convert_alpha()
        exit_img = pygame.image.load("images/exit_btn.png").convert_alpha()
        # create button instances
        start_button = botao.Button(100, 300, start_img, 0.8)
        exit_button = botao.Button(450, 300, exit_img, 0.8)

        if start_button.draw(superficie):
            print("START")
            grupo_inimigos = Group()
            grupo_tiros = Group()
            jogador = Jogador(grupo_tiros)
            grupo_duno = GroupSingle(jogador)

            grupo_inimigos.add(Virus())

            mortes = 0
            round = 0
            estado = 1
        if exit_button.draw(superficie):
            print("EXIT")
            pygame.quit()
        display.update()
        # pygame.time.delay(1000)

    elif estado == 1:
        clock.tick(120)  # FPS

        if round % 120 == 0:
            if mortes < 20:
                grupo_inimigos.add(Virus())
            for i in range(int(mortes / 20)):
                grupo_inimigos.add(Virus())

        # Espaço dos eventos

        if groupcollide(grupo_tiros, grupo_inimigos, True, True):
            mortes += 1

        # Espaço do display
        superficie.blit(fundo, (0, 0))

        fonte_mortes = fonte.render(f"Mortes: {mortes}", True, (255, 255, 255))

        superficie.blit(fonte_mortes, (20, 70))

        grupo_duno.draw(superficie)
        grupo_inimigos.draw(superficie)
        grupo_tiros.draw(superficie)

        grupo_duno.update()
        grupo_inimigos.update()
        grupo_tiros.update()

        round += 1
        display.update()

    elif estado == 0:
        superficie.fill((202, 228, 241))

        start_img = pygame.image.load("images/start_btn.png").convert_alpha()
        exit_img = pygame.image.load("images/exit_btn.png").convert_alpha()
        # create button instances
        start_button = botao.Button(100, 200, start_img, 0.8)
        exit_button = botao.Button(450, 200, exit_img, 0.8)

        if start_button.draw(superficie):
            print("START")
            estado = 1
        if exit_button.draw(superficie):
            print("EXIT")
            pygame.quit()

        # event handler

        pygame.display.update()
