# ================================================
# KarTEA.py - Classe principal do jogo
# Versão Orientada a Objetos
# ================================================

import sys

import cv2
import pygame

# Imports das classes refatoradas
from udescjoinvilletteagames.kartea.gamecontroller import GameController
from udescjoinvilletteagames.kartea.gameutil import GameSettings
from udescjoinvilletteagames.kartea.gameview import Menu


# TODO aonde tiver chamada de arquivo fazer o acerto de configurações etc
class KarTEA:
    """Classe principal que gerencia o ciclo de vida completo do jogo."""

    def __init__(self):
        self.settings = GameSettings()
        pygame.init()
        pygame.display.set_caption(self.settings.WINDOW_NAME)

        self.screen = pygame.display.set_mode(
            (self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT)
        )
        self.clock = pygame.time.Clock()

        # Instâncias principais
        self.game_controller = GameController(self.screen)
        self.menu = Menu(self.screen)

        # Estado atual do jogo
        self.state = "menu"

    def user_events(self):
        """Gerencia eventos globais (fechar janela, ESC, teclas de atalho)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.close()
                    sys.exit()

                if event.key == pygame.K_q:  # Atalho rápido para sair
                    self.close()
                    sys.exit()

    def update(self):
        """Atualiza o estado atual (menu ou jogo)."""
        if self.state == "menu":
            result = self.menu.update()

            if result == "game":
                self.game_controller.reset()
                self.state = "game"

            elif result == "prev":
                # if arquivo.get_Nivel() != 1:
                #    arquivo.set_Nivel(arquivo.get_Nivel() - 1)
                self.game_controller.reset()
                self.state = "game"

            elif result == "rest":
                self.game_controller.reset()
                self.state = "game"

            elif result == "next":
                # if arquivo.get_Nivel() != 6:
                #    arquivo.set_Nivel(arquivo.get_Nivel() + 1)
                # else:
                # if arquivo.get_Fase() != 3:
                # arquivo.set_Fase(arquivo.get_Fase() + 1)
                # arquivo.set_Nivel(1)
                self.game_controller.reset()
                self.state = "game"

        elif self.state == "game":
            self.settings.TIME_PAST += self.clock.get_time()
            result = self.game_controller.update()

            if result == "menu":
                self.state = "menu"

    def draw(self):
        """Atualiza a tela (chamado após update)."""
        pygame.display.update()

    def run(self):
        """Loop principal do jogo."""
        try:
            while True:
                self.user_events()
                self.clock.tick(self.settings.FPS)
                self.update()
                self.draw()

                # Mostrar FPS (útil para debug)
                if self.settings.DRAW_FPS:
                    fps_font = pygame.font.SysFont("coopbl", 22)
                    fps_label = fps_font.render(
                        f"FPS: {int(self.clock.get_fps())}",
                        True,
                        (255, 200, 20),
                    )
                    self.screen.blit(fps_label, (5, 5))

        except Exception as e:
            print(f"Erro durante a execução do jogo: {e}")
        finally:
            self.close()

    def close(self):
        """Libera todos os recursos antes de fechar."""
        if hasattr(self.game_controller, "camera"):
            self.game_controller.camera.close_camera()
        if hasattr(self.game_controller, "pose_tracking"):
            self.game_controller.pose_tracking.close()
        cv2.destroyAllWindows()
        pygame.quit()


# ====================== Ponto de entrada padrão ======================
if __name__ == "__main__":
    kartea = KarTEA()
    kartea.run()
