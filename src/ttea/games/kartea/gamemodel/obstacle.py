"""Obstacle object of the KarTEA road."""

from .target import EventType, Target


class Obstacle(Target):
    """Obstacle in the game. Inherits from Target.

    Changes the image, the size and the result:

    - avoided (left the screen) -> 10 points, AVOIDED_OBSTACLE;
    - collided with the car -> 0 points, COLLIDED_OBSTACLE.

    Attributes
    ----------
    COLLIDED_RESULT : tuple[int, EventType], class attribute
        ``(0, EventType.COLLIDED_OBSTACLE)``.
    AVOIDED_RESULT : tuple[int, EventType], class attribute
        ``(10, EventType.AVOIDED_OBSTACLE)``.
    """

    COLLIDED_RESULT = (0, EventType.COLLIDED_OBSTACLE)
    AVOIDED_RESULT = (10, EventType.AVOIDED_OBSTACLE)

    def _size(self) -> tuple[int, int]:
        """Return the obstacle size (``OBSTACLE_SIZES``)."""
        return self.settings.OBSTACLE_SIZES

    def _image_path(self) -> str:
        """Return the obstacle image (``OBSTACLE_IMAGE``)."""
        return self.settings.OBSTACLE_IMAGE
