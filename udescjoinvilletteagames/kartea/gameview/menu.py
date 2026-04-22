import sys

import pygame

from udescjoinvilletteagames.kartea.gamemodel import Background, Image
from udescjoinvilletteagames.kartea.gameui import UI

# import settings
# from settings import *
# from background import Background


class Menu:
    """Classe responsável por gerenciar todos os menus e telas de feedback do jogo."""

    def __init__(self, surface):
        self.surface = surface

        # Background do menu
        self.background = Background()
        self.background.background_menu()

        # Som de clique (usado em todos os botões)
        self.click_sound = pygame.mixer.Sound("Assets/Kartea/Sounds/point.wav")

    def draw(self):
        """Desenha o fundo básico do menu."""
        self.background.draw(self.surface)
        fundo = Image.load(
            "Assets/Kartea/Fundo.png", size=(SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        Image.draw(self.surface, fundo, (0, 0))

    def draw_feedback(self):
        """Desenha a tela de feedback com estatísticas do nível."""
        ui.draw_text(
            self.surface,
            "Feedback",
            ((SCREEN_WIDTH // 2) + 50, 100),
            COLORS["title"],
            font=FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

        UI.draw_text(
            self.surface,
            "Quantidade",
            ((SCREEN_WIDTH // 2) + 250, 100),
            COLORS["title"],
            font=FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

        # Pontuação
        UI.draw_text(
            self.surface,
            "Pontuação",
            ((SCREEN_WIDTH // 2) + 50, 130),
            COLORS["title"],
            font=FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )
        UI.draw_text(
            self.surface,
            str(settings.score),
            ((SCREEN_WIDTH // 2) + 250, 130),
            COLORS["title"],
            font=FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

        # Movimentos
        UI.draw_text(
            self.surface,
            "Movimentos",
            ((SCREEN_WIDTH // 2) + 50, 160),
            COLORS["title"],
            font=FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )
        UI.draw_text(
            self.surface,
            str(settings.movimento),
            ((SCREEN_WIDTH // 2) + 250, 160),
            COLORS["title"],
            font=FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

        # Alvos
        UI.draw_text(
            self.surface,
            "Alvos Gerados",
            ((SCREEN_WIDTH // 2) + 50, 190),
            COLORS["title"],
            font=FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )
        UI.draw_text(
            self.surface,
            str(settings.Alvo),
            ((SCREEN_WIDTH // 2) + 250, 190),
            COLORS["title"],
            font=FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

        UI.draw_text(
            self.surface,
            "Alvos Colididos",
            ((SCREEN_WIDTH // 2) + 50, 220),
            COLORS["title"],
            font=FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )
        UI.draw_text(
            self.surface,
            str(settings.Alvo_c),
            ((SCREEN_WIDTH // 2) + 250, 220),
            COLORS["title"],
            font=FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

        UI.draw_text(
            self.surface,
            "Alvos Desviados",
            ((SCREEN_WIDTH // 2) + 50, 250),
            COLORS["title"],
            font=FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )
        UI.draw_text(
            self.surface,
            str(settings.Alvo_d),
            ((SCREEN_WIDTH // 2) + 250, 250),
            COLORS["title"],
            font=FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

        # Obstáculos
        UI.draw_text(
            self.surface,
            "Obst. Gerados",
            ((SCREEN_WIDTH // 2) + 50, 280),
            COLORS["title"],
            font=FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )
        UI.draw_text(
            self.surface,
            str(settings.Obst),
            ((SCREEN_WIDTH // 2) + 250, 280),
            COLORS["title"],
            font=FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

        UI.draw_text(
            self.surface,
            "Obst. Desviados",
            ((SCREEN_WIDTH // 2) + 50, 310),
            COLORS["title"],
            font=FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )
        UI.draw_text(
            self.surface,
            str(settings.Obst_d),
            ((SCREEN_WIDTH // 2) + 250, 310),
            COLORS["title"],
            font=FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

        UI.draw_text(
            self.surface,
            "Obst. Colididos",
            ((SCREEN_WIDTH // 2) + 50, 340),
            COLORS["title"],
            font=FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )
        UI.draw_text(
            self.surface,
            str(settings.Obst_c),
            ((SCREEN_WIDTH // 2) + 250, 340),
            COLORS["title"],
            font=FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

    def _handle_inicial_menu(self):
        """Gerencia o menu inicial (tela principal)."""
        UI.draw_text(
            self.surface,
            GAME_TITLE,
            (SCREEN_WIDTH // 2, 120),
            COLORS["title"],
            font=FONTS["big"],
            shadow=True,
            shadow_color=(255, 255, 255),
            pos_mode="center",
        )

        if UI.button(
            self.surface, 0, 300, "Jogar", click_sound=self.click_sound
        ):
            return "game"

        if UI.button(
            self.surface,
            0,
            300 + BUTTONS_SIZES[1] * 4,
            "Sair",
            click_sound=self.click_sound,
        ):
            pygame.display.quit()
            sys.exit()

        return None

    def _handle_pause_menu(self):
        """Gerencia o menu de pausa."""
        UI.draw_text(
            self.surface,
            "Pause",
            (SCREEN_WIDTH // 2, 120),
            COLORS["title"],
            font=FONTS["big"],
            shadow=True,
            shadow_color=(255, 255, 255),
            pos_mode="center",
        )

        if UI.button(
            self.surface, 0, 300, "Continuar", click_sound=self.click_sound
        ):
            return "game"

        if UI.button(
            self.surface,
            1,
            300 + BUTTONS_SIZES[1] * 2,
            "Retroceder",
            click_sound=self.click_sound,
        ):
            return "prev"

        if UI.button(
            self.surface,
            0,
            300 + BUTTONS_SIZES[1] * 2,
            "Reiniciar",
            click_sound=self.click_sound,
        ):
            return "rest"

        if UI.button(
            self.surface,
            2,
            300 + BUTTONS_SIZES[1] * 2,
            "Avançar",
            click_sound=self.click_sound,
        ):
            return "next"

        if UI.button(
            self.surface,
            0,
            300 + BUTTONS_SIZES[1] * 4,
            "Sair",
            click_sound=self.click_sound,
        ):
            pygame.display.quit()
            sys.exit()

        return None

    def _handle_feedback_menu(self, feedback_type: str):
        """Gerencia as telas de feedback (Feedback_1, Feedback_2, Feedback_3)."""
        if feedback_type == "Feedback_1":
            trofeu = Image.load("Assets/Kartea/trofeu - 25.png")
            Image.draw(self.surface, trofeu, (0, 0))
            action_on_play = "prev"

        elif feedback_type == "Feedback_2":
            trofeu = Image.load("Assets/Kartea/trofeu - 50.png")
            Image.draw(self.surface, trofeu, (0, 0))
            action_on_play = "rest"

        elif feedback_type == "Feedback_3":
            trofeu = Image.load("Assets/Kartea/trofeu - 75.png")
            Image.draw(self.surface, trofeu, (0, 0))
            action_on_play = "next"
        else:
            return None

        self.draw_feedback()

        if UI.button(
            self.surface,
            2,
            300 + BUTTONS_SIZES[1] * 4,
            "Jogar",
            click_sound=self.click_sound,
        ):
            return action_on_play

        if UI.button(
            self.surface,
            1,
            300 + BUTTONS_SIZES[1] * 4,
            "Sair",
            click_sound=self.click_sound,
        ):
            pygame.display.quit()
            sys.exit()

        return None

    def update(self):
        """Atualiza o menu atual e retorna a ação escolhida (game, prev, rest, next, etc.)."""
        self.draw()

        result = None

        if settings.MENU == "Inicial":
            result = self._handle_inicial_menu()

        elif settings.MENU == "Pause":
            result = self._handle_pause_menu()

        elif settings.MENU in ("Feedback_1", "Feedback_2", "Feedback_3"):
            result = self._handle_feedback_menu(settings.MENU)

        return result
