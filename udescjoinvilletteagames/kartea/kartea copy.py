# KarTEA.py
import sys

import arquivo
import cv2
import pygame
import settings
from game import Game
from menu import Menu
from settings import *


class KarTEA:
    """Classe principal que gerencia o jogo KarTEA (menu + game loop)"""

    def __init__(self):
        # Inicialização do Pygame
        pygame.init()
        pygame.display.set_caption(WINDOW_NAME)

        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT), 0, 0
        )
        self.clock = pygame.time.Clock()

        # Fontes
        self.fps_font = pygame.font.SysFont("coopbl", 22)

        # Instâncias principais
        self.game = Game(self.screen)
        self.menu = Menu(self.screen)

        # Estado inicial
        self.state = "menu"

        # Controle de saída
        self.running = True

    def handle_events(self):
        """Processa eventos globais (quit, teclas de atalho, etc)"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return

                if event.key == pygame.K_q:
                    self.running = False
                    cv2.destroyWindow(
                        "Tela de Captura"
                    )  # cuidado: só se janela existir
                    return

                if event.key == pygame.K_SPACE:
                    print("Space pressed (KarTEA)")
                    # Aqui você pode pausar ou voltar pro menu, se quiser
                    # self.state = "menu"

    def update_state(self):
        """Atualiza a lógica de acordo com o estado atual"""
        if self.state == "menu":
            action = self.menu.update()

            if action == "game":
                self.state = "game"

            elif action == "prev":
                if arquivo.get_Nivel() != 1:
                    arquivo.set_Nivel(arquivo.get_Nivel() - 1)
                self.game.reset()
                self.state = "game"

            elif action == "rest":
                self.game.reset()
                self.state = "game"

            elif action == "next":
                if arquivo.get_Nivel() != 6:
                    arquivo.set_Nivel(arquivo.get_Nivel() + 1)
                else:
                    if arquivo.get_Fase() != 3:
                        arquivo.set_Fase(arquivo.get_Fase() + 1)
                        arquivo.set_Nivel(1)
                self.game.reset()
                self.state = "game"

        elif self.state == "game":
            settings.TIME_PAST += self.clock.get_time()
            if self.game.update() == "menu":
                self.state = "menu"

    def draw_fps(self):
        if DRAW_FPS:
            fps_label = self.fps_font.render(
                f"FPS: {int(self.clock.get_fps())}", True, (255, 200, 20)
            )
            self.screen.blit(fps_label, (5, 5))

    def run(self):
        """Loop principal do jogo"""
        while self.running:
            self.handle_events()

            # Limita FPS e atualiza lógica
            self.clock.tick(FPS)
            self.update_state()

            # Atualiza tela
            pygame.display.update()

            # Mostra FPS (se ativado)
            self.draw_fps()

        # Finalização limpa
        pygame.quit()
        sys.exit()


# Ponto de entrada padrão
if __name__ == "__main__":
    game = KarTEA()
    game.run()
