"""Text and button drawing for the KarTEA game screens (pygame side).

The ``UI`` class is used by the menus and the HUD to draw text, buttons
that the player can trigger with the mouse or with the feet, and the
marker that shows where the feet are.
"""

import time
from typing import TYPE_CHECKING

import pygame

from ttea.games.kartea.gameutil.alphablit import alpha_blit

if TYPE_CHECKING:
    from ttea.games.kartea.gameutil import GameSettings


class UI:
    """Draw text and buttons on the game interface.

    Buttons can be triggered by the mouse or by the player's feet
    (``feet_pos`` in ``button``): with the feet, the player has to stand
    still on the button for ``GameSettings.FEET_CLICK_TIME`` seconds
    while the button fills up.

    Parameters
    ----------
    settings : GameSettings
        Game settings (fonts, colors, sizes), injected by the caller.

    Attributes
    ----------
    settings : GameSettings
        The injected game settings.
    CLICK_MOUSE : str, class attribute
        Source returned by ``button`` when the mouse clicked it
        (``"mouse"``).
    CLICK_FEET : str, class attribute
        Source returned by ``button`` when the feet confirmed it
        (``"feet"``).

    See Also
    --------
    Menu : Menus built from these buttons.
    """

    CLICK_MOUSE = "mouse"
    CLICK_FEET = "feet"

    def __init__(self, settings: "GameSettings"):
        self.settings = settings
        # Button being selected with the feet: button key, start of
        # the count and last instant the feet were on it.
        self._feet_selection = {"key": None, "start": 0.0, "seen": 0.0}

    def reset_feet_selection(self) -> None:
        """Cancel the feet selection in progress."""
        self._feet_selection["key"] = None

    def draw_player_marker(
        self,
        surface: pygame.Surface,
        pos: tuple | None,
        radius: int | None = None,
    ) -> None:
        """Draw the dot at the position of the player's feet.

        Parameters
        ----------
        surface : pygame.Surface
            Surface to draw on.
        pos : tuple | None
            Position (x, y) on the screen; None (player not detected)
            draws nothing.
        radius : int | None, optional
            Radius in pixels. Defaults to
            ``GameSettings.FEET_MARKER_RADIUS`` (already scaled).

        Notes
        -----
        The dot is clamped so it stays entirely on the screen, and it
        gets a border (``FEET_MARKER_BORDER_COLOR``, width ``radius //
        6``, at least 1 px) so it remains visible over light
        backgrounds.
        """
        if pos is None:
            return
        settings = self.settings
        if radius is None:
            radius = settings.FEET_MARKER_RADIUS
        width, height = surface.get_size()
        # Keep the whole dot on the screen, even with the feet slightly
        # outside the calibrated area.
        x = max(radius, min(width - radius, int(pos[0])))
        y = max(radius, min(height - radius, int(pos[1])))
        pygame.draw.circle(surface, settings.FEET_MARKER_COLOR, (x, y), radius)
        pygame.draw.circle(
            surface,
            settings.FEET_MARKER_BORDER_COLOR,
            (x, y),
            radius,
            width=max(1, radius // 6),
        )

    def draw_text(
        self,
        surface: pygame.Surface,
        text: str,
        pos: tuple,
        color: tuple,
        font=None,
        pos_mode: str = "top_left",
        shadow: bool = False,
        shadow_color: tuple = (0, 0, 0),
        shadow_offset: int = 2,
    ):
        """Draw text on the surface, optionally with a shadow.

        Parameters
        ----------
        surface : pygame.Surface
            Surface to draw on.
        text : str
            Text to render.
        pos : tuple
            Position (x, y), interpreted according to ``pos_mode``.
        color : tuple
            Text color.
        font : pygame.font.Font, optional
            Font to use. Defaults to ``GameSettings.FONTS["medium"]``.
        pos_mode : str, optional
            ``"top_left"`` (default) or ``"center"``: which point of the
            text ``pos`` refers to. Any other value leaves the text at
            (0, 0).
        shadow : bool, optional
            Whether to draw a shadow under the text. Defaults to False.
        shadow_color : tuple, optional
            Shadow color. Defaults to black.
        shadow_offset : int, optional
            Shadow offset in pixels, to the left and down. Defaults to
            2.
        """
        if font is None:
            font = self.settings.FONTS["medium"]
        label = font.render(text, True, color)
        label_rect = label.get_rect()

        if pos_mode == "top_left":
            label_rect.x, label_rect.y = pos
        elif pos_mode == "center":
            label_rect.center = pos

        if shadow:
            label_shadow = font.render(text, True, shadow_color)
            alpha_blit(
                surface,
                label_shadow,
                (label_rect.x - shadow_offset, label_rect.y + shadow_offset),
            )

        alpha_blit(surface, label, label_rect)

    def button(
        self,
        surface: pygame.Surface,
        pos_x: int,
        pos_y: int,
        text: str | None = None,
        click_sound: pygame.mixer.Sound | None = None,
        feet_pos: tuple | None = None,
    ) -> str | None:
        """Draw a button and report whether it was triggered this frame.

        With ``feet_pos``, the player's feet can also trigger the
        button: the player has to stand still on it for
        ``FEET_CLICK_TIME`` seconds. While counting, the button fills
        up, so the player sees it is being selected and can step off
        before it is confirmed.

        Parameters
        ----------
        surface : pygame.Surface
            Surface to draw on.
        pos_x : int
            Horizontal position: 1 left quarter, 2 right quarter, any
            other value (usually 0) center.
        pos_y : int
            Y position of the top of the button.
        text : str | None, optional
            Text of the button. Defaults to no text.
        click_sound : pygame.mixer.Sound | None, optional
            Sound played when the button is triggered.
        feet_pos : tuple | None, optional
            Position (x, y) of the feet on the screen; None disables the
            feet selection.

        Returns
        -------
        str | None
            ``UI.CLICK_MOUSE`` or ``UI.CLICK_FEET`` if the button was
            triggered this frame (both truthy in an ``if``); None
            otherwise.

        Notes
        -----
        - The button size is ``GameSettings.BUTTONS_SIZES`` and it is
          highlighted (``"second"`` color) while the mouse or the feet
          are on it.
        - The mouse triggers the button while the left button is pressed
          over it; this takes precedence over the feet.
        - Once the feet count starts, the button "grows"
          ``FEET_CLICK_MARGIN`` px and stepping off for less than
          ``FEET_CLICK_EXIT_TOLERANCE`` s does not cancel the selection
          (pose tracking jitters a few pixels).
        - A button is identified by ``(pos_x, pos_y, text)``; only one
          button can be selected with the feet at a time.
        """
        settings = self.settings
        if pos_x == 1:  # left
            rect = pygame.Rect(
                (
                    settings.SCREEN_WIDTH // 4
                    - settings.BUTTONS_SIZES[0] // 2,
                    pos_y,
                ),
                settings.BUTTONS_SIZES,
            )
        elif pos_x == 2:  # right
            rect = pygame.Rect(
                (
                    3 * settings.SCREEN_WIDTH // 4
                    - settings.BUTTONS_SIZES[0] // 2,
                    pos_y,
                ),
                settings.BUTTONS_SIZES,
            )
        else:  # center (default)
            rect = pygame.Rect(
                (
                    settings.SCREEN_WIDTH // 2
                    - settings.BUTTONS_SIZES[0] // 2,
                    pos_y,
                ),
                settings.BUTTONS_SIZES,
            )

        mouse_on_button = rect.collidepoint(pygame.mouse.get_pos())

        # Feet selection
        progress, feet_confirmed = self._update_feet_selection(
            (pos_x, pos_y, text), rect, feet_pos
        )
        feet_selecting = self._feet_selection["key"] == (pos_x, pos_y, text)

        color = (
            settings.COLORS["buttons"]["second"]
            if mouse_on_button or feet_selecting or feet_confirmed
            else settings.COLORS["buttons"]["default"]
        )

        pygame.draw.rect(
            surface,
            settings.COLORS["buttons"]["shadow"],
            (rect.x - 6, rect.y - 6, rect.w, rect.h),
        )

        pygame.draw.rect(surface, color, rect)

        # Fill bar showing the progress of the feet selection
        if progress > 0:
            pygame.draw.rect(
                surface,
                settings.COLORS["buttons"]["shadow"],
                (rect.x, rect.y, int(rect.w * progress), rect.h),
            )

        if text is not None:
            self.draw_text(
                surface,
                text,
                rect.center,
                settings.COLORS["buttons"]["text"],
                pos_mode="center",
                shadow=True,
                shadow_color=settings.COLORS["buttons"]["shadow"],
            )

        source = None
        if mouse_on_button and pygame.mouse.get_pressed()[0]:
            source = self.CLICK_MOUSE
        elif feet_confirmed:
            source = self.CLICK_FEET

        if source is not None and click_sound is not None:
            click_sound.play()
        return source

    def _update_feet_selection(
        self, key: tuple, rect: pygame.Rect, feet_pos: tuple | None
    ) -> tuple[float, bool]:
        """Advance the feet selection of the button ``key``.

        Parameters
        ----------
        key : tuple
            Identifier of the button, ``(pos_x, pos_y, text)``.
        rect : pygame.Rect
            Area of the button on the screen.
        feet_pos : tuple | None
            Position (x, y) of the feet, or None if not detected.

        Returns
        -------
        tuple[float, bool]
            Progress from 0 to 1, and True if the selection was
            confirmed in this frame.

        Notes
        -----
        A selection not seen for more than ``FEET_CLICK_EXIT_TOLERANCE``
        s (feet off the button, or the menu not drawn for a while)
        starts over, so it never confirms immediately when the menu
        comes back. It only confirms with the feet on the button in the
        current frame.
        """
        settings = self.settings
        selection = self._feet_selection
        now = time.monotonic()
        selecting = selection["key"] == key

        # Stale selection (see Notes): start over.
        if (
            selecting
            and now - selection["seen"] > settings.FEET_CLICK_EXIT_TOLERANCE
        ):
            selection["key"] = None
            selecting = False

        on_area = False
        if feet_pos is not None:
            area = (
                rect.inflate(
                    2 * settings.FEET_CLICK_MARGIN,
                    2 * settings.FEET_CLICK_MARGIN,
                )
                if selecting
                else rect
            )
            on_area = area.collidepoint(feet_pos)
        if on_area:
            if not selecting:
                selection["key"] = key
                selection["start"] = now
                selecting = True
            selection["seen"] = now

        if not selecting:
            return 0.0, False

        progress = min(
            (now - selection["start"]) / settings.FEET_CLICK_TIME, 1.0
        )
        # During the exit tolerance the count goes on, but it only
        # fires with the feet on the button in this frame.
        if progress >= 1.0 and on_area:
            selection["key"] = None
            return 1.0, True
        return progress, False
