"""Menus and feedback screens of the KarTEA game (pygame)."""

from typing import TYPE_CHECKING

import pygame

from ttea.games.kartea.gamemodel import Background, Image, Sound
from ttea.games.kartea.gameui import UI

if TYPE_CHECKING:
    from ttea.games.kartea.gameutil import GameSettings, GameState


class Menu:
    """Manage all menus and feedback screens of the game.

    Reads from the GameState which screen to show (``state.menu``) and
    the level counters (``state.level_stats``); it does not change the
    state.

    With feet click on (``state.feet_click``), ``update`` receives the
    feet position: the buttons are also triggered by the feet and the
    feet dot is drawn on top of everything. ``selected_by_feet`` tells
    whether the last action came from the feet.

    Parameters
    ----------
    surface : pygame.Surface
        Game screen.
    settings : GameSettings
        Game configuration.
    state : GameState
        Match state.

    Attributes
    ----------
    surface : pygame.Surface
        Game screen.
    settings : GameSettings
        Game configuration.
    state : GameState
        Match state.
    ui : UI
        Drawing helpers (buttons, texts, feet dot).
    background : Background
        Road background with the menu image.
    click_sound : pygame.mixer.Sound
        Menu click sound.
    feet_pos : tuple | None
        Feet position in the current frame (None: feet selection off or
        player not detected).
    selected_by_feet : bool
        True if the action returned by the last ``update`` came from the
        feet.

    Notes
    -----
    All texts are translated with gettext ``_()`` (i18n).
    """

    def __init__(self, surface, settings: "GameSettings", state: "GameState"):
        self.surface = surface
        self.settings = settings
        self.state = state
        self.ui = UI(settings)
        self.background = Background(settings)
        self.background.background_menu()
        self.click_sound = Sound.load(settings.MENU_CLICK_SOUND)
        self.feet_pos = None
        self.selected_by_feet = False

    def _s(self, value):
        """Scale a value in pixels of the base resolution (800x600)."""
        return int(value * self.settings.UI_SCALE)

    def _content_area(self):
        """Return the content area of the menu.

        The area keeps the aspect ratio of the original design
        (800x600), scaled uniformly by UI_SCALE and centered on the
        screen (letterbox). Using this area, instead of stretching
        images to cover the whole screen, avoids distortion and keeps
        any background image aligned with texts positioned with
        ``_s()``.

        Returns
        -------
        tuple[int, int, int, int]
            ``(origin_x, origin_y, width, height)``.
        """
        content_w = int(self.settings.BASE_WIDTH * self.settings.UI_SCALE)
        content_h = int(self.settings.BASE_HEIGHT * self.settings.UI_SCALE)
        origin_x = (self.surface.get_width() - content_w) // 2
        origin_y = (self.surface.get_height() - content_h) // 2
        return origin_x, origin_y, content_w, content_h

    def draw(self):
        """Draw the basic menu background."""
        self.background.draw(self.surface)
        background_image = Image.load(
            self.settings.MENU_BACKGROUND,
            size=(self.surface.get_width(), self.surface.get_height()),
        )
        Image.draw(self.surface, background_image, (0, 0))

    def _draw_label(self, text, pos, font="medium", pos_mode="top_left"):
        """Draw a text in the menu style (title color, white shadow)."""
        self.ui.draw_text(
            self.surface,
            text,
            pos,
            self.settings.COLORS["title"],
            font=self.settings.FONTS[font],
            shadow=True,
            shadow_color=(255, 255, 255),
            pos_mode=pos_mode,
        )

    def _draw_title(self, text):
        """Draw a title centered at the top of the menu."""
        self._draw_label(
            text,
            (self.surface.get_width() // 2, self._s(120)),
            font="big",
            pos_mode="center",
        )

    def _buttons(self, buttons):
        """Draw the buttons; return the action of the first triggered.

        All buttons are drawn every frame (the feet selection depends on
        it to keep counting). If the action came from the feet,
        ``selected_by_feet`` becomes True.

        Parameters
        ----------
        buttons : list[tuple]
            (column, row, text, key, action). The row is measured in
            button heights below y=300 (800x600 base).

        Returns
        -------
        str | None
            Action of the clicked button (or of the pressed key).
        """
        keys = pygame.key.get_pressed()
        button_h = self.settings.BUTTONS_SIZES[1]
        result = None
        for column, row, text, key, action in buttons:
            source = self.ui.button(
                self.surface,
                column,
                self._s(300) + button_h * row,
                text,
                click_sound=self.click_sound,
                feet_pos=self.feet_pos,
            )
            if result is None and (source or keys[key]):
                result = action
                self.selected_by_feet = source == UI.CLICK_FEET
        return result

    def draw_feedback(self):
        """Draw the feedback screen with the level statistics.

        One (label, value) row every 30 px from y=100, aligned with the
        content area of the background image.
        """
        # origin_y aligns the text with the content area (letterbox) of
        # the background image drawn in _handle_feedback_menu.
        _origin_x, origin_y, _content_w, _content_h = self._content_area()
        stats = self.state.level_stats

        rows = [
            (_("Feedback"), _("Quantidade")),
            (_("Pontuação"), stats.score),
            (_("Movimentos"), stats.movement),
            (_("Alvos Gerados"), stats.targets),
            (_("Alvos Colididos"), stats.targets_collided),
            (_("Alvos Desviados"), stats.targets_avoided),
            (_("Obst. Gerados"), stats.obstacles),
            (_("Obst. Desviados"), stats.obstacles_avoided),
            (_("Obst. Colididos"), stats.obstacles_collided),
        ]
        center_x = self.surface.get_width() // 2
        for index, (label, value) in enumerate(rows):
            y = origin_y + self._s(100 + 30 * index)
            self._draw_label(label, (center_x + self._s(50), y))
            self._draw_label(str(value), (center_x + self._s(250), y))

    def draw_player_name(self):
        """Draw the player's first name centered under the trophy.

        The trophy of the feedback images is centered at x=200 and ends
        near y=400 (800x600 base), so the name is centered at (200, 430)
        of the content area. Nothing is drawn without a name.
        """
        name = self.state.player_name
        if not name:
            return
        origin_x, origin_y, _content_w, _content_h = self._content_area()
        self._draw_label(
            name,
            (origin_x + self._s(200), origin_y + self._s(430)),
            font="medium",
            pos_mode="center",
        )

    def _handle_initial_menu(self):
        """Handle the start menu (main screen).

        Returns
        -------
        str | None
            "game" (F2) or "exit" (F7); main records the exit in the
            session and ends the game.
        """
        self._draw_title(_(self.settings.GAME_TITLE))
        # main records the exit ("exit") in the session and ends the
        # game
        return self._buttons(
            [
                (0, 0, _("Jogar [F2]"), pygame.K_F2, "game"),
                (0, 4, _("Sair [F7]"), pygame.K_F7, "exit"),
            ]
        )

    def _handle_pause_menu(self):
        """Handle the pause menu.

        Returns
        -------
        str | None
            "game" (F3), "prev" (F4), "rest" (F5), "next" (F6) or "exit"
            (F7).
        """
        self._draw_title(_("Pause"))
        return self._buttons(
            [
                (0, 0, _("Continuar [F3]"), pygame.K_F3, "game"),
                (1, 2, _("Retroceder [F4]"), pygame.K_F4, "prev"),
                (0, 2, _("Reiniciar [F5]"), pygame.K_F5, "rest"),
                (2, 2, _("Avançar [F6]"), pygame.K_F6, "next"),
                (0, 4, _("Sair [F7]"), pygame.K_F7, "exit"),
            ]
        )

    def _handle_feedback_menu(self, feedback_type: str):
        """Handle the feedback screens (Feedback_1, _2 and _3).

        Parameters
        ----------
        feedback_type : str
            "Feedback_1" (25% trophy), "Feedback_2" (50%) or
            "Feedback_3" (75%).

        Returns
        -------
        str | None
            "play" (F2) or "exit" (F7); None for an unknown type.

        Notes
        -----
        - The player's first name is drawn under the trophy
          (``draw_player_name``), followed by the level statistics
          (``draw_feedback``).
        - "play" only starts the next level: it was already set at the
          end of the level (GameController).
        """
        image_path = {
            "Feedback_1": self.settings.MENU_FEEDBACK_25,
            "Feedback_2": self.settings.MENU_FEEDBACK_50,
            "Feedback_3": self.settings.MENU_FEEDBACK_75,
        }.get(feedback_type)
        if image_path is None:
            return None

        origin_x, origin_y, content_w, content_h = self._content_area()
        trophy = Image.load(image_path, size=(content_w, content_h))
        Image.draw(self.surface, trophy, (origin_x, origin_y))

        self.draw_player_name()
        self.draw_feedback()

        # "exit": main records the exit.
        return self._buttons(
            [
                (1, 4, _("Jogar [F2]"), pygame.K_F2, "play"),
                (2, 4, _("Sair [F7]"), pygame.K_F7, "exit"),
            ]
        )

    def update(self, feet_pos: tuple | None = None):
        """Update the current menu and return the chosen action.

        Actions: "game" (play/continue), "prev", "rest", "next" (pause
        menu), "play" (feedback screen: starts the level already
        defined) and "exit". ``selected_by_feet`` tells whether the
        action came from the feet.

        Parameters
        ----------
        feet_pos : tuple | None, optional
            Feet (x, y) position on screen, when feet click is on
            (``state.feet_click``). None: mouse/keyboard only.

        Returns
        -------
        str | None
            The chosen action, or None.
        """
        self.feet_pos = feet_pos if self.state.feet_click else None
        self.selected_by_feet = False
        self.draw()

        result = None

        if self.state.menu == "Inicial":
            result = self._handle_initial_menu()

        elif self.state.menu == "Pause":
            result = self._handle_pause_menu()

        elif self.state.menu in ("Feedback_1", "Feedback_2", "Feedback_3"):
            result = self._handle_feedback_menu(self.state.menu)

        # Feet dot on top of the buttons: without it the player cannot
        # tell where they are "pointing".
        if self.state.feet_click:
            self.ui.draw_player_marker(self.surface, self.feet_pos)

        return result
