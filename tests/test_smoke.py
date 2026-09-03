import os
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import cv2
import pygame
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QApplication, QMainWindow

from ttea.games.kartea.gamecore.camera import Camera
from ttea.games.kartea.gameutil.alphablit import alpha_blit_flags
from ttea.main import App
from ttea.ui import Ui_MainView
from ttea.util import PathConfig


class SmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt_app = QApplication.instance() or QApplication([])

    def test_application_components_load(self):
        self.assertIsNotNone(App)

        window = QMainWindow()
        Ui_MainView().setupUi(window)

        self.assertTrue(QFile(":/icons/system/appicon").exists())
        self.assertTrue(
            (PathConfig.MODELS_DIR / "pose_landmarker_full.task").is_file()
        )

        window.close()

    @patch("cv2.VideoCapture")
    def test_camera_uses_native_backends(self, mock_videocapture):
        mock_instance = mock_videocapture.return_value
        mock_instance.read.return_value = (False, None)

        cam = Camera()

        # Mapeamento simulando o retorno que o INI/QSettings entregaria para cada chave
        configured_backends = {
            "opencv/opencv_windows_capture": "CAP_DSHOW",
            "opencv/opencv_mac_capture": "CAP_AVFOUNDATION",
            "opencv/opencv_linux_capture": "CAP_V4L2",
        }

        def fake_settings_value(key, default="CAP_ANY"):
            return configured_backends.get(key, default)

        target_service = (
            cam.service.calibration_service.calibration_setting_service
        )

        with patch.object(
            target_service.settings, "value", side_effect=fake_settings_value
        ):
            with patch("sys.platform", "win32"):
                self.assertEqual(cam.camera_backend(), cv2.CAP_DSHOW)

            with patch("sys.platform", "darwin"):
                self.assertEqual(cam.camera_backend(), cv2.CAP_AVFOUNDATION)

            with patch("sys.platform", "linux"):
                self.assertEqual(cam.camera_backend(), cv2.CAP_V4L2)

            with patch("sys.platform", "freebsd14"):
                # Como freebsd cai no 'else', ele usará opencv_linux_capture
                self.assertEqual(cam.camera_backend(), cv2.CAP_V4L2)

    def test_macos_uses_sdl2_alpha_blitter(self):
        with patch(
            "ttea.games.kartea.gameutil.alphablit.sys.platform", "darwin"
        ):
            self.assertEqual(alpha_blit_flags(), pygame.BLEND_ALPHA_SDL2)

        with patch(
            "ttea.games.kartea.gameutil.alphablit.sys.platform", "win32"
        ):
            self.assertEqual(alpha_blit_flags(), 0)


if __name__ == "__main__":
    unittest.main()
