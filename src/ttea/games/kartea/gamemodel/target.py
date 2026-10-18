"""Target (star) object of the KarTEA road and its kill result."""

import random
import time
from typing import TYPE_CHECKING, NamedTuple

import pygame

from ttea.games.kartea.model import PlayerKarteaSessionDetail

from .image import Image

if TYPE_CHECKING:
    from ttea.games.kartea.gameutil import GameSettings

EventType = PlayerKarteaSessionDetail.EventType


class KillResult(NamedTuple):
    """Result of removing a target/obstacle.

    The model only reports what happened. GameController records the
    event and updates score and counters; FeedbackView plays the sound
    and shows the feedback image.

    Attributes
    ----------
    points : int
        Points earned.
    event_type : PlayerKarteaSessionDetail.EventType
        Event that happened (collided with/avoided target/obstacle).
    road : int
        Lane of the object (event position).

    Examples
    --------
    >>> KillResult(10, EventType.COLLIDED_TARGET, 1).is_positive
    True
    >>> KillResult(0, EventType.COLLIDED_OBSTACLE, 2).is_positive
    False
    """

    points: int
    event_type: EventType
    road: int

    @property
    def is_positive(self) -> bool:
        """Whether the result is good (positive feedback)."""
        return self.event_type in (
            EventType.COLLIDED_TARGET,
            EventType.AVOIDED_OBSTACLE,
        )


class Target:
    """Target (star) in the game.

    Subclasses change only the image, the size and the ``kill`` result
    (see Obstacle).

    Parameters
    ----------
    r : int | None
        Lane index (0, 1 or 2). If None (or out of range), chosen at
        random.
    settings : GameSettings
        Game configuration (injected).
    move_speed : int, optional
        Speed used by move() (set by the current level, in
        GameController). Defaults to 1.

    Attributes
    ----------
    COLLIDED_RESULT : tuple[int, EventType], class attribute
        (points, event) when it collides: ``(10, COLLIDED_TARGET)``.
    AVOIDED_RESULT : tuple[int, EventType], class attribute
        (points, event) when it is avoided: ``(0, AVOIDED_TARGET)``.
    MOVE_PATTERN : dict[int, tuple[int, int, int]], class attribute
        By speed: (lateral move step, growth step, lateral offset). Used
        by move().
    settings : GameSettings
        Game configuration.
    move_speed : int
        Speed used by move().
    size : tuple[int, int]
        Current size (grows as the object approaches).
    rect : pygame.Rect
        Hitbox/position on screen.
    images : list[pygame.Surface]
        Animation frames.
    current_frame : int
        Index of the frame being shown.
    current_pos : tuple
        Current position.
    current_road : int
        Lane of the object (0 left, 1 middle, 2 right).
    animation_timer : float
        Time of the next frame change.
    line : Line | None
        Road line the object is attached to.
    prev_pos_y : float
        Height in the previous frame, set by update_current_pos (used by
        reached).
    """

    COLLIDED_RESULT: tuple[int, EventType] = (10, EventType.COLLIDED_TARGET)
    AVOIDED_RESULT: tuple[int, EventType] = (0, EventType.AVOIDED_TARGET)

    MOVE_PATTERN = {
        1: (10, 5, 3),
        2: (8, 4, 2),
        3: (12, 6, 1),
        4: (16, 8, 1),
    }

    def __init__(
        self,
        r: int | None,
        settings: "GameSettings",
        move_speed: int = 1,
    ):
        self.settings = settings
        self.move_speed = move_speed

        size = self._size()
        road, start_pos = self.define_spawn_pos(r)

        self.size = size
        self.rect = pygame.Rect(start_pos[0], start_pos[1], size[0], size[1])
        self.images = [Image.load(self._image_path(), size=size)]
        self.current_frame = 0
        self.current_pos = start_pos
        self.current_road = road
        self.animation_timer = 0
        self.line = None

    def _size(self) -> tuple[int, int]:
        """Return the object size (``GameSettings.TARGETS_SIZES``)."""
        return self.settings.TARGETS_SIZES

    def _image_path(self) -> str:
        """Return the object image (``GameSettings.TARGET_IMAGE``)."""
        return self.settings.TARGET_IMAGE

    def define_spawn_pos(self, r: int | None = None):
        """Define the lane and initial position of the object.

        Parameters
        ----------
        r : int | None, optional
            Desired lane (0 left, 1 middle, 2 right); random if None or
            out of range.

        Returns
        -------
        tuple
            ``(road, start_pos)``, with ``start_pos`` from
            ``GameSettings.OBJ_POS``.
        """
        if r is not None and 0 <= r <= 2:
            road = r
        else:
            road = random.randint(0, 2)  # 0 left, 1 middle, 2 right

        start_pos = self.settings.OBJ_POS[road]
        return road, start_pos

    def define_pos(self, x: float, y: float):
        """Move the object rectangle to the projected coordinates.

        Parameters
        ----------
        x, y : float
            Projected position; the current rect size is kept.
        """
        self.rect = pygame.Rect(x, y, self.rect.width, self.rect.height)

    def _grow(self):
        """Grow the object by 3 px (approaching effect)."""
        self.rect.inflate_ip(3, 3)
        self.size = (int(self.size[0] + 3), int(self.size[1] + 3))
        self.images = [Image.load(self._image_path(), size=self.size)]

    def _lateral(self, dx: int) -> int:
        """Return the lateral move by lane (left -dx, right +dx)."""
        if self.current_road == 0:
            return -dx
        if self.current_road == 2:
            return dx
        return 0

    def move(self):
        """Move the object down with a small lateral drift.

        The drift depends on the lane and on the current speed
        (MOVE_PATTERN); speeds outside the table use a default pattern.
        """
        speed = self.move_speed
        y = self.current_pos[1]
        vel = [0, speed]

        pattern = self.MOVE_PATTERN.get(speed)
        if pattern is not None:
            lateral_step, grow_step, dx = pattern
            if y % lateral_step == 0:
                vel = [self._lateral(dx), speed]
            elif y % grow_step == 0:
                self._grow()
                vel = [self._lateral(dx), speed]
        else:  # default speed
            if y % 10 != 0:
                self._grow()
            vel = [self._lateral(3), speed]

        self.rect.move_ip(vel)
        self.current_pos = (
            self.current_pos[0] + vel[0],
            self.current_pos[1] + vel[1],
        )

    def move_to(self, x: float, y: float):
        """Move the object directly to a given position.

        Parameters
        ----------
        x, y : float
            New position; the rect is moved by the same offset.
        """
        vel = [x - self.current_pos[0], y - self.current_pos[1]]
        self.rect.move_ip(vel)
        self.current_pos = (x, y)

    def update_current_pos(self, x: float, y: float):
        """Update the current position directly (used by Background).

        Keeps the height of the previous frame to detect the passage in
        front of the car (see reached).

        Parameters
        ----------
        x, y : float
            New position.
        """
        self.prev_pos_y = self.current_pos[1]
        self.current_pos = (x, y)

    def reached(self, line_y: float) -> bool:
        """Check whether the object base crossed ``line_y`` this frame.

        Parameters
        ----------
        line_y : float
            Screen y to test (front of the car).

        Returns
        -------
        bool
            True if the previous height was above ``line_y`` and the
            current one is at or below it.

        Notes
        -----
        Compares with the previous frame, so the passage is detected
        even when the road advances several segments at once (low FPS).
        """
        prev_y = getattr(self, "prev_pos_y", self.current_pos[1])
        return prev_y < line_y <= self.current_pos[1]

    def animate(self):
        """Advance the animation frame when its time has come."""
        t = time.time()
        if t > self.animation_timer:
            self.animation_timer = t + self.settings.ANIMATION_SPEED
            self.current_frame += 1
            if self.current_frame > len(self.images) - 1:
                self.current_frame = 0

    def draw_hitbox(self, surface: pygame.Surface):
        """Draw the object hitbox (when enabled).

        Parameters
        ----------
        surface : pygame.Surface
            Surface drawn on.
        """
        pygame.draw.rect(surface, (200, 60, 0), self.rect)

    def draw(self, surface: pygame.Surface):
        """Draw the object on screen, animated.

        Parameters
        ----------
        surface : pygame.Surface
            Surface drawn on. The hitbox is drawn too when
            ``DRAW_HITBOX`` is on.
        """
        self.animate()
        Image.draw(
            surface,
            self.images[self.current_frame],
            self.rect.center,
            pos_mode="center",
        )

        if self.settings.DRAW_HITBOX:
            self.draw_hitbox(surface)

    def kill(self, targets: list, collided: bool) -> KillResult:
        """Remove the object from the list and return the result.

        Does not play sounds or draw: GameController hands the result to
        FeedbackView.

        Parameters
        ----------
        targets : list
            Active objects (the object is removed from it).
        collided : bool
            True when it collided with the car; False when it left the
            screen without colliding.

        Returns
        -------
        KillResult
            Points, event and lane. Target: 10 when collided, 0 when
            avoided.
        """
        if self in targets:
            targets.remove(self)
        points, event_type = (
            self.COLLIDED_RESULT if collided else self.AVOIDED_RESULT
        )
        return KillResult(points, event_type, self.current_road)
