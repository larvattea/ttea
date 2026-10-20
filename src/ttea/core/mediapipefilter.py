"""Image enhancement and landmark smoothing for pose detection.

Improves camera frames before they reach MediaPipe (CLAHE for dark
scenes, gamma correction for bright ones) and smooths the detected
landmarks over time to reduce jitter.
"""

from collections import deque

import cv2
import numpy as np

from ttea.service import CalibrationService


class MediaPipeFilter:
    """Enhance camera frames and smooth pose landmarks.

    All thresholds and factors are read from ``CalibrationService``
    when the object is created, except the brightness limits and the
    movement threshold, which are read on every call.

    Attributes
    ----------
    service : CalibrationService
        Source of the filter settings.
    clahe : cv2.CLAHE
        CLAHE operator built with the configured clip limit and tile
        grid size.
    smoothing_frames : int
        Number of recent positions averaged per landmark.
    history : dict[int, collections.deque]
        Recent ``(x, y)`` positions per landmark index, each deque
        limited to ``smoothing_frames`` items.
    gamma_table : numpy.ndarray
        256-entry ``uint8`` lookup table for gamma correction.

    Notes
    -----
    The gamma table maps each level ``i`` to
    ``255 * (i / 255) ** (1 / gamma)``, where ``gamma`` is
    ``get_filter_gamma_factor()``.
    """

    def __init__(self):
        self.service = CalibrationService()
        self.clahe = cv2.createCLAHE(
            clipLimit=self.service.get_filter_clahe_clip(),
            tileGridSize=(self.service.get_filter_clahe_grid()),
        )
        self.smoothing_frames = (
            self.service.get_filter_average_smooth_frames()
        )
        self.history = {}

        # Precomputed once, so each frame needs only one LUT lookup.
        inv_gamma = 1.0 / self.service.get_filter_gamma_factor()
        self.gamma_table = np.array(
            [((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]
        ).astype("uint8")

    def apply_enhancements(self, frame):
        """Apply the filters that suit the frame brightness.

        Parameters
        ----------
        frame : numpy.ndarray
            BGR image from OpenCV.

        Returns
        -------
        numpy.ndarray
            The enhanced BGR image (or the input frame if no filter
            applies).

        Notes
        -----
        Brightness is the mean of the V channel in HSV (0-255). Below
        ``get_filter_clahe_lum_below()`` CLAHE is applied to help the
        detection in dark scenes; above ``get_filter_gamma_lum_above()``
        gamma correction is applied for full-light scenes. Both checks
        use the brightness of the original frame.
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        avg_brightness = np.mean(hsv[:, :, 2])

        # Typical limits: dark below ~100 (CLAHE helps the AI) and full
        # light above ~150 (only a light gamma).
        if avg_brightness < self.service.get_filter_clahe_lum_below():
            frame = self.apply_clahe(frame)

        if avg_brightness > self.service.get_filter_gamma_lum_above():
            frame = self.apply_gamma(frame)
        return frame

    def apply_clahe(self, frame):
        """Apply CLAHE to the lightness channel of a BGR frame.

        Parameters
        ----------
        frame : numpy.ndarray
            BGR image from OpenCV.

        Returns
        -------
        numpy.ndarray
            BGR image with CLAHE applied to the L channel in LAB space.
        """
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l_enhanced = self.clahe.apply(l)
        enhanced_lab = cv2.merge((l_enhanced, a, b))
        return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    def apply_gamma(self, frame):
        """Apply gamma correction to a BGR frame.

        Parameters
        ----------
        frame : numpy.ndarray
            BGR image from OpenCV.

        Returns
        -------
        numpy.ndarray
            Image mapped through ``gamma_table`` with ``cv2.LUT``.
        """
        return cv2.LUT(frame, self.gamma_table)

    def smooth_landmarks(self, pose_landmarks_list):
        """Smooth landmark positions with a moving average.

        Parameters
        ----------
        pose_landmarks_list : list
            One list of normalized landmarks per detected pose, as in
            ``PoseLandmarkerResult.pose_landmarks``.

        Returns
        -------
        list
            The same list, with ``x`` and ``y`` of each landmark
            replaced in place by the average of its last
            ``smoothing_frames`` positions; an empty list when the input
            is empty.

        Notes
        -----
        All body landmarks are smoothed. When a landmark moves farther
        than ``get_filter_landmark_limit()`` (Euclidean distance in
        normalized x, y) from its last position, its history is cleared
        so fast movements, such as steps, are not delayed. An empty
        input clears the whole history.

        The history is keyed only by landmark index, so with more than
        one detected pose the positions of different people are
        averaged together.
        """
        if not pose_landmarks_list:
            self.history.clear()
            return []

        movement_threshold = self.service.get_filter_landmark_limit()

        for landmarks in pose_landmarks_list:
            for idx, pt in enumerate(landmarks):
                if idx not in self.history:
                    self.history[idx] = deque(maxlen=self.smoothing_frames)

                if len(self.history[idx]) > 0:
                    last_x, last_y = self.history[idx][-1]
                    distance = np.sqrt(
                        (pt.x - last_x) ** 2 + (pt.y - last_y) ** 2
                    )
                    if distance > movement_threshold:
                        self.history[idx].clear()

                self.history[idx].append((pt.x, pt.y))
                avg_coords = np.mean(self.history[idx], axis=0)
                pt.x = float(avg_coords[0])
                pt.y = float(avg_coords[1])

        return pose_landmarks_list
