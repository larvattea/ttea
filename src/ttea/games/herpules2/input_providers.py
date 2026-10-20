"""Input providers of Herpules 2: keyboard, script and MediaPipe.

Each provider has ``get_input()``, returning an ``InputState`` per
frame, and ``calibrar()``.
"""

import pygame
import mediapipe as mp
from input_state import InputState
from pose_detector import PoseDetector



class KeyboardInputProvider:
    """Keyboard input: holding Down crouches.

    Jumps come from the Up key press handled by ``GameController``.
    """

    def get_input(self):
        """Return the input of the held keys.

        Returns
        -------
        InputState
            ``abaixar`` is True while Down is held; ``pular`` is always
            False.
        """
        estado = InputState()
        keys = pygame.key.get_pressed()
        estado.abaixar = keys[pygame.K_DOWN]
        return estado

    def calibrar(self):
        """Do nothing; the keyboard needs no calibration."""
        pass


class ScriptedInputProvider:
    """Fixed input sequence for automated tests.

    Jumps at frame 60 and crouches from frame 180 to 240.

    Attributes
    ----------
    frame : int
        Number of frames already returned.
    """

    def __init__(self):
        self.frame = 0

    def get_input(self):
        """Return the input of the current frame and advance one frame.

        Returns
        -------
        InputState
            The scripted input of this frame.
        """
        estado = InputState()

        if self.frame == 60:
            estado.pular = True

        if 180 <= self.frame <= 240:
            estado.abaixar = True

        self.frame += 1
        return estado

    def calibrar(self):
        """Do nothing; the script needs no calibration."""
        pass


class MediapipeInputProvider:
    """Body movement input: jumping and crouching seen by the camera.

    Compares the height of the hips and ankles (normalized image
    coordinates, y grows downward) with a baseline measured by
    ``calibrar``.

    Attributes
    ----------
    detector : PoseDetector
        Camera and pose detector.
    baseline_hip_y, baseline_foot_y : float | None
        Reference height of the hips and of the ankles.
    cooldown_pulo : int
        Frames left before another jump can be detected.
    pose_landmark : type
        MediaPipe ``PoseLandmark`` enum.
    hip_y_anterior : float | None
        Hip height in the previous frame.
    frames_sem_pose : int
        Consecutive frames without a pose.
    limiar_pulo : float
        Hip rise above the baseline needed for a jump (0.03).
    limiar_subida : float
        Hip rise between two frames needed for a jump (0.008).
    limiar_agachar : float
        Hip drop below the baseline that means crouching (0.05).
    """

    def __init__(self):
        self.detector = PoseDetector()
        self.baseline_hip_y = None
        self.baseline_foot_y = None
        self.cooldown_pulo = 0
        self.pose_landmark = mp.solutions.pose.PoseLandmark
        self.hip_y_anterior = None
        self.frames_sem_pose = 0
        self.limiar_pulo = 0.03
        self.limiar_subida = 0.008
        self.limiar_agachar = 0.05

    def release(self):
        """Release the camera and the pose detector."""
        self.detector.release()

    def calibrar(self):
        """Measure the baseline height of the hips and ankles.

        Notes
        -----
        Averages the mean of both hips and of both ankles over 30 camera
        reads; reads without a pose are skipped. Because the detector
        processes every other frame, half of the reads repeat the last
        landmarks.
        """
        valores_hip = []
        valores_foot = []

        for _ in range(30):
            landmarks = self.detector.read_pose()
            if landmarks:
                left_hip = landmarks[self.pose_landmark.LEFT_HIP]
                right_hip = landmarks[self.pose_landmark.RIGHT_HIP]

                hip_y = (left_hip.y + right_hip.y) / 2
                valores_hip.append(hip_y)

                left_ankle = landmarks[self.pose_landmark.LEFT_ANKLE]
                right_ankle = landmarks[self.pose_landmark.RIGHT_ANKLE]

                foot_y = (left_ankle.y + right_ankle.y) / 2
                valores_foot.append(foot_y)

        if valores_hip:
            self.baseline_hip_y = sum(valores_hip) / len(valores_hip)

        if valores_foot:
            self.baseline_foot_y = sum(valores_foot) / len(valores_foot)

    def get_input(self):
        """Turn the current pose into jump and crouch input.

        Returns
        -------
        InputState
            Empty when there is no pose or a baseline is still missing
            (it is then taken from the current pose).

        Notes
        -----
        A jump needs the hips above the baseline by ``limiar_pulo``, the
        ankles above theirs by 0.02, the hips rising by more than
        ``limiar_subida`` since the last frame and no cooldown; it then
        starts a 15-frame cooldown. Crouching is reported while the hips
        are below the baseline by more than ``limiar_agachar``.
        """
        estado = InputState()
        landmarks = self.detector.read_pose()

        if landmarks is None:
            self.frames_sem_pose += 1
            return estado

        self.frames_sem_pose = 0

        left_hip = landmarks[self.pose_landmark.LEFT_HIP]
        right_hip = landmarks[self.pose_landmark.RIGHT_HIP]
        hip_y = (left_hip.y + right_hip.y) / 2

        left_ankle = landmarks[self.pose_landmark.LEFT_ANKLE]
        right_ankle = landmarks[self.pose_landmark.RIGHT_ANKLE]

        foot_y = (left_ankle.y + right_ankle.y) / 2

        if self.baseline_hip_y is None:
            self.baseline_hip_y = hip_y
            self.hip_y_anterior = hip_y
            return estado

        if self.hip_y_anterior is None:
            self.hip_y_anterior = hip_y
            return estado
        
        if self.baseline_foot_y is None:
            self.baseline_foot_y = foot_y
            return estado

        delta_y = self.hip_y_anterior - hip_y
        self.hip_y_anterior = hip_y

        if self.cooldown_pulo > 0:
            self.cooldown_pulo -= 1

        feet_up = foot_y < self.baseline_foot_y - 0.02
        hip_up = hip_y < self.baseline_hip_y - self.limiar_pulo

        if (
            hip_up
            and feet_up
            and delta_y > self.limiar_subida
            and self.cooldown_pulo == 0
        ):
            estado.pular = True
            self.cooldown_pulo = 15

        if hip_y > self.baseline_hip_y + self.limiar_agachar:
            estado.abaixar = True

        return estado
