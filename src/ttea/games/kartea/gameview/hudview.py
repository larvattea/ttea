"""Game HUD: score, time, phase and level.

Attributes
----------
TIMER_WARNING_COLOR : tuple[int, int, int]
    Text color when few seconds are left.
TIMER_WARNING_SECONDS : int
    Seconds left below which the warning color is used (5).
SHADOW_COLOR : tuple[int, int, int]
    Color of the text shadow.
MARGIN : int
    Distance (px) from the screen edges.
"""

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from ttea.games.kartea.gameui import UI
    from ttea.games.kartea.gameutil import GameSettings, GameState

TIMER_WARNING_COLOR = (160, 40, 0)
TIMER_WARNING_SECONDS = 5
SHADOW_COLOR = (255, 255, 255)
MARGIN = 5


class HudView:
    """Draw the HUD. Only reads the GameState; changes nothing.

    Parameters
    ----------
    settings : GameSettings
        Game configuration (fonts and colors).
    ui : UI
        Drawing helpers.

    Attributes
    ----------
    settings : GameSettings
        Game configuration.
    ui : UI
        Drawing helpers.
    """

    def __init__(self, settings: "GameSettings", ui: "UI"):
        self.settings = settings
        self.ui = ui

    def draw(
        self, surface: pygame.Surface, state: "GameState", time_left: int
    ) -> None:
        """Draw the HUD, if enabled (``state.hud``).

        Parameters
        ----------
        surface : pygame.Surface
            Game screen.
        state : GameState
            Match state (score, phase, level).
        time_left : int
            Seconds left in the level.

        Notes
        -----
        Score at the top right, time centered, phase and level at the
        top left. Time, phase and level use the warning color when fewer
        than TIMER_WARNING_SECONDS are left. The labels are translated
        with gettext ``_()`` (i18n).
        """
        if not state.hud:
            return

        screen_width = surface.get_width()
        font = self.settings.FONTS["medium"]

        # --- SCORE (5 px from the right edge) ---
        score_text = _("Pontuação : {}").format(state.level_stats.score)
        score_x = screen_width - font.size(score_text)[0] - MARGIN
        self._text(
            surface,
            score_text,
            (score_x, MARGIN),
            self.settings.COLORS["score"],
        )

        # --- TIME (centered on the screen) ---
        timer_text = _("Tempo : {}").format(time_left)
        timer_x = (screen_width - font.size(timer_text)[0]) // 2
        timer_color = (
            TIMER_WARNING_COLOR
            if time_left < TIMER_WARNING_SECONDS
            else self.settings.COLORS["timer"]
        )
        self._text(surface, timer_text, (timer_x, MARGIN), timer_color)

        # --- PHASE AND LEVEL (top left corner) ---
        self._text(
            surface,
            _("Fase : {}").format(state.phase),
            (MARGIN, MARGIN),
            timer_color,
        )
        self._text(
            surface,
            _("Nível : {}").format(state.level),
            (MARGIN, 25),
            timer_color,
        )

    def _text(self, surface, text, pos, color) -> None:
        """Draw a HUD text with the medium font and a shadow."""
        self.ui.draw_text(
            surface,
            text,
            pos,
            color,
            font=self.settings.FONTS["medium"],
            shadow=True,
            shadow_color=SHADOW_COLOR,
        )
