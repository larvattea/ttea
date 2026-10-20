"""Geometry helpers for projection (keystone) calibration.

The projected game content is fitted into the screen with a fixed
aspect ratio and mapped onto four destination corners through a
perspective (homography) transform built with OpenCV.
"""

from typing import Tuple

import cv2
import numpy as np


class CalibrationMath:
    """Mathematical utilities for projection / keystone calibration.

    All methods are classmethods; the class holds no state.

    Notes
    -----
    Corner points are always ordered top-left, top-right, bottom-left,
    bottom-right (TL, TR, BL, BR), both in the source rectangle of
    ``get_perspective_transform`` and in the destination points.
    """

    @classmethod
    def calculate_projection_area(
        cls,
        screen_width: int,
        screen_height: int,
        aspect_ratio: Tuple[int, int],
    ) -> Tuple[int, int]:
        """Compute the content size that fits the screen at a ratio.

        Parameters
        ----------
        screen_width : int
            Screen width in pixels.
        screen_height : int
            Screen height in pixels.
        aspect_ratio : tuple[int, int]
            Desired width/height ratio, e.g. ``(4, 3)`` or ``(16, 9)``.

        Returns
        -------
        tuple[int, int]
            ``(content_width, content_height)`` in pixels.

        Raises
        ------
        ValueError
            If ``aspect_ratio`` is not a tuple of two positive values.

        Notes
        -----
        Height has priority: the content takes the full screen height
        and the width follows the ratio. Only when that width exceeds
        the screen width is the content fitted to the full width
        instead.
        Integer division is used, so sizes are rounded down.

        Examples
        --------
        >>> calc = CalibrationMath.calculate_projection_area
        >>> calc(1920, 1080, (4, 3))
        (1440, 1080)
        >>> calc(1280, 1024, (16, 9))
        (1280, 720)
        """
        if not (
            isinstance(aspect_ratio, tuple)
            and len(aspect_ratio) == 2
            and all(x > 0 for x in aspect_ratio)
        ):
            raise ValueError(
                "The parameter aspect_ratio must be a tuple of two positive "
                "integers (e.g., (4, 3))"
            )

        ratio_w, ratio_h = aspect_ratio
        content_height = screen_height
        content_width = (screen_height * ratio_w) // ratio_h

        # Width overflow is rare in 16:9; it happens on narrow screens.
        if content_width > screen_width:
            content_width = screen_width
            content_height = (screen_width * ratio_h) // ratio_w

        return content_width, content_height

    @classmethod
    def calculate_centered_destination_points(
        cls,
        screen_width: int,
        screen_height: int,
        content_width: int,
        content_height: int,
        center_horizontally: bool = True,
        center_vertically: bool = True,
    ) -> np.ndarray:
        """Compute the corners of the content area on the screen.

        Parameters
        ----------
        screen_width : int
            Screen width in pixels.
        screen_height : int
            Screen height in pixels.
        content_width : int
            Content width in pixels.
        content_height : int
            Content height in pixels.
        center_horizontally : bool, optional
            Center the content horizontally; otherwise align it to the
            left edge. Default is True.
        center_vertically : bool, optional
            Center the content vertically; otherwise align it to the top
            edge. Default is True.

        Returns
        -------
        numpy.ndarray
            ``float32`` array of shape (4, 2) with the ``(x, y)``
            corners in TL, TR, BL, BR order.

        Examples
        --------
        >>> pts = CalibrationMath.calculate_centered_destination_points(
        ...     1920, 1080, 1440, 1080
        ... )
        >>> pts.tolist()
        [[240.0, 0.0], [1680.0, 0.0], [240.0, 1080.0], [1680.0, 1080.0]]
        """
        left = (
            (screen_width - content_width) // 2 if center_horizontally else 0
        )
        top = (screen_height - content_height) // 2 if center_vertically else 0

        return np.float32(
            [
                [left, top],  # TL
                [left + content_width, top],  # TR
                [left, top + content_height],  # BL
                [left + content_width, top + content_height],  # BR
            ]
        )

    @classmethod
    def calculate_destination_points_with_flip(
        cls,
        screen_width: int,
        screen_height: int,
        content_width: int,
        content_height: int,
        flip_h: bool = False,
        flip_v: bool = False,
        center_horizontally: bool = True,
        center_vertically: bool = True,
    ) -> np.ndarray:
        """Compute the content corners with optional mirroring.

        Parameters
        ----------
        screen_width : int
            Screen width in pixels.
        screen_height : int
            Screen height in pixels.
        content_width : int
            Content width in pixels.
        content_height : int
            Content height in pixels.
        flip_h : bool, optional
            Mirror the content horizontally. Default is False.
        flip_v : bool, optional
            Mirror the content vertically. Default is False.
        center_horizontally : bool, optional
            Center the content horizontally. Default is True.
        center_vertically : bool, optional
            Center the content vertically. Default is True.

        Returns
        -------
        numpy.ndarray
            ``float32`` array of shape (4, 2) with the corners of
            ``calculate_centered_destination_points`` reordered for the
            requested mirroring.

        Notes
        -----
        Mirroring only reorders the corners (TL, TR, BL, BR = 0, 1, 2,
        3): horizontal uses ``[1, 0, 3, 2]``, vertical ``[2, 3, 0, 1]``
        and both ``[3, 2, 1, 0]``. Used as destination points of
        ``get_perspective_transform``, this flips the warped image.

        Examples
        --------
        >>> cm = CalibrationMath
        >>> pts = cm.calculate_destination_points_with_flip(
        ...     100, 50, 100, 50, flip_h=True
        ... )
        >>> pts.tolist()
        [[100.0, 0.0], [0.0, 0.0], [100.0, 50.0], [0.0, 50.0]]
        """
        points = cls.calculate_centered_destination_points(
            screen_width,
            screen_height,
            content_width,
            content_height,
            center_horizontally,
            center_vertically,
        )

        if not (flip_h or flip_v):
            return points

        order = [0, 1, 2, 3]

        if flip_h:
            order = [1, 0, 3, 2]  # horizontal mirror
        if flip_v:
            order = [2, 3, 0, 1]  # vertical mirror
            if flip_h:
                order = [3, 2, 1, 0]  # both

        return points[np.array(order)]

    @classmethod
    def get_perspective_transform(
        cls,
        content_size: Tuple[int, int],
        dst_points: np.ndarray,
    ) -> np.ndarray:
        """Build the 3x3 homography from content to destination points.

        Parameters
        ----------
        content_size : tuple[int, int]
            ``(width, height)`` of the source content in pixels.
        dst_points : numpy.ndarray
            ``float32`` array of shape (4, 2) with the destination
            corners in TL, TR, BL, BR order.

        Returns
        -------
        numpy.ndarray
            3x3 perspective matrix from ``cv2.getPerspectiveTransform``.

        Examples
        --------
        >>> import numpy as np
        >>> dst = np.float32([[0, 0], [100, 0], [0, 50], [100, 50]])
        >>> calc = CalibrationMath.get_perspective_transform
        >>> m = calc((100, 50), dst)
        >>> bool(np.allclose(m, np.eye(3)))
        True
        """
        src_points = np.float32(
            [
                [0, 0],
                [content_size[0], 0],
                [0, content_size[1]],
                [content_size[0], content_size[1]],
            ]
        )
        return cv2.getPerspectiveTransform(src_points, dst_points)

    @classmethod
    def get_inverse_transform(cls, matrix: np.ndarray) -> np.ndarray:
        """Return the inverse of a transform matrix.

        Used to map screen/camera points back to game coordinates.

        Parameters
        ----------
        matrix : numpy.ndarray
            Square transform matrix, usually from
            ``get_perspective_transform``.

        Returns
        -------
        numpy.ndarray
            Inverse matrix computed by ``numpy.linalg.inv``.

        Raises
        ------
        numpy.linalg.LinAlgError
            If the matrix is singular.

        Examples
        --------
        >>> import numpy as np
        >>> m = np.array([[2.0, 0, 0], [0, 2.0, 0], [0, 0, 1.0]])
        >>> CalibrationMath.get_inverse_transform(m).diagonal().tolist()
        [0.5, 0.5, 1.0]
        """
        return np.linalg.inv(matrix)
