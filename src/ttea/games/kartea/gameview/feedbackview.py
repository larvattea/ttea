"""Immediate collision/avoidance feedback: sound and image."""

from typing import TYPE_CHECKING

import pygame

from ttea.games.kartea.gamemodel import Image, Sound

if TYPE_CHECKING:
    from ttea.games.kartea.gamemodel import KillResult
    from ttea.games.kartea.gameutil import GameSettings


class FeedbackView:
    """Play the sound and show the feedback image of a KillResult.

    A positive result (collided with a target, avoided an obstacle)
    plays the hit sound and shows the positive image; a negative one,
    the miss sound and the negative image. The image is centered at 20%
    of the screen height and stays visible for
    ``settings.FEEDBACK_IMAGE_TIME`` seconds (configurable per player, 0
    to 2 s). With 0 the image appears for a single frame, as in the
    original game. A new result replaces the current image and restarts
    the count.

    Use every frame: ``show`` when there is a result and ``draw`` after
    drawing the road, the car and the HUD.

    Parameters
    ----------
    settings : GameSettings
        Game configuration (sounds, images and display time).
    sound_enabled : bool, optional
        Initial sound state. Defaults to True.

    Attributes
    ----------
    settings : GameSettings
        Game configuration.
    sounds : dict[bool, pygame.mixer.Sound]
        Hit (True) and miss (False) sounds.
    images : dict[bool, pygame.Surface]
        Positive (True) and negative (False) images.
    duration : float
        Display time (s) of an image.
    current : bool | None
        Image being shown (True positive, False negative), or None.
    time_left : float
        Seconds left to show the current image.
    """

    def __init__(self, settings: "GameSettings", sound_enabled: bool = True):
        self.settings = settings
        self.sounds = {
            True: Sound.load(settings.POINT_SOUND),
            False: Sound.load(settings.MISS_SOUND),
        }
        self.images = {
            True: Image.load(settings.POSITIVE_FEEDBACK_IMAGE),
            False: Image.load(settings.NEGATIVE_FEEDBACK_IMAGE),
        }
        self.duration = float(settings.FEEDBACK_IMAGE_TIME)
        self.current: bool | None = None
        self.time_left = 0.0
        self.set_sound_enabled(sound_enabled)

    def set_sound_enabled(self, enabled: bool) -> None:
        """Turn the feedback sounds on or off.

        Parameters
        ----------
        enabled : bool
            True sets the volume to 1; False mutes the sounds.
        """
        volume = 1 if enabled else 0
        for sound in self.sounds.values():
            sound.set_volume(volume)

    def show(self, surface: pygame.Surface, result: "KillResult") -> None:
        """Play the sound and start showing the image of the result.

        The image is drawn by ``draw``, from this same frame on, until
        the configured time is complete.

        Parameters
        ----------
        surface : pygame.Surface
            Game screen (not used; drawing happens in ``draw``).
        result : KillResult
            Result of the removed object.
        """
        positive = result.is_positive
        self.sounds[positive].play()
        self.current = positive
        self.time_left = self.duration

    def draw(self, surface: pygame.Surface, delta_time: float) -> None:
        """Draw the image being shown and subtract the frame time.

        Parameters
        ----------
        surface : pygame.Surface
            Game screen.
        delta_time : float
            Frame duration in seconds (GameState.delta_time).
        """
        if self.current is None:
            return
        self._draw_image(surface)
        self.time_left -= delta_time
        if self.time_left <= 0:
            self.clear()

    def clear(self) -> None:
        """Remove the image being shown (e.g. when a level starts)."""
        self.current = None
        self.time_left = 0.0

    def _draw_image(self, surface: pygame.Surface) -> None:
        """Draw the current image, centered at 20% of the height."""
        if self.current is None:
            return
        image_pos = (
            surface.get_width() // 2,
            int(surface.get_height() * 0.20),
        )
        Image.draw(
            surface,
            self.images[self.current],
            image_pos,
            pos_mode=Image.IMAGE_POS_CENTER,
        )
