"""Segment (line) of the KarTEA pseudo-3D road."""

from typing import TYPE_CHECKING

import pygame

from ttea.games.kartea.gameutil.alphablit import alpha_blit

if TYPE_CHECKING:
    from ttea.games.kartea.gamemodel import Target
    from ttea.games.kartea.gameutil import GameSettings


class Line:
    """Line (segment) of the road in the pseudo-3D system.

    Parameters
    ----------
    settings : GameSettings
        Game configuration (injected).

    Attributes
    ----------
    TARGET_X_BY_ROAD : dict[int, float], class attribute
        Lateral position of a target/obstacle by lane (0 left, 1
        middle).
    TARGET_X_RIGHT : float, class attribute
        Lateral position for any other lane (right).
    settings : GameSettings
        Game configuration.
    x, y, z : float
        3D position of the line.
    screen_x, screen_y, screen_w : float
        Projected 2D position and half width of the road on screen.
    scale : float
        Projection scale.
    curve : float
        Road curvature at this line.
    clip : float
        Screen y below which sprites of this line are hidden (terrain in
        front).
    passed : bool
        True after the camera has gone past this line (set by
        Background); used to detect the finish line crossing even when
        the road advances several segments per frame.
    sprite_x : float
        Lateral offset of the left side sprite (tree).
    sprite : pygame.Surface | None
        Left side sprite.
    sprite_rect : pygame.Rect | None
        Rect of the left side sprite.
    sprite2_x : float
        Lateral offset of the right side sprite (tree).
    sprite2 : pygame.Surface | None
        Right side sprite.
    sprite2_rect : pygame.Rect | None
        Rect of the right side sprite.
    target_x : float
        Lateral offset of the target/obstacle.
    target : Target | None
        Target/obstacle on this line.
    target_rect : pygame.Rect | None
        Rect of the target/obstacle.
    grass_color, rumble_color, road_color, div_color : pygame.Color
        Colors of the line, set by Background when the road is created.
    """

    def __init__(self, settings: "GameSettings"):
        self.settings = settings

        # 3D position
        self.x: float = 0.0
        self.y: float = 0.0
        self.z: float = 0.0

        # Projected 2D position
        self.screen_x: float = 0.0
        self.screen_y: float = 0.0
        self.screen_w: float = 0.0

        self.scale: float = 0.0
        self.curve: float = 0.0
        self.clip: float = 0.0

        self.passed: bool = False

        # Left side sprite (tree)
        self.sprite_x: float = 0.0
        self.sprite: pygame.Surface | None = None
        self.sprite_rect: pygame.Rect | None = None

        # Right side sprite (tree)
        self.sprite2_x: float = 0.0
        self.sprite2: pygame.Surface | None = None
        self.sprite2_rect: pygame.Rect | None = None

        # Target / obstacle
        self.target_x: float = 0.0
        self.target: Target | None = None
        self.target_rect: pygame.Rect | None = None

    def project(self, cam_x: float, cam_y: float, cam_z: float):
        """Project the 3D position to 2D screen coordinates.

        Parameters
        ----------
        cam_x, cam_y, cam_z : float
            Camera position.

        Notes
        -----
        Updates ``scale``, ``screen_x``, ``screen_y`` and ``screen_w``.
        Must only be called for lines in front of the camera (``z >
        cam_z``).
        """
        self.scale = self.settings.CAMERA_DEPTH / (self.z - cam_z)
        self.screen_x = (
            (1 + self.scale * (self.x - cam_x))
            * self.settings.SCREEN_WIDTH
            / 2
        )
        self.screen_y = (
            (1 - self.scale * (self.y - cam_y))
            * self.settings.SCREEN_HEIGHT
            / 5
        )
        self.screen_w = (
            self.scale
            * self.settings.ROAD_WIDTH
            * self.settings.SCREEN_WIDTH
            / 2
        )

    def draw_sprite(self, draw_surface: pygame.Surface):
        """Draw the left side sprite (left tree).

        Parameters
        ----------
        draw_surface : pygame.Surface
            Surface drawn on.
        """
        self._draw_side_sprite(draw_surface, self.sprite, self.sprite_x)

    def draw_sprite2(self, draw_surface: pygame.Surface):
        """Draw the right side sprite (right tree).

        Parameters
        ----------
        draw_surface : pygame.Surface
            Surface drawn on.
        """
        self._draw_side_sprite(draw_surface, self.sprite2, self.sprite2_x)

    TARGET_X_BY_ROAD = {0: -2.25, 1: -0.5}
    TARGET_X_RIGHT = 1.25

    def _project(self, sprite: pygame.Surface, offset_x: float):
        """Project a sprite on this line of the road.

        Parameters
        ----------
        sprite : pygame.Surface
            Image at its original size.
        offset_x : float
            Lateral position relative to the road center.

        Returns
        -------
        tuple
            ``(dest_x, dest_y, dest_w, dest_h, hidden)``: rectangle on
            screen and whether the sprite is fully hidden by the terrain
            in front (``self.clip``).
        """
        dest_w = sprite.get_width() * self.screen_w / 266
        dest_h = sprite.get_height() * self.screen_w / 266
        dest_x = (
            self.screen_x
            + self.scale * offset_x * self.settings.SCREEN_WIDTH / 2
            + dest_w * offset_x
        )
        dest_y = self.screen_y + 4 - dest_h

        # Only hide the part of the sprite below self.clip
        clip_h = max(0, dest_y + dest_h - self.clip)
        return dest_x, dest_y, dest_w, dest_h, clip_h >= dest_h

    def _draw_projected(
        self,
        draw_surface: pygame.Surface,
        sprite: pygame.Surface,
        offset_x: float,
        max_scale: float,
        target: "Target | None" = None,
    ) -> bool:
        """Project and draw a sprite; return True if it was drawn.

        ``max_scale`` limits the size on screen (relative to the
        original image). With ``target``, the projected position is
        passed to it (``define_pos``) even when the sprite is not drawn.
        """
        dest_x, dest_y, dest_w, dest_h, hidden = self._project(
            sprite, offset_x
        )
        if target is not None:
            target.define_pos(dest_x, dest_y)
        if hidden or dest_w > max_scale * sprite.get_width():
            return False
        scaled_sprite = pygame.transform.scale(sprite, (dest_w, dest_h))
        alpha_blit(draw_surface, scaled_sprite, (dest_x, dest_y))
        return True

    def _draw_side_sprite(
        self,
        draw_surface: pygame.Surface,
        sprite: pygame.Surface | None,
        offset_x: float,
    ):
        """Draw a side sprite (tree) projected on this line.

        Clipping uses the same rule as draw_target (see _project): only
        the part of the sprite below ``self.clip`` (terrain in front) is
        hidden.
        """
        if sprite is not None:
            self._draw_projected(draw_surface, sprite, offset_x, max_scale=2)

    def draw_target(self, draw_surface: pygame.Surface):
        """Draw the target or obstacle attached to this line.

        Parameters
        ----------
        draw_surface : pygame.Surface
            Surface drawn on.

        Notes
        -----
        The lateral position comes from the target lane
        (TARGET_X_BY_ROAD). The hitbox is drawn too when ``DRAW_HITBOX``
        is on.
        """
        if self.target is None:
            return

        self.target_x = self.TARGET_X_BY_ROAD.get(
            self.target.current_road, self.TARGET_X_RIGHT
        )
        drawn = self._draw_projected(
            draw_surface,
            self.target.images[0],
            self.target_x,
            max_scale=1.5,
            target=self.target,
        )

        if drawn and self.settings.DRAW_HITBOX:
            self.target.draw_hitbox(draw_surface)
