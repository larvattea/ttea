"""Car controlled by the player in the KarTEA game."""

import time
from collections import deque
from typing import TYPE_CHECKING

import pygame

from .image import Image

if TYPE_CHECKING:
    from ttea.games.kartea.gamemodel.target import KillResult
    from ttea.games.kartea.gameutil import GameSettings


class Car:
    """Car controlled by the player (feet position via MediaPipe).

    Parameters
    ----------
    settings : GameSettings
        Game configuration (injected).

    Attributes
    ----------
    settings : GameSettings
        Game configuration.
    orig_image : pygame.Surface
        Vehicle image at ``CAR_SIZE``.
    image : pygame.Surface
        Image drawn (copy of ``orig_image``).
    image_smaller : pygame.Surface
        Vehicle image loaded again at ``CAR_SIZE``.
    rect : pygame.Rect
        Collision rectangle (hitbox), ``CAR_HITBOX_SIZE``.
    left_click : bool
        Interaction control (click / feet closed).
    lane_history : collections.deque
        ``(time, lane)`` pairs of the last COLLISION_LANE_TOLERANCE
        seconds; with tolerance 0, only the current lane.
    """

    def __init__(self, settings: "GameSettings"):
        self.settings = settings

        self.orig_image = Image.load(
            self.settings.VEHICLE_IMAGE,
            size=(self.settings.CAR_SIZE, self.settings.CAR_SIZE),
        )
        self.image = self.orig_image.copy()
        self.image_smaller = Image.load(
            self.settings.VEHICLE_IMAGE,
            size=(self.settings.CAR_SIZE, self.settings.CAR_SIZE),
        )

        self.rect = pygame.Rect(
            self.settings.SCREEN_WIDTH // 2,
            self.settings.SCREEN_HEIGHT // 2,
            self.settings.CAR_HITBOX_SIZE[0],
            self.settings.CAR_HITBOX_SIZE[1],
        )

        self.left_click = False

        self.lane_history = deque()

    def follow_mouse(self):
        """Move the car to follow the mouse (used for testing)."""
        self.rect.center = pygame.mouse.get_pos()

    def follow_mediapipe_hand(self, x: int, y: int):
        """Move the car to the detected feet position (MediaPipe).

        Parameters
        ----------
        x, y : int
            Screen position of the feet.
        """
        self.rect.center = (x, y)

    def draw_hitbox(self, surface: pygame.Surface):
        """Draw the car hitbox (when DRAW_HITBOX is on).

        Parameters
        ----------
        surface : pygame.Surface
            Surface drawn on.
        """
        pygame.draw.rect(surface, (200, 60, 0), self.rect)

    def draw(self, surface: pygame.Surface):
        """Draw the car on screen, centered on its hitbox.

        Parameters
        ----------
        surface : pygame.Surface
            Surface drawn on. The hitbox is drawn too when
            ``DRAW_HITBOX`` is on.
        """
        Image.draw(surface, self.image, self.rect.center, pos_mode="center")

        if self.settings.DRAW_HITBOX:
            self.draw_hitbox(surface)

    def record_lane(self, lane: int, now: float | None = None) -> None:
        """Record the current lane of the player (called every frame).

        Parameters
        ----------
        lane : int
            Current lane (0, 1, 2; -1 outside the area).
        now : float | None, optional
            Timestamp (s); ``time.time()`` when None.

        Notes
        -----
        Entries older than COLLISION_LANE_TOLERANCE are dropped, but the
        most recent one is always kept.
        """
        now = time.time() if now is None else now
        self.lane_history.append((now, lane))
        oldest = now - self.settings.COLLISION_LANE_TOLERANCE
        while len(self.lane_history) > 1 and self.lane_history[0][0] < oldest:
            self.lane_history.popleft()

    def hits(self, target) -> bool:
        """Decide whether the object hits the car, by player lane.

        Considers the lanes recorded in the tolerance window
        (GameSettings.COLLISION_LANE_TOLERANCE): it collides if the
        player was in the object's lane (star or obstacle) for MOST of
        the window. This absorbs the jitter of the feet reading near the
        lane boundary in both directions: a player in the lane does not
        miss the collision because of one wrong frame, and a player in
        another lane does not collide because of one frame read in the
        object's lane.

        Parameters
        ----------
        target : Target
            Object reaching the car.

        Returns
        -------
        bool
            True if it collides. With tolerance 0 the lane at the
            instant of the passage counts. Outside the area (-1) it does
            not collide.

        Examples
        --------
        >>> from types import SimpleNamespace as NS
        >>> car = Car.__new__(Car)
        >>> car.settings = NS(COLLISION_LANE_TOLERANCE=0.2)
        >>> car.lane_history = deque()
        >>> for t, lane in [(0.0, 1), (0.05, 2), (0.1, 1)]:
        ...     car.record_lane(lane, now=t)
        >>> car.hits(NS(current_road=1))
        True
        """
        lanes = [lane for _, lane in self.lane_history]
        if not lanes:
            return False
        in_lane = sum(1 for lane in lanes if lane == target.current_road)
        return in_lane > len(lanes) / 2

    def kill_targets(self, targets: list) -> list["KillResult"]:
        """Resolve the collisions of the objects that reached the car.

        When the base of an object passes the front of the car (top of
        the hitbox) in this frame, it collides if the player is in the
        object's lane (see hits). If it does not collide, the object
        goes on and is recorded as avoided when it leaves the screen
        (GameController).

        Parameters
        ----------
        targets : list
            Active objects; collided ones are removed from it.

        Returns
        -------
        list[KillResult]
            One result per object collided in this frame. Score,
            recording and feedback are handled by GameController.
        """
        front_y = self.rect.top
        results = []
        for target in targets[:]:
            if target.reached(front_y) and self.hits(target):
                results.append(target.kill(targets, collided=True))
        return results
