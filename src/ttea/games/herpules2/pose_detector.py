"""Camera and MediaPipe pose detection for Herpules 2."""

import cv2
import mediapipe as mp


class PoseDetector:
    """Read the camera and detect the body pose with MediaPipe.

    Parameters
    ----------
    camera_index : int, optional
        OpenCV camera index. Default is 0.
    mostrar_camera : bool, optional
        Show the camera image in a "Camera" window. Default is True.
    mostrar_landmarks : bool, optional
        Draw the landmarks on that image. Default is True.

    Attributes
    ----------
    cap : cv2.VideoCapture
        Camera, set to 640x480.
    mp_pose, mp_drawing : module
        MediaPipe pose solution and drawing utilities.
    pose : mediapipe.solutions.pose.Pose
        Pose detector (model complexity 1, confidences 0.5).
    mostrar_camera, mostrar_landmarks : bool
        Display options.
    frame_skip : int
        Frames read so far, used to process every other frame.
    last_landmarks : list | None
        Last landmarks found.

    Notes
    -----
    If the camera cannot be opened, a message is printed and
    ``read_pose`` returns None.
    """

    def __init__(self, camera_index=0, mostrar_camera=True, mostrar_landmarks=True):
        self.cap = cv2.VideoCapture(camera_index)

        if not self.cap.isOpened():
            print("Erro: não foi possível abrir a câmera.")

        # Lower resolution = better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils

        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.mostrar_camera = mostrar_camera
        self.mostrar_landmarks = mostrar_landmarks

        self.frame_skip = 0
        self.last_landmarks = None

    def read_pose(self):
        """Read a camera frame and return the body landmarks.

        Returns
        -------
        list | None
            The 33 pose landmarks (normalized coordinates), or None if
            the camera cannot be read.

        Notes
        -----
        The image is mirrored. Only every other frame is processed; the
        others, and frames without a pose, return the last landmarks
        found, which may be stale (None before the first detection).
        """
        if self.cap is None or not self.cap.isOpened():
            return None

        ok, frame = self.cap.read()

        if not ok:
            print("Erro: não foi possível ler frame da câmera.")
            return None

        frame = cv2.flip(frame, 1)

        # Process the pose only every other frame, for performance

        self.frame_skip += 1

        if self.frame_skip % 2 != 0:
            return self.last_landmarks


        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        rgb.flags.writeable = False

        resultado = self.pose.process(rgb)

        rgb.flags.writeable = True

        if (
            self.mostrar_landmarks
            and resultado.pose_landmarks
        ):
            self.mp_drawing.draw_landmarks(
                frame,
                resultado.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS
            )

        if self.mostrar_camera:
            cv2.imshow("Camera", frame)
            cv2.waitKey(1)

        if not resultado.pose_landmarks:
            return self.last_landmarks

        self.last_landmarks = resultado.pose_landmarks.landmark

        return self.last_landmarks

    def release(self):
        """Release the camera, the detector and the OpenCV windows."""
        if self.cap is not None:
            self.cap.release()

        self.pose.close()

        cv2.destroyAllWindows()
