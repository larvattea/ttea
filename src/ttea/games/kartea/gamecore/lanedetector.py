"""Detection of the player's lane from the feet position.

Attributes
----------
OUT_OF_AREA : int
    Lane value outside the game area (-1).
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ttea.games.kartea.gameutil import GameSettings

OUT_OF_AREA = -1


class LaneDetector:
    """Turn the horizontal feet position into a lane.

    The position is already in screen pixels; the lane is 0 (left),
    1 (middle), 2 (right) or OUT_OF_AREA (-1). The lane boundaries come
    from GameSettings (thirds of the width).

    Parameters
    ----------
    settings : GameSettings
        Game configuration (LANE_DIV_0 to LANE_DIV_3).

    Attributes
    ----------
    settings : GameSettings
        Game configuration.
    """

    def __init__(self, settings: "GameSettings"):
        self.settings = settings

    def lane_for_x(self, x: float) -> int:
        """Return the lane of screen x coordinate ``x``.

        Parameters
        ----------
        x : float
            Horizontal position in screen pixels.

        Returns
        -------
        int
            0, 1 or 2; OUT_OF_AREA outside ``[LANE_DIV_0, LANE_DIV_3)``.

        Examples
        --------
        >>> from types import SimpleNamespace
        >>> settings = SimpleNamespace(
        ...     LANE_DIV_0=0, LANE_DIV_1=100,
        ...     LANE_DIV_2=200, LANE_DIV_3=300,
        ... )
        >>> detector = LaneDetector(settings)
        >>> detector.lane_for_x(150), detector.lane_for_x(300)
        (1, -1)
        """
        s = self.settings
        if s.LANE_DIV_0 <= x < s.LANE_DIV_1:
            return 0
        if s.LANE_DIV_1 <= x < s.LANE_DIV_2:
            return 1
        if s.LANE_DIV_2 <= x < s.LANE_DIV_3:
            return 2
        return OUT_OF_AREA
