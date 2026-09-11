import argparse
import gettext
import os
import sys
from typing import Optional

import cv2
import pygame

from ttea.games.kartea.gamecontroller import GameController
from ttea.games.kartea.gameutil import GameSettings
from ttea.games.kartea.gameutil.alphablit import alpha_blit
from ttea.games.kartea.gameview import Menu
from ttea.games.kartea.model import PlayerKarteaConfig
from ttea.games.kartea.service import PlayerKarteaConfigService
from ttea.games.kartea.util import KarteaPathConfig


class KarTEA:
    """Classe principal que gerencia o jogo KarTEA."""

    def __init__(self):
        """Inicializa o jogo, janela, objetos e variáveis de estado."""
        parser = argparse.ArgumentParser(description="KarTEA Exergame")

        # 1. Parse de argumentos
        parser.add_argument(
            "--lang", type=str, default="pt_BR", help="Idioma do app"
        )
        parser.add_argument(
            "--player_id", type=int, default=0, help="ID do Jogador"
        )
        parser.add_argument(
            "--professional_id", type=int, default=0, help="ID do Profissional"
        )

        args = parser.parse_args()

        self.set_game_language(args.lang)

        # 2. Busca de dados
        self.service = PlayerKarteaConfigService()
        self.player_config = self.service.find_config_by_player_id(
            args.player_id
        )

        self.default_config = self.service.get_kartea_ini_config()

        if self.player_config is None:
            self.player_config = self.create_player_config(
                args.player_id, self.default_config
            )

        # 3. DELEGAÇÃO: Passa tudo para o GameSettings
        GameSettings.setup(
            args, self.service, self.player_config, self.default_config
        )

        # 4. Inicialização do Pygame usando os valores que agora estão no GameSettings
        pygame.init()
        pygame.display.set_caption(GameSettings.WINDOW_NAME)

        if GameSettings.FULLSCREEN:
            self.screen = pygame.display.set_mode(
                (GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT),
                pygame.FULLSCREEN,
                display=GameSettings.SCREEN_OS_INDEX,
            )
        else:
            self.screen = pygame.display.set_mode(
                (GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT),
                display=GameSettings.SCREEN_OS_INDEX,
            )

        GameSettings.regain_focus()

        self.clock = pygame.time.Clock()

        # Fonts
        self.fps_font = pygame.font.SysFont("cooperblack", 22)

        # Inicialização do mixer
        pygame.mixer.init()

        # Criação dos objetos principais
        self.game = GameController(self.screen)
        self.menu = Menu(self.screen)

        # Estado atual do jogo
        self.state = "menu"

        # Variáveis de controle
        self.running = True

    def create_player_config(
        self, player_id: int, ini_data: dict
    ) -> Optional[PlayerKarteaConfig]:
        game_settings = ini_data.get("game_settings", {})
        visual_res = ini_data.get("visual_resources", {})
        visual_feed = ini_data.get("visual_feedback", {})
        sound_feed = ini_data.get("sound_feedback", {})
        interface = ini_data.get("interface_settings", {})

        data = {
            "player_id": player_id,
            "session_id": None,
            "phase_id": int(game_settings.get("phase_default", 1)),
            "level_id": int(game_settings.get("level_default", 1)),
            "level_time": int(game_settings.get("level_time_default", 120)),
            "vehicle_image": visual_res.get(
                "vehicle_image_default", "defaultvehicle"
            ),
            "environment_image_right": visual_res.get(
                "environment_image_default_right", "right"
            ),
            "environment_image_left": visual_res.get(
                "environment_image_default_left", "left"
            ),
            "target_image": visual_res.get(
                "target_image_default", "defaultstar"
            ),
            "obstacle_image": visual_res.get(
                "obstacle_image_default", "defaultobstacle"
            ),
            "positive_feedback_image": visual_feed.get(
                "positive_feedback_image_default", "positive"
            ),
            "neutral_feedback_image": visual_feed.get(
                "neutral_feedback_image_default", "neutral"
            ),
            "negative_feedback_image": visual_feed.get(
                "negative_feedback_image_default", "negative"
            ),
            "positive_feedback_sound": sound_feed.get(
                "positive_feedback_sound_default", "hit"
            ),
            "neutral_feedback_sound": sound_feed.get(
                "neutral_feedback_sound_default", "miss"
            ),
            "negative_feedback_sound": sound_feed.get(
                "negative_feedback_sound_default", "error"
            ),
            "palette": int(interface.get("palette_default", 0)),
            "hud": interface.get("hud_default", "true").lower() == "true",
            "sound": interface.get("sound_default", "true").lower() == "true",
        }
        return self.service.create_config(data)

    def set_game_language(self, lang_code="pt_BR"):
        locales_dir = os.path.join(
            KarteaPathConfig.KARTEA_RESOURCES_DIR, "locales"
        )
        translation = gettext.translation(
            "kartea",
            localedir=locales_dir,
            languages=[lang_code],
            fallback=True,
        )
        translation.install()

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
            GameSettings.regain_focus()  # Traz a janela do Pygame de volta para o foco ativo
        elif menu_result == "prev":
            if GameSettings.LEVEL != 1:
                GameSettings.LEVEL = GameSettings.LEVEL - 1
            self.game.reset()
            self.state = "game"
        elif menu_result == "rest":
            self.game.reset()
            self.state = "game"
        elif menu_result == "next":
            if GameSettings.LEVEL != 7:
                GameSettings.LEVEL = GameSettings.LEVEL + 1
            else:
                if GameSettings.PHASE != 3:
                    GameSettings.PHASE = GameSettings.PHASE + 1
                    GameSettings.LEVEL = 1
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
            alpha_blit(self.screen, fps_label, (5, 5))

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


def main() -> None:
    """Start the KarTEA Game."""
    kartea = KarTEA()
    kartea.run()


if __name__ == "__main__":
    main()
