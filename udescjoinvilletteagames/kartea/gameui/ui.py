import pygame

from udescjoinvilletteagames.kartea.gameutil import GameSettings


class UI:
    """
    Classe responsável por desenhar elementos de interface (texto e botões).
    Usa as configurações globais da classe GameSettings.
    """

    UI_POS_TOP_LEFT = "top_left"
    UI_POS_CENTER = "center"

    def __init__(self, settings: GameSettings = None):
        self.settings = settings or GameSettings()

    def draw_text(
        self,
        surface: pygame.Surface,
        text: str,
        pos: tuple,
        color: tuple,
        font=None,
        pos_mode: str = UI_POS_TOP_LEFT,
        shadow: bool = False,
        shadow_color: tuple = (0, 0, 0),
        shadow_offset: int = 2,
    ):
        """Desenha texto com suporte a sombra."""
        if font is None:
            font = self.settings.FONTS["medium"]

        label = font.render(text, True, color)
        label_rect = label.get_rect()

        if pos_mode == UI.UI_POS_TOP_LEFT:
            label_rect.topleft = pos
        elif pos_mode == UI.UI_POS_CENTER:
            label_rect.center = pos

        if shadow:
            shadow_label = font.render(text, True, shadow_color)
            surface.blit(
                shadow_label,
                (label_rect.x - shadow_offset, label_rect.y + shadow_offset),
            )

        surface.blit(label, label_rect)

    def button(
        self,
        surface: pygame.Surface,
        pos_x: int,  # 1 = esquerda, 2 = direita, outro = centro
        pos_y: int,
        text: str = None,
        click_sound=None,
    ) -> bool:
        """Desenha um botão e retorna True se foi clicado."""

        if pos_x == 1:  # esquerda
            rect = pygame.Rect(
                (
                    self.settings.SCREEN_WIDTH // 4
                    - self.settings.BUTTONS_SIZES[0] // 2,
                    pos_y,
                ),
                self.settings.BUTTONS_SIZES,
            )
        elif pos_x == 2:  # direita
            rect = pygame.Rect(
                (
                    3 * self.settings.SCREEN_WIDTH // 4
                    - self.settings.BUTTONS_SIZES[0] // 2,
                    pos_y,
                ),
                self.settings.BUTTONS_SIZES,
            )
        else:  # centro
            rect = pygame.Rect(
                (
                    self.settings.SCREEN_WIDTH // 2
                    - self.settings.BUTTONS_SIZES[0] // 2,
                    pos_y,
                ),
                self.settings.BUTTONS_SIZES,
            )

        # Hover effect
        mouse_pos = pygame.mouse.get_pos()
        on_button = rect.collidepoint(mouse_pos)
        color = (
            self.settings.COLORS["buttons"]["second"]
            if on_button
            else self.settings.COLORS["buttons"]["default"]
        )

        # Sombra do botão
        pygame.draw.rect(
            surface,
            self.settings.COLORS["buttons"]["shadow"],
            (rect.x - 6, rect.y - 6, rect.w, rect.h),
        )

        # Botão principal
        pygame.draw.rect(surface, color, rect)

        # Texto do botão
        if text is not None:
            self.draw_text(
                surface,
                text,
                rect.center,
                self.settings.COLORS["buttons"]["text"],
                pos_mode=self.UI_POS_CENTER,
                shadow=True,
                shadow_color=self.settings.COLORS["buttons"]["shadow"],
            )

        # Clique
        if on_button and pygame.mouse.get_pressed()[0]:
            if click_sound is not None:
                click_sound.play()
            return True

        return False
