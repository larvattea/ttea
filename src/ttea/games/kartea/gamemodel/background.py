"""Rendering of the KarTEA horizon, pseudo-3D road and sprites."""

import time
from typing import TYPE_CHECKING

import pygame

from ttea.games.kartea.gametheme import KarTEATheme

from .image import Image
from .line import Line

if TYPE_CHECKING:
    from ttea.games.kartea.gameutil import GameSettings


class Background:
    """Render the game background, road and sprites.

    Parameters
    ----------
    settings : GameSettings
        Game configuration (injected).

    Attributes
    ----------
    settings : GameSettings
        Game configuration.
    theme : KarTEATheme
        Track colors from the player's palette.
    clock : pygame.time.Clock
        Pygame clock.
    last_time, time_left : float
        Timestamps taken at creation.
    dt : float
        Delta time placeholder (0).
    sprite_tree_left, sprite_tree_right : pygame.Surface
        Environment images placed beside the road.
    background_image : pygame.Surface
        Horizon image scaled to the screen height (aspect ratio kept).
    background_surface : pygame.Surface
        Horizon image tiled to cover the screen width with a margin.
    background_rect : pygame.Rect
        Position of ``background_surface``.
    menu_image : pygame.Surface | None
        Menu background, loaded by ``background_menu``.
    lines : list[Line]
        The 5000 lines of the road.
    line_count : int
        Number of lines.
    pos : float
        Road position (advances with delta time).
    last_start_pos : int | None
        ``start_pos`` of the previous frame (see _handle_passed_lines).
    player_x, player_y : int
        Camera lateral position and height.
    speed : float
        Road speed, in units per real second.

    Notes
    -----
    The horizon image has a fixed native size and does not follow the
    screen resolution. It is scaled to the screen height and tiled as
    many times as needed, so no black bands appear vertically or on wide
    screens (e.g. Full HD).
    """

    def __init__(self, settings: "GameSettings"):
        self.settings = settings

        self.theme = KarTEATheme(self.settings.PALETTE)
        self.clock = pygame.time.Clock()
        self.last_time = time.time()
        self.time_left = time.time()
        self.dt = 0

        self.sprite_tree_left = Image.load(
            self.settings.ENVIRONMENT_IMAGE_LEFT
        )

        self.sprite_tree_right = Image.load(
            self.settings.ENVIRONMENT_IMAGE_RIGHT
        )

        # The horizon has a fixed native size (e.g. 768x411): scale it
        # to the screen height and tile it to cover the width (2 fixed
        # copies left black bands on screens wider than ~1536px, like
        # Full HD).
        raw_horizon = Image.load(self.settings.HORIZON_BG_IMAGE)
        native_w = raw_horizon.get_width()
        native_h = raw_horizon.get_height()
        scale_factor = self.settings.SCREEN_HEIGHT / native_h
        scaled_w = max(1, int(native_w * scale_factor))

        self.background_image = Image.scale(
            raw_horizon, (scaled_w, self.settings.SCREEN_HEIGHT)
        )

        tiles = max(2, (self.settings.SCREEN_WIDTH // scaled_w) + 2)

        self.background_surface = pygame.Surface(
            (scaled_w * tiles, self.settings.SCREEN_HEIGHT)
        )
        for i in range(tiles):
            self.background_surface.blit(
                self.background_image, (scaled_w * i, 0)
            )
        self.background_rect = self.background_surface.get_rect(topleft=(0, 0))

        self.menu_image = None

        self.lines: list[Line] = []
        self._create_road_lines()

        self.line_count = len(self.lines)
        self.pos = 0
        self.last_start_pos = None
        self.player_x = 0
        self.player_y = 1500

        self.speed = 0

    def _create_road_lines(self):
        """Create the 5000 lines that make up the road.

        Colors alternate every 3 lines (dark/light tones of the theme)
        and trees are placed every 70 lines.
        """
        for i in range(5000):
            line = Line(self.settings)
            line.z = i * self.settings.SEGMENT_LENGTH + 0.00001

            is_alternate = (i // 3) % 2

            line.grass_color = self.theme.grass[
                "light" if is_alternate else "dark"
            ]

            line.rumble_color = self.theme.rumble[
                "light" if is_alternate else "dark"
            ]

            line.road_color = self.theme.road["light"]

            line.div_color = (
                self.theme.rumble["light"]
                if is_alternate
                else self.theme.road["light"]
            )

            if i % 70 == 0:
                line.sprite_x = -2.5
                line.sprite = self.sprite_tree_left
                line.sprite2_x = 1
                line.sprite2 = self.sprite_tree_right

            self.lines.append(line)

    def set_speed_level(self, level: int) -> None:
        """Set the road speed from the arrival time.

        The speed (units per real SECOND, applied in draw() with
        delta_time) is computed so that an object takes
        ``settings.OBJECT_ARRIVAL_TIME[level]`` seconds between
        appearing on the road and reaching the front of the car, on any
        machine and FPS.

        Parameters
        ----------
        level : int
            Speed 1 (levels 1-2), 2 (levels 3-4) or 3 (levels 5-7).
        """
        seconds = self.settings.OBJECT_ARRIVAL_TIME[level]
        distance = (
            self.settings.OBJECT_ARRIVAL_SEGMENTS
            * self.settings.SEGMENT_LENGTH
        )
        self.speed = distance / seconds

    def speed1(self):
        """Set the slow speed (levels 1-2)."""
        self.set_speed_level(1)

    def speed2(self):
        """Set the medium speed (levels 3-4)."""
        self.set_speed_level(2)

    def speed3(self):
        """Set the fast speed (levels 5-7)."""
        self.set_speed_level(3)

    def stop(self):
        """Stop the road movement."""
        self.speed = 0

    def background_menu(self):
        """Load the menu background image, at screen size."""
        self.menu_image = Image.load(
            self.settings.MENU_BACKGROUND,
            size=(self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT),
            convert="default",
        )

    def get_start_pos(self) -> int:
        """Return the line index where targets/obstacles spawn.

        Returns
        -------
        int
            OBJECT_SPAWN_SEGMENTS lines ahead of the current position,
            wrapped around the road length.
        """
        # self.pos is a float (advances by delta time): // on a float
        # returns a float, and list indexing requires an int.
        return (
            int(self.pos // self.settings.SEGMENT_LENGTH)
            + self.settings.OBJECT_SPAWN_SEGMENTS
        ) % self.line_count

    def draw(self, surface: pygame.Surface, delta_time: float = 0.0):
        """Draw the background, the road and the sprites.

        Parameters
        ----------
        surface : pygame.Surface
            Surface drawn on.
        delta_time : float, optional
            Real time (s) since the previous frame
            (GameState.delta_time). With 0 the road does not advance
            (e.g. menu background).

        Notes
        -----
        The road advances by real elapsed time, not per frame, so it
        moves at the same speed in real seconds whatever FPS is
        achieved. The road loops after the last line. Lines behind the
        camera are not projected or drawn; each trapezoid joins the
        previous line projected in THIS frame to the current one.
        """
        # Draw the fixed background
        surface.blit(self.background_surface, self.background_rect)

        # Clear to black and redraw (original effect)
        surface.fill("black")
        surface.blit(self.background_surface, self.background_rect)

        # Advance by real elapsed time, not per frame, so the speed in
        # real seconds does not depend on the FPS (e.g. pose processing
        # can slow the game down on some machines).
        self.pos += self.speed * delta_time

        # Infinite road loop
        while self.pos >= self.line_count * self.settings.SEGMENT_LENGTH:
            self.pos -= self.line_count * self.settings.SEGMENT_LENGTH
        while self.pos < 0:
            self.pos += self.line_count * self.settings.SEGMENT_LENGTH

        # start_pos must be an int: it is a list index and a range()
        # limit below.
        start_pos = int(self.pos // self.settings.SEGMENT_LENGTH)
        self._handle_passed_lines(start_pos)

        x = dx = 0.0
        cam_h = self.player_y + self.lines[start_pos].y
        maxy = self.settings.SCREEN_HEIGHT * 2

        # Previous line projected in THIS frame. Each trapezoid joins
        # the previous line to the current one; using self.lines[n - 1]
        # took, on the first loop line, a projection from an earlier
        # frame.
        prev = None

        # Render the road segments
        for n in range(start_pos, start_pos + 300):
            current = self.lines[n % self.line_count]
            cam_z = self.pos - (
                self.line_count * self.settings.SEGMENT_LENGTH
                if n >= self.line_count
                else 0
            )

            # With delta_time, self.pos is fractional and line start_pos
            # is BEHIND the camera (z < cam_z). Projected, it would come
            # out inverted (above the screen), become the clipping limit
            # (maxy) and the rest of the road would be discarded, with a
            # trapezoid drawn over the screen. Lines behind the camera
            # are neither projected nor drawn.
            if current.z - cam_z <= 0:
                x += dx
                dx += current.curve
                prev = None
                continue

            current.project(self.player_x - x, cam_h, cam_z)
            x += dx
            dx += current.curve

            current.clip = maxy

            if current.screen_y >= maxy:
                prev = current
                continue
            maxy = current.screen_y

            # First visible line: no previous line in this frame yet (it
            # is below the bottom edge of the screen, so there is no
            # gap).
            if prev is None:
                prev = current
                continue

            # Road layers
            self.draw_quad(
                surface,
                current.grass_color,
                0,
                prev.screen_y,
                self.settings.SCREEN_WIDTH,
                0,
                current.screen_y,
                self.settings.SCREEN_WIDTH,
            )
            self.draw_quad(
                surface,
                current.rumble_color,
                prev.screen_x,
                prev.screen_y,
                prev.screen_w * 1.2,
                current.screen_x,
                current.screen_y,
                current.screen_w * 1.2,
            )
            self.draw_quad(
                surface,
                current.road_color,
                prev.screen_x,
                prev.screen_y,
                prev.screen_w,
                current.screen_x,
                current.screen_y,
                current.screen_w,
            )
            self.draw_quad(
                surface,
                current.div_color,
                prev.screen_x,
                prev.screen_y,
                prev.screen_w * 0.35,
                current.screen_x,
                current.screen_y,
                current.screen_w * 0.35,
            )
            self.draw_quad(
                surface,
                current.road_color,
                prev.screen_x,
                prev.screen_y,
                prev.screen_w * 0.3,
                current.screen_x,
                current.screen_y,
                current.screen_w * 0.3,
            )
            prev = current

        self._draw_sprites(surface, start_pos)

    def _draw_sprites(self, surface: pygame.Surface, start_pos: int) -> None:
        """Draw sprites, trees and targets, from back to front.

        Uses only lines projected in this frame: start_pos + 1 to
        start_pos + 299 (start_pos + 300 kept the projection of a
        previous frame).
        """
        for n in range(start_pos + 299, start_pos, -1):
            line = self.lines[n % self.line_count]

            if line.sprite is not None:
                line.draw_sprite(surface)
            if line.sprite2 is not None:
                line.draw_sprite2(surface)
            if line.target is not None:
                line.draw_target(surface)
                line.target.update_current_pos(
                    line.target.current_pos[0], line.screen_y
                )

    def _handle_passed_lines(self, start_pos: int) -> None:
        """Handle the lines left behind the camera in this frame.

        Each line passed is marked with ``line.passed = True`` (used to
        detect the finish line crossing) and has its target released, as
        described below.

        A target/obstacle is only considered avoided when the projection
        of its line goes past the bottom of the screen. With delta_time,
        a slower frame (disk write, MediaPipe) makes the road advance
        several segments at once, and the line could go straight behind
        the camera without passing that point: the target stayed without
        an outcome (no "Desviou" recorded) until the end of the level.

        For each line passed since the previous frame:

        - the target goes below the screen (position and rectangle), and
          the GameController removal loop records it as avoided, without
          counting a collision with the car;
        - the line no longer points to the target, so it is not drawn
          again when the road wraps around (5000 segments).
        """
        last = self.last_start_pos
        self.last_start_pos = start_pos
        if last is None:
            return

        passed = (start_pos - last) % self.line_count
        far_below = self.settings.SCREEN_HEIGHT * 10
        for i in range(1, passed + 1):
            line = self.lines[(last + i) % self.line_count]
            line.passed = True
            target = line.target
            if target is None:
                continue
            line.target = None
            target.define_pos(target.rect.x, far_below)
            target.update_current_pos(target.current_pos[0], far_below)

    def draw_quad(
        self,
        surface: pygame.Surface,
        color: pygame.Color,
        x1: int,
        y1: int,
        w1: int,
        x2: int,
        y2: int,
        w2: int,
    ):
        """Draw a quadrilateral (trapezoid) used to render the road.

        Parameters
        ----------
        surface : pygame.Surface
            Surface drawn on.
        color : pygame.Color
            Fill color.
        x1, y1, w1 : int
            Center, height and half width of the bottom edge.
        x2, y2, w2 : int
            Center, height and half width of the top edge.
        """
        pygame.draw.polygon(
            surface,
            color,
            [(x1 - w1, y1), (x2 - w2, y2), (x2 + w2, y2), (x1 + w1, y1)],
        )
