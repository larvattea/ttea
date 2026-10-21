"""Camera capture (OpenCV) of the KarTEA game."""

from typing import TYPE_CHECKING

import cv2

from ttea.games.kartea.gameutil import regain_focus

if TYPE_CHECKING:
    from ttea.games.kartea.gameutil import GameSettings
    from ttea.games.kartea.model import CameraConfig


class Camera:
    """Manage the camera (video capture via OpenCV).

    Parameters
    ----------
    config : CameraConfig
        Camera index and backend (KarteaHardwareService).
    settings : GameSettings
        Calibration points and colors used to draw the area.

    Attributes
    ----------
    config : CameraConfig
        Camera configuration.
    settings : GameSettings
        Game configuration.
    cap : cv2.VideoCapture
        Open video capture.
    ret : bool
        Whether the last read succeeded.
    frame : numpy.ndarray | None
        Last frame read (None after a failed read).

    Notes
    -----
    The first frame is read and the "Tela de Captura" window is created
    on creation, so the window takes the focus once, before the pygame
    window gets it back (``regain_focus``).
    """

    def __init__(self, config: "CameraConfig", settings: "GameSettings"):
        self.config = config
        self.settings = settings
        self.cap = cv2.VideoCapture(
            config.camera_index, config.capture_backend
        )
        self.ret = False
        self.frame = None
        self._window_shown = False

        self.ret, self.frame = self.cap.read()

        # Created here, not on the first imshow, so it does not steal
        # the focus from the pygame window later.
        cv2.namedWindow("Tela de Captura")

    def load_camera(self) -> bool:
        """Read a camera frame and draw the calibration area on it.

        Returns
        -------
        bool
            True if a frame was read; False otherwise (``frame`` becomes
            None).

        Notes
        -----
        The frame is mirrored horizontally and the 4 sides and 4 points
        of the calibration area are drawn on it
        (``CALIBRATION_LINE_COLOR`` and ``CALIBRATION_POINT_COLOR``).
        ``show`` displays it, once the pose is drawn too.
        """
        self.ret, self.frame = self.cap.read()

        if not self.ret or self.frame is None:
            self.frame = None
            return False

        if self.frame is not None:
            # Mirror the image horizontally
            self.frame = cv2.flip(self.frame, 1)

            # Sides of the calibration area
            cv2.line(
                self.frame,
                self.settings.CALIBRATION_POINTS[0],
                self.settings.CALIBRATION_POINTS[1],
                self.settings.CALIBRATION_LINE_COLOR,
                2,
            )

            cv2.line(
                self.frame,
                self.settings.CALIBRATION_POINTS[1],
                self.settings.CALIBRATION_POINTS[3],
                self.settings.CALIBRATION_LINE_COLOR,
                2,
            )

            cv2.line(
                self.frame,
                self.settings.CALIBRATION_POINTS[2],
                self.settings.CALIBRATION_POINTS[0],
                self.settings.CALIBRATION_LINE_COLOR,
                2,
            )

            cv2.line(
                self.frame,
                self.settings.CALIBRATION_POINTS[2],
                self.settings.CALIBRATION_POINTS[3],
                self.settings.CALIBRATION_LINE_COLOR,
                2,
            )

            # Calibration points as circles
            cv2.circle(
                self.frame,
                self.settings.CALIBRATION_POINTS[0],
                5,
                self.settings.CALIBRATION_POINT_COLOR,
                3,
            )
            cv2.circle(
                self.frame,
                self.settings.CALIBRATION_POINTS[1],
                5,
                self.settings.CALIBRATION_POINT_COLOR,
                3,
            )
            cv2.circle(
                self.frame,
                self.settings.CALIBRATION_POINTS[2],
                5,
                self.settings.CALIBRATION_POINT_COLOR,
                3,
            )
            cv2.circle(
                self.frame,
                self.settings.CALIBRATION_POINTS[3],
                5,
                self.settings.CALIBRATION_POINT_COLOR,
                3,
            )

        return True

    def show(self) -> None:
        """Show the last frame in the "Tela de Captura" window."""
        if self.frame is None:
            return
        cv2.imshow("Tela de Captura", self.frame)

        # The first imshow resizes the window, and Windows activates
        # it: give the focus back to the game window once.
        if not self._window_shown:
            self._window_shown = True
            regain_focus()

    def close_camera(self):
        """Release the camera and close the capture window."""
        if self.cap is not None:
            self.cap.release()
        cv2.destroyWindow("Tela de Captura")
