"""Body pose tracking (MediaPipe), focused on the player's feet.

The module-level ``mp_drawing``, ``mp_drawing_styles`` and ``mp_poses``
are the MediaPipe drawing helpers and pose connections used to draw
the landmarks.
"""

import time
from typing import TYPE_CHECKING

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.framework.formats import landmark_pb2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

if TYPE_CHECKING:
    from ttea.games.kartea.gameutil import GameSettings
    from ttea.games.kartea.model import PoseTrackingConfig

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_poses = mp.solutions.pose


class PoseTracking:
    """Detect the body pose with MediaPipe, focusing on the feet.

    Parameters
    ----------
    config : PoseTrackingConfig
        MediaPipe model and parameters (KarteaHardwareService).
    settings : GameSettings
        Screen and calibration points used in the camera -> screen
        mapping.

    Attributes
    ----------
    settings : GameSettings
        Game configuration.
    pose_tracking : vision.PoseLandmarker
        MediaPipe Tasks pose landmarker.
    feet_x, feet_y : int
        Screen position of the center of the feet; ``feet_y`` is locked
        near the bottom so the car only moves horizontally.
    feet1_x, feet1_y : float
        Normalized position of the player's left heel (landmark 30).
    feet2_x, feet2_y : float
        Normalized position of the player's right heel (landmark 29).
    feet_y_free : int
        Real screen y of the feet (before the lock); used by the feet
        marker and the feet button selection.
    has_pose : bool
        True if the player was detected in the last processed frame.
    results : PoseLandmarkerResult | None
        Result of the last detection.
    feet_closed : bool
        Kept from the original code; always False (see is_feet_closed).
    last_timestamp_ms : int
        Timestamp of the last frame sent to MediaPipe.

    Notes
    -----
    The frame reaches ``scan_feets`` already mirrored by ``Camera``.
    MediaPipe names the sides from the body it sees, so on a mirrored
    image its labels are swapped: landmark 29 ("left heel") is the
    player's real right heel and 30 is the real left heel. That is why
    landmark 30 is used as the left foot (``get_feet1``) and 29 as the
    right foot (``get_feet2``).
    """

    def __init__(self, config: "PoseTrackingConfig", settings: "GameSettings"):
        self.settings = settings
        # ============= MediaPipe Tasks (Pose Landmarker) =============
        base_options = python.BaseOptions(model_asset_path=config.model_path)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=config.running_mode,
            num_poses=config.num_poses,
            min_pose_detection_confidence=config.min_pose_detection_confidence,
            min_pose_presence_confidence=config.min_pose_presence_confidence,
            min_tracking_confidence=config.min_tracking_confidence,
        )

        self.pose_tracking = vision.PoseLandmarker.create_from_options(options)

        # Feet position
        self.feet_x = 0
        self.feet_y = 0
        self.feet1_x = 0
        self.feet1_y = 0
        self.feet2_x = 0
        self.feet2_y = 0
        self.feet_y_free = 0
        self.has_pose = False

        self.results = None
        self.feet_closed = (
            False
            # Kept as in the original (even though the method is empty)
        )
        self.last_timestamp_ms = 0

    def scan_feets(self, image):
        """Detect the feet in a camera frame and annotate the image.

        Parameters
        ----------
        image : numpy.ndarray
            Frame captured by the camera (BGR).

        Returns
        -------
        numpy.ndarray
            The same image, with the pose landmarks drawn when a player
            is detected.

        Notes
        -----
        - Timestamps sent to MediaPipe (video mode) are kept strictly
          increasing.
        - The feet center is the midpoint of the two heels, mapped to
          the screen by ``to_screen_position``; ``feet_y`` is then
          locked at ``SCREEN_HEIGHT - 50 * SCREEN_HEIGHT /
          BASE_HEIGHT``.
        - Without a detected pose, ``has_pose`` is False and the
          positions keep their previous values.
        """
        rows, cols, _ = image.shape

        # BGR -> RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Wrap the image in the format the Tasks API expects
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

        timestamp_ms = int(time.time() * 1000)
        if timestamp_ms <= self.last_timestamp_ms:
            timestamp_ms = self.last_timestamp_ms + 1
        self.last_timestamp_ms = timestamp_ms

        self.results = self.pose_tracking.detect_for_video(
            mp_image, timestamp_ms
        )

        self.feet_closed = False
        self.has_pose = False

        if (
            self.results.pose_landmarks
            and len(self.results.pose_landmarks) > 0
        ):
            landmarks = self.results.pose_landmarks[0]
            # Landmark 30 = left heel, Landmark 29 = right heel
            self.feet1_x = landmarks[30].x
            self.feet1_y = landmarks[30].y
            self.feet2_x = landmarks[29].x
            self.feet2_y = landmarks[29].y

            # Center point between the two feet
            x = (self.feet1_x + self.feet2_x) / 2
            y = (self.feet1_y + self.feet2_y) / 2

            # Map to the screen with the perspective transform
            self.feet_x, self.feet_y = self.to_screen_position(x, y)
            self.has_pose = True
            self.feet_y_free = self.feet_y  # real Y, before the lock

            # Lock Y (lateral movement only)
            self.feet_y = self.settings.SCREEN_HEIGHT - int(
                50 * self.settings.SCREEN_HEIGHT / self.settings.BASE_HEIGHT
            )

            pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            pose_landmarks_proto.landmark.extend(
                [
                    landmark_pb2.NormalizedLandmark(
                        x=landmark.x,
                        y=landmark.y,
                        z=landmark.z,
                        visibility=landmark.visibility,
                        presence=landmark.presence,
                    )
                    for landmark in landmarks
                ]
            )

            # Draw the landmarks on the image
            mp_drawing.draw_landmarks(
                image,
                pose_landmarks_proto,
                mp_poses.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
            )

        return image

    def get_feet_center(self):
        """Return the center position of the feet (controls the car).

        Returns
        -------
        tuple
            ``(feet_x, feet_y)``, with ``feet_y`` locked near the
            bottom.
        """
        return (self.feet_x, self.feet_y)

    def get_feet_marker_position(self) -> tuple[int, int] | None:
        """Return the real (x, y) screen position of the feet.

        Unlike get_feet_center, y is not locked. Used by the feet marker
        and by the feet button selection.

        Returns
        -------
        tuple[int, int] | None
            (x, y) in screen pixels, or None if the player was not
            detected in the last frame.
        """
        if not self.has_pose:
            return None
        return (int(self.feet_x), int(self.feet_y_free))

    def get_feet1(self):
        """Return the screen position of the first foot (landmark 30).

        Returns
        -------
        tuple[int, int]
            Heel position mapped by ``to_screen_position``.
        """
        return self.to_screen_position(self.feet1_x, self.feet1_y)

    def get_feet2(self):
        """Return the screen position of the second foot (landmark 29).

        Returns
        -------
        tuple[int, int]
            Heel position mapped by ``to_screen_position``.
        """
        return self.to_screen_position(self.feet2_x, self.feet2_y)

    def is_feet_closed(self):
        """Reserved to detect closed feet (not implemented)."""

    def to_screen_position(self, x: float, y: float):
        """Map a camera position to game screen coordinates.

        Parameters
        ----------
        x, y : float
            Normalized position (0-1) in the camera image.

        Returns
        -------
        tuple[int, int]
            Position in screen pixels.

        Notes
        -----
        A perspective transform maps the calibrated area
        (CALIBRATION_POINTS) to the control image (CONTROL_WIDTH x
        CONTROL_HEIGHT); the result is then scaled to the screen by
        WIDTH_RATIO and HEIGHT_RATIO.
        """
        pts1 = np.float32(
            [
                self.settings.CALIBRATION_POINTS[0],
                self.settings.CALIBRATION_POINTS[1],
                self.settings.CALIBRATION_POINTS[2],
                self.settings.CALIBRATION_POINTS[3],
            ]
        )
        pts2 = np.float32(
            [
                [0, 0],
                [self.settings.CONTROL_WIDTH, 0],
                [0, self.settings.CONTROL_HEIGHT],
                [
                    self.settings.CONTROL_WIDTH,
                    self.settings.CONTROL_HEIGHT,
                ],
            ]
        )

        matrix = cv2.getPerspectiveTransform(pts1, pts2)

        # Normalized position -> control image pixels
        p = (
            int(x * self.settings.CONTROL_WIDTH),
            int(y * self.settings.CONTROL_HEIGHT),
        )

        # Apply the perspective transform
        position_x = (
            matrix[0][0] * p[0] + matrix[0][1] * p[1] + matrix[0][2]
        ) / (matrix[2][0] * p[0] + matrix[2][1] * p[1] + matrix[2][2])
        position_y = (
            matrix[1][0] * p[0] + matrix[1][1] * p[1] + matrix[1][2]
        ) / (matrix[2][0] * p[0] + matrix[2][1] * p[1] + matrix[2][2])

        # Scale to the real game screen size
        p_after = (
            int(position_x * self.settings.WIDTH_RATIO),
            int(position_y * self.settings.HEIGHT_RATIO),
        )

        return p_after
