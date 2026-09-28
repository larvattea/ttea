import sys

import pygame

from ttea.games.kartea.gamemodel import Background, Image
from ttea.games.kartea.gameui import UI
from ttea.games.kartea.gameutil import GameSettings


class Menu:
    """Classe responsável por gerenciar todos os menus e telas de feedback do jogo."""

    def __init__(self, surface):
        self.surface = surface
        self.background = Background()
        self.background.background_menu()
        self.click_sound = pygame.mixer.Sound(GameSettings.MENU_CLICK_SOUND)

    def _s(self, value):
        """Escala um valor de pixel definido para a resolução base (800x600)."""
        return int(value * GameSettings.UI_SCALE)

    def _content_area(self):
        """
        Área de conteúdo com o mesmo aspect ratio do design original
        (800x600), escalada uniformemente por UI_SCALE e centralizada na
        tela (letterbox). Usar essa área — em vez de esticar imagens pra
        cobrir a tela toda — evita distorção e mantém qualquer imagem de
        fundo perfeitamente alinhada com textos posicionados via self._s().

        Retorna (origin_x, origin_y, largura, altura).
        """
        content_w = int(GameSettings.BASE_WIDTH * GameSettings.UI_SCALE)
        content_h = int(GameSettings.BASE_HEIGHT * GameSettings.UI_SCALE)
        origin_x = (self.surface.get_width() - content_w) // 2
        origin_y = (self.surface.get_height() - content_h) // 2
        return origin_x, origin_y, content_w, content_h

    def draw(self):
        """Desenha o fundo básico do menu."""
        self.background.draw(self.surface)
        fundo = Image.load(
            GameSettings.MENU_BACKGROUND,
            # size=(GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT),
            size=(self.surface.get_width(), self.surface.get_height()),
        )
        Image.draw(self.surface, fundo, (0, 0))

    def draw_feedback(self):
        """Desenha a tela de feedback com estatísticas do nível."""
        # origin_y alinha o texto com a área de conteúdo (letterbox) da
        # imagem de fundo desenhada em _handle_feedback_menu.
        origin_x_unused, origin_y, content_w_unused, content_h_unused = (
            self._content_area()
        )
        UI.draw_text(
            self.surface,
            _("Feedback"),
            # ((GameSettings.SCREEN_WIDTH // 2) + 50, 100),
            # ((self.surface.get_width() // 2) + 50, 100),
            (
                (self.surface.get_width() // 2) + self._s(50),
                origin_y + self._s(100),
            ),
            GameSettings.COLORS["title"],
            font=GameSettings.FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

        UI.draw_text(
            self.surface,
            _("Quantidade"),
            # ((GameSettings.SCREEN_WIDTH // 2) + 250, 100),
            # ((self.surface.get_width() // 2) + 250, 100),
            (
                (self.surface.get_width() // 2) + self._s(250),
                origin_y + self._s(100),
            ),
            GameSettings.COLORS["title"],
            font=GameSettings.FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

        # Pontuação
        UI.draw_text(
            self.surface,
            _("Pontuação"),
            # ((GameSettings.SCREEN_WIDTH // 2) + 50, 130),
            # ((self.surface.get_width() // 2) + 50, 130),
            (
                (self.surface.get_width() // 2) + self._s(50),
                origin_y + self._s(130),
            ),
            GameSettings.COLORS["title"],
            font=GameSettings.FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )
        UI.draw_text(
            self.surface,
            str(GameSettings.score),
            # ((GameSettings.SCREEN_WIDTH // 2) + 250, 130),
            # ((self.surface.get_width() // 2) + 250, 130),
            (
                (self.surface.get_width() // 2) + self._s(250),
                origin_y + self._s(130),
            ),
            GameSettings.COLORS["title"],
            font=GameSettings.FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

        # Movimentos
        UI.draw_text(
            self.surface,
            _("Movimentos"),
            # ((GameSettings.SCREEN_WIDTH // 2) + 50, 160),
            # ((self.surface.get_width() // 2) + 50, 160),
            (
                (self.surface.get_width() // 2) + self._s(50),
                origin_y + self._s(160),
            ),
            GameSettings.COLORS["title"],
            font=GameSettings.FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )
        UI.draw_text(
            self.surface,
            str(GameSettings.movimento),
            # ((GameSettings.SCREEN_WIDTH // 2) + 250, 160),
            # ((self.surface.get_width() // 2) + 250, 160),
            (
                (self.surface.get_width() // 2) + self._s(250),
                origin_y + self._s(160),
            ),
            GameSettings.COLORS["title"],
            font=GameSettings.FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

        # Alvos
        UI.draw_text(
            self.surface,
            _("Alvos Gerados"),
            # ((GameSettings.SCREEN_WIDTH // 2) + 50, 190),
            # ((self.surface.get_width() // 2) + 50, 190),
            (
                (self.surface.get_width() // 2) + self._s(50),
                origin_y + self._s(190),
            ),
            GameSettings.COLORS["title"],
            font=GameSettings.FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )
        UI.draw_text(
            self.surface,
            str(GameSettings.Alvo),
            # ((GameSettings.SCREEN_WIDTH // 2) + 250, 190),
            # ((self.surface.get_width() // 2) + 250, 190),
            (
                (self.surface.get_width() // 2) + self._s(250),
                origin_y + self._s(190),
            ),
            GameSettings.COLORS["title"],
            font=GameSettings.FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

        UI.draw_text(
            self.surface,
            _("Alvos Colididos"),
            # ((GameSettings.SCREEN_WIDTH // 2) + 50, 220),
            # ((self.surface.get_width() // 2) + 50, 220),
            (
                (self.surface.get_width() // 2) + self._s(50),
                origin_y + self._s(220),
            ),
            GameSettings.COLORS["title"],
            font=GameSettings.FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )
        UI.draw_text(
            self.surface,
            str(GameSettings.Alvo_c),
            # ((GameSettings.SCREEN_WIDTH // 2) + 250, 220),
            # ((self.surface.get_width() // 2) + 250, 220),
            (
                (self.surface.get_width() // 2) + self._s(250),
                origin_y + self._s(220),
            ),
            GameSettings.COLORS["title"],
            font=GameSettings.FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

        UI.draw_text(
            self.surface,
            _("Alvos Desviados"),
            # ((GameSettings.SCREEN_WIDTH // 2) + 50, 250),
            # ((self.surface.get_width() // 2) + 50, 250),
            (
                (self.surface.get_width() // 2) + self._s(50),
                origin_y + self._s(250),
            ),
            GameSettings.COLORS["title"],
            font=GameSettings.FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )
        UI.draw_text(
            self.surface,
            str(GameSettings.Alvo_d),
            # ((GameSettings.SCREEN_WIDTH // 2) + 250, 250),
            # ((self.surface.get_width() // 2) + 250, 250),
            (
                (self.surface.get_width() // 2) + self._s(250),
                origin_y + self._s(250),
            ),
            GameSettings.COLORS["title"],
            font=GameSettings.FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

        # Obstáculos
        UI.draw_text(
            self.surface,
            _("Obst. Gerados"),
            # ((GameSettings.SCREEN_WIDTH // 2) + 50, 280),
            # ((self.surface.get_width() // 2) + 50, 280),
            (
                (self.surface.get_width() // 2) + self._s(50),
                origin_y + self._s(280),
            ),
            GameSettings.COLORS["title"],
            font=GameSettings.FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )
        UI.draw_text(
            self.surface,
            str(GameSettings.Obst),
            # ((GameSettings.SCREEN_WIDTH // 2) + 250, 280),
            # ((self.surface.get_width() // 2) + 250, 280),
            (
                (self.surface.get_width() // 2) + self._s(250),
                origin_y + self._s(280),
            ),
            GameSettings.COLORS["title"],
            font=GameSettings.FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

        UI.draw_text(
            self.surface,
            _("Obst. Desviados"),
            # ((GameSettings.SCREEN_WIDTH // 2) + 50, 310),
            # ((self.surface.get_width() // 2) + 50, 310),
            (
                (self.surface.get_width() // 2) + self._s(50),
                origin_y + self._s(310),
            ),
            GameSettings.COLORS["title"],
            font=GameSettings.FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )
        UI.draw_text(
            self.surface,
            str(GameSettings.Obst_d),
            # ((GameSettings.SCREEN_WIDTH // 2) + 250, 310),
            # ((self.surface.get_width() // 2) + 250, 310),
            (
                (self.surface.get_width() // 2) + self._s(250),
                origin_y + self._s(310),
            ),
            GameSettings.COLORS["title"],
            font=GameSettings.FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

        UI.draw_text(
            self.surface,
            _("Obst. Colididos"),
            # ((GameSettings.SCREEN_WIDTH // 2) + 50, 340),
            # ((self.surface.get_width() // 2) + 50, 340),
            (
                (self.surface.get_width() // 2) + self._s(50),
                origin_y + self._s(340),
            ),
            GameSettings.COLORS["title"],
            font=GameSettings.FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )
        UI.draw_text(
            self.surface,
            str(GameSettings.Obst_c),
            # ((GameSettings.SCREEN_WIDTH // 2) + 250, 340),
            # ((self.surface.get_width() // 2) + 250, 340),
            (
                (self.surface.get_width() // 2) + self._s(250),
                origin_y + self._s(340),
            ),
            GameSettings.COLORS["title"],
            font=GameSettings.FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

    def _handle_inicial_menu(self):
        """Gerencia o menu inicial (tela principal)."""
        UI.draw_text(
            self.surface,
            _(GameSettings.GAME_TITLE),
            # (GameSettings.SCREEN_WIDTH // 2, 120),
            # (self.surface.get_width() // 2, 120),
            (self.surface.get_width() // 2, self._s(120)),
            GameSettings.COLORS["title"],
            font=GameSettings.FONTS["big"],
            shadow=True,
            shadow_color=(255, 255, 255),
            pos_mode="center",
        )

        keys = pygame.key.get_pressed()

        if (
            UI.button(
                self.surface,
                0,
                # 300,
                self._s(300),
                _("Jogar [F2]"),
                click_sound=self.click_sound,
            )
            or keys[pygame.K_F2]
        ):
            return "game"

        if (
            UI.button(
                self.surface,
                0,
                # 300 + GameSettings.BUTTONS_SIZES[1] * 4,
                self._s(300) + GameSettings.BUTTONS_SIZES[1] * 4,
                _("Sair [F7]"),
                click_sound=self.click_sound,
            )
            or keys[pygame.K_F7]
        ):
            pygame.display.quit()
            sys.exit()

        return None

    def _handle_pause_menu(self):
        """Gerencia o menu de pausa."""
        UI.draw_text(
            self.surface,
            _("Pause"),
            # (GameSettings.SCREEN_WIDTH // 2, 120),
            # (self.surface.get_width() // 2, 120),
            (self.surface.get_width() // 2, self._s(120)),
            GameSettings.COLORS["title"],
            font=GameSettings.FONTS["big"],
            shadow=True,
            shadow_color=(255, 255, 255),
            pos_mode="center",
        )

        keys = pygame.key.get_pressed()
        if (
            UI.button(
                self.surface,
                0,
                # 300,
                self._s(300),
                _("Continuar [F3]"),
                click_sound=self.click_sound,
            )
            or keys[pygame.K_F3]
        ):
            return "game"

        if (
            UI.button(
                self.surface,
                1,
                # 300 + GameSettings.BUTTONS_SIZES[1] * 2,
                self._s(300) + GameSettings.BUTTONS_SIZES[1] * 2,
                _("Retroceder [F4]"),
                click_sound=self.click_sound,
            )
            or keys[pygame.K_F4]
        ):
            return "prev"

        if (
            UI.button(
                self.surface,
                0,
                # 300 + GameSettings.BUTTONS_SIZES[1] * 2,
                self._s(300) + GameSettings.BUTTONS_SIZES[1] * 2,
                _("Reiniciar [F5]"),
                click_sound=self.click_sound,
            )
            or keys[pygame.K_F5]
        ):
            return "rest"

        if (
            UI.button(
                self.surface,
                2,
                # 300 + GameSettings.BUTTONS_SIZES[1] * 2,
                self._s(300) + GameSettings.BUTTONS_SIZES[1] * 2,
                _("Avançar [F6]"),
                click_sound=self.click_sound,
            )
            or keys[pygame.K_F6]
        ):
            return "next"

        if (
            UI.button(
                self.surface,
                0,
                # 300 + GameSettings.BUTTONS_SIZES[1] * 4,
                self._s(300) + GameSettings.BUTTONS_SIZES[1] * 4,
                _("Sair [F7]"),
                click_sound=self.click_sound,
            )
            or keys[pygame.K_F7]
        ):
            pygame.display.quit()
            sys.exit()

        return None

    def _handle_feedback_menu(self, feedback_type: str):
        """Gerencia as telas de feedback (Feedback_1, Feedback_2, Feedback_3)."""
        origin_x, origin_y, content_w, content_h = self._content_area()
        content_size = (content_w, content_h)

        if feedback_type == "Feedback_1":
            trofeu = Image.load(
                GameSettings.MENU_FEEDBACK_25, size=content_size
            )
            action_on_play = "prev"
        elif feedback_type == "Feedback_2":
            trofeu = Image.load(
                GameSettings.MENU_FEEDBACK_50, size=content_size
            )
            action_on_play = "rest"
        elif feedback_type == "Feedback_3":
            trofeu = Image.load(
                GameSettings.MENU_FEEDBACK_75, size=content_size
            )
            action_on_play = "next"
        else:
            return None

        Image.draw(self.surface, trofeu, (origin_x, origin_y))

        self.draw_feedback()

        keys = pygame.key.get_pressed()

        if (
            UI.button(
                self.surface,
                1,
                # 300 + GameSettings.BUTTONS_SIZES[1] * 4,
                self._s(300) + GameSettings.BUTTONS_SIZES[1] * 4,
                _("Jogar [F2]"),
                click_sound=self.click_sound,
            )
            or keys[pygame.K_F2]
        ):
            return action_on_play

        if (
            UI.button(
                self.surface,
                2,
                # 300 + GameSettings.BUTTONS_SIZES[1] * 4,
                self._s(300) + GameSettings.BUTTONS_SIZES[1] * 4,
                _("Sair [F7]"),
                click_sound=self.click_sound,
            )
            or keys[pygame.K_F7]
        ):
            pygame.display.quit()
            sys.exit()

        return None

    def update(self):
        """Atualiza o menu atual e retorna a ação escolhida (game, prev, rest, next, etc.)."""
        self.draw()

        result = None

        if GameSettings.MENU == "Inicial":
            result = self._handle_inicial_menu()

        elif GameSettings.MENU == "Pause":
            result = self._handle_pause_menu()

        elif GameSettings.MENU in ("Feedback_1", "Feedback_2", "Feedback_3"):
            result = self._handle_feedback_menu(GameSettings.MENU)

        return result
