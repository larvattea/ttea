import argparse
import sys

import cv2
import pygame

# import arquivo
# import settings
# from settings import *
from udescjoinvilletteagames.kartea.gamecontroller import GameController
from udescjoinvilletteagames.kartea.gameutil import GameSettings
from udescjoinvilletteagames.kartea.gameview import Menu
from udescjoinvilletteagames.kartea.service import PlayerKarteaConfigService


class KarTEA:
    """Classe principal que gerencia o jogo KarTEA."""

    def __init__(self):
        """Inicializa o jogo, janela, objetos e variáveis de estado."""
        parser = argparse.ArgumentParser(description="KarTEA Exergame")

        # Define os argumentos esperados
        parser.add_argument(
            "--lang", type=str, default="pt", help="Idioma do app"
        )
        parser.add_argument(
            "--player_id", type=int, default=0, help="ID do Jogador"
        )
        parser.add_argument(
            "--professional_id", type=int, default=0, help="ID do Profissional"
        )

        args = parser.parse_args()

        # Agora você pode acessar os valores
        self.current_lang = args.lang
        self.player_id = args.player_id
        self.professional_id = args.professional_id

        self.service = PlayerKarteaConfigService()
        self.default_config = self.service.get_kartea_ini_config()
        pygame.init()
        pygame.display.set_caption(GameSettings.WINDOW_NAME)

        self.screen = pygame.display.set_mode(
            (GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT)
        )
        self.clock = pygame.time.Clock()

        # Fonts
        self.fps_font = pygame.font.SysFont("coopbl", 22)

        # Inicialização do mixer
        pygame.mixer.init()

        # Criação dos objetos principais
        self.game = GameController(self.screen)
        self.menu = Menu(self.screen)

        # Estado atual do jogo
        self.state = "menu"

        # Variáveis de controle
        self.running = True

        # TODO colocar no settings
        self.phase = self.default_config["game_settings"]["phase_default"]
        self.level = self.default_config["game_settings"]["level_default"]
        self.level_time = self.default_config["game_settings"][
            "level_time_default"
        ]

        # (Música comentada - mantida como no original)
        # pygame.mixer.music.load("Assets/Kartea/Sounds/Komiku_-_12_-_Bicycle.mp3")
        # pygame.mixer.music.set_volume(MUSIC_VOLUME)
        # pygame.mixer.music.play(-1)

    def handle_events(self):
        """Gerencia todos os eventos do usuário."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                if event.key == pygame.K_SPACE:
                    self.state = "menu"

                # Teclas de atalho adicionais (mantidas do original)
                if event.key == pygame.K_q:
                    self.running = False
                    cv2.destroyWindow("Tela de Captura")

    def update_menu(self):
        """Atualiza o menu e processa as transições de estado."""
        menu_result = self.menu.update()

        if menu_result == "game":
            self.state = "game"

        elif menu_result == "prev":
            if self.level != 1:
                self.level = self.level - 1
            self.game.reset()
            self.state = "game"

        elif menu_result == "rest":
            self.game.reset()
            self.state = "game"

        elif menu_result == "next":
            if self.level != 6:
                self.level = self.level + 1
            else:
                if self.phase != 3:
                    self.phase = self.phase + 1
                    self.level = 1
            self.game.reset()
            self.state = "game"

    def update_game(self):
        """Atualiza a lógica do jogo."""
        GameSettings.TIME_PAST += self.clock.get_time()

        if self.game.update() == "menu":
            self.state = "menu"

    def update(self):
        """Atualiza o estado atual do jogo."""
        if self.state == "menu":
            self.update_menu()
        elif self.state == "game":
            self.update_game()

    def draw_fps(self):
        """Desenha o contador de FPS no canto superior esquerdo."""
        if GameSettings.DRAW_FPS:
            fps_label = self.fps_font.render(
                f"FPS: {int(self.clock.get_fps())}", True, (255, 200, 20)
            )
            self.screen.blit(fps_label, (5, 5))

    def run(self):
        """Loop principal do jogo."""
        try:
            pygame.init()
        except Exception as e:
            print(f"Erro ao iniciar pygame: {e}")
            return

        while self.running:
            # Eventos
            self.handle_events()

            # Atualização
            self.clock.tick(GameSettings.FPS)
            self.update()

            # Desenho / Renderização
            pygame.display.update()

            # FPS (mantido fora do update para ficar sempre visível)
            self.draw_fps()

        # Finalização limpa
        pygame.quit()
        sys.exit()


# ====================== EXECUÇÃO DO JOGO ======================
if __name__ == "__main__":
    kartea = KarTEA()
    kartea.run()
