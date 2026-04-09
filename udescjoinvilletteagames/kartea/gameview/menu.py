import sys

import pygame

from udescjoinvilletteagames.kartea.gamemodel import Background, Image
from udescjoinvilletteagames.kartea.gameui import UI
from udescjoinvilletteagames.kartea.gameutil import GameSettings
from udescjoinvilletteagames.kartea.util import KarteaPathConfig


class Menu:
    """Gerencia todas as telas de menu, pausa e feedback."""

    def __init__(self, surface: pygame.Surface):
        self.settings = GameSettings()
        self.ui = UI()
        self.surface = surface
        self.background = Background()
        self.click_sound = pygame.mixer.Sound(
            KarteaPathConfig.game_sound("point.wav")
        )

        # Carrega background do menu (mantido compatível)
        self.background_menu_image = Image.load(
            KarteaPathConfig.game_image("background_menu.png"),
            # "Assets/Kartea/Background_Menu.png",
            size=(self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT),
        )

    def draw_background(self):
        """Desenha o fundo comum do menu."""
        self.background.draw(
            self.surface
        )  # usa o background da pista como base
        Image.draw(self.surface, self.background_menu_image, (0, 0))

    def draw_feedback(self):
        """Desenha as estatísticas na tela de feedback."""
        center_x = self.settings.SCREEN_WIDTH // 2

        self.ui.draw_text(
            self.surface,
            "Feedback",
            (center_x + 50, 100),
            self.settings.COLORS["title"],
            font=self.settings.FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

        self.ui.draw_text(
            self.surface,
            "Quantidade",
            (center_x + 250, 100),
            self.settings.COLORS["title"],
            font=self.settings.FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

        # Pontuação
        self.ui.draw_text(
            self.surface,
            "Pontuação",
            (center_x + 50, 130),
            self.settings.COLORS["title"],
            font=self.settings.FONTS["medium"],
            shadow=True,
        )

        self.ui.draw_text(
            self.surface,
            str(self.settings.score),
            (center_x + 250, 130),
            self.settings.COLORS["title"],
            font=self.settings.FONTS["medium"],
            shadow=True,
        )

        # Movimentos
        self.ui.draw_text(
            self.surface,
            "Movimentos",
            (center_x + 50, 160),
            self.settings.COLORS["title"],
            font=self.settings.FONTS["medium"],
            shadow=True,
        )
        self.ui.draw_text(
            self.surface,
            str(self.settings.move),
            (center_x + 250, 160),
            self.settings.COLORS["title"],
            font=self.settings.FONTS["medium"],
            shadow=True,
        )

        # Alvos
        self.ui.draw_text(
            self.surface,
            "Alvos Gerados",
            (center_x + 50, 190),
            self.settings.COLORS["title"],
            font=self.settings.FONTS["medium"],
            shadow=True,
        )
        self.ui.draw_text(
            self.surface,
            str(self.settings.target),
            (center_x + 250, 190),
            self.settings.COLORS["title"],
            font=self.settings.FONTS["medium"],
            shadow=True,
        )

        self.ui.draw_text(
            self.surface,
            "Alvos Colididos",
            (center_x + 50, 220),
            self.settings.COLORS["title"],
            font=self.settings.FONTS["medium"],
            shadow=True,
        )
        self.ui.draw_text(
            self.surface,
            str(self.settings.target_c),
            (center_x + 250, 220),
            self.settings.COLORS["title"],
            font=self.settings.FONTS["medium"],
            shadow=True,
        )

        self.ui.draw_text(
            self.surface,
            "Alvos Desviados",
            (center_x + 50, 250),
            self.settings.COLORS["title"],
            font=self.settings.FONTS["medium"],
            shadow=True,
        )
        self.ui.draw_text(
            self.surface,
            str(self.settings.target_d),
            (center_x + 250, 250),
            self.settings.COLORS["title"],
            font=self.settings.FONTS["medium"],
            shadow=True,
        )

        # Obstáculos
        self.ui.draw_text(
            self.surface,
            "Obst. Gerados",
            (center_x + 50, 280),
            self.settings.COLORS["title"],
            font=self.settings.FONTS["medium"],
            shadow=True,
        )
        self.ui.draw_text(
            self.surface,
            str(self.settings.obstacle),
            (center_x + 250, 280),
            self.settings.COLORS["title"],
            font=self.settings.FONTS["medium"],
            shadow=True,
        )

        self.ui.draw_text(
            self.surface,
            "Obst. Desviados",
            (center_x + 50, 310),
            self.settings.COLORS["title"],
            font=self.settings.FONTS["medium"],
            shadow=True,
        )
        self.ui.draw_text(
            self.surface,
            str(self.settings.obstacle_d),
            (center_x + 250, 310),
            self.settings.COLORS["title"],
            font=self.settings.FONTS["medium"],
            shadow=True,
        )

        self.ui.draw_text(
            self.surface,
            "Obst. Colididos",
            (center_x + 50, 340),
            self.settings.COLORS["title"],
            font=self.settings.FONTS["medium"],
            shadow=True,
        )
        self.ui.draw_text(
            self.surface,
            str(self.settings.obstacle_c),
            (center_x + 250, 340),
            self.settings.COLORS["title"],
            font=self.settings.FONTS["medium"],
            shadow=True,
        )

    def update(self):
        """Atualiza e desenha a tela atual do menu."""
        self.draw_background()

        current_menu = self.settings.MENU

        if current_menu == "Inicial":
            return self._draw_initial_menu()

        if current_menu == "Pause":
            return self._draw_pause_menu()

        if current_menu in ("Feedback_1", "Feedback_2", "Feedback_3"):
            return self._draw_feedback_menu(current_menu)

        # Retorna string indicando ação (usado pelo KarTEA.py)
        return None

    def _draw_initial_menu(self):
        """Tela inicial do jogo."""
        self.ui.draw_text(
            self.surface,
            self.settings.GAME_TITLE,
            (self.settings.SCREEN_WIDTH // 2, 120),
            self.settings.COLORS["title"],
            font=self.settings.FONTS["big"],
            shadow=True,
            shadow_color=(255, 255, 255),
            pos_mode="center",
        )

        if self.ui.button(
            self.surface, 0, 300, "Jogar", click_sound=self.click_sound
        ):
            return "game"

        if self.ui.button(
            self.surface,
            0,
            300 + self.settings.BUTTONS_SIZES[1] * 4,
            "Sair",
            click_sound=self.click_sound,
        ):
            pygame.quit()
            sys.exit()

        return None

    def _draw_pause_menu(self):
        """Tela de pausa."""
        self.ui.draw_text(
            self.surface,
            "Pause",
            (self.settings.SCREEN_WIDTH // 2, 120),
            self.settings.COLORS["title"],
            font=self.settings.FONTS["big"],
            shadow=True,
            shadow_color=(255, 255, 255),
            pos_mode="center",
        )

        if self.ui.button(
            self.surface, 0, 300, "Continuar", click_sound=self.click_sound
        ):
            return "game"

        if self.ui.button(
            self.surface,
            1,
            300 + self.settings.BUTTONS_SIZES[1] * 2,
            "Retroceder",
            click_sound=self.click_sound,
        ):
            return "prev"

        if self.ui.button(
            self.surface,
            0,
            300 + self.settings.BUTTONS_SIZES[1] * 2,
            "Reiniciar",
            click_sound=self.click_sound,
        ):
            return "rest"

        if self.ui.button(
            self.surface,
            2,
            300 + self.settings.BUTTONS_SIZES[1] * 2,
            "Avançar",
            click_sound=self.click_sound,
        ):
            return "next"

        if self.ui.button(
            self.surface,
            0,
            300 + self.settings.BUTTONS_SIZES[1] * 4,
            "Sair",
            click_sound=self.click_sound,
        ):
            pygame.quit()
            sys.exit()

        return None

    def _draw_feedback_menu(self, feedback_type: str):
        """Telas de feedback (1 = ruim, 2 = médio, 3 = bom)."""
        # Desenha troféu correspondente
        if feedback_type == "Feedback_1":
            trofeu = Image.load("Assets/Kartea/trofeu - 25.png")
        elif feedback_type == "Feedback_2":
            trofeu = Image.load("Assets/Kartea/trofeu - 50.png")
        else:  # Feedback_3
            trofeu = Image.load("Assets/Kartea/trofeu - 75.png")

        Image.draw(self.surface, trofeu, (0, 0))

        self.draw_feedback()

        # Botões
        if self.ui.button(
            self.surface,
            2,
            300 + self.settings.BUTTONS_SIZES[1] * 4,
            "Jogar",
            click_sound=self.click_sound,
        ):
            if feedback_type == "Feedback_1":
                return "prev"
            elif feedback_type == "Feedback_2":
                return "rest"
            else:
                return "next"

        if self.ui.button(
            self.surface,
            1,
            300 + self.settings.BUTTONS_SIZES[1] * 4,
            "Sair",
            click_sound=self.click_sound,
        ):
            pygame.quit()
            sys.exit()

        return None
