import os
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import cv2
import pygame
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QApplication, QMainWindow

from ttea.games.kartea.gameutil.alphablit import alpha_blit_flags
from ttea.main import App
from ttea.service import CalibrationSettingService
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

    def test_capture_uses_native_backends(self):
        service = CalibrationSettingService()

        # Mapeamento simulando o retorno que o INI/QSettings
        # entregaria para cada chave
        configured_backends = {
            "opencv/opencv_windows_capture": "CAP_DSHOW",
            "opencv/opencv_mac_capture": "CAP_AVFOUNDATION",
            "opencv/opencv_linux_capture": "CAP_V4L2",
        }

        def fake_settings_value(key, default="CAP_ANY"):
            return configured_backends.get(key, default)

        with (
            patch.object(
                service.settings, "value", side_effect=fake_settings_value
            ),
            patch.object(service, "is_raspberry_pi", return_value=False),
        ):
            with patch("sys.platform", "win32"):
                self.assertEqual(
                    service.get_opencv_capture_backend(), cv2.CAP_DSHOW
                )

            with patch("sys.platform", "darwin"):
                self.assertEqual(
                    service.get_opencv_capture_backend(),
                    cv2.CAP_AVFOUNDATION,
                )

            with patch("sys.platform", "linux"):
                self.assertEqual(
                    service.get_opencv_capture_backend(), cv2.CAP_V4L2
                )

            with patch("sys.platform", "freebsd14"):
                # Como freebsd cai no 'else', ele usará opencv_linux_capture
                self.assertEqual(
                    service.get_opencv_capture_backend(), cv2.CAP_V4L2
                )

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
