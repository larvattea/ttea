import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import cv2
import pygame
from PySide6.QtCore import QFile, QUrl
from PySide6.QtHelp import QHelpEngineCore
from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QMainWindow

from ttea.games.kartea.gameutil.alphablit import alpha_blit_flags
from ttea.main import App
from ttea.model import Language
from ttea.service import CalibrationSettingService, HelpService
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


class HelpTest(unittest.TestCase):
    """Help system: topic map and compiled help files."""

    @classmethod
    def setUpClass(cls):
        """Create the QApplication shared by the tests."""
        cls.qt_app = QApplication.instance() or QApplication([])

    def test_every_screen_points_to_a_known_topic(self):
        """Every screen in VIEW_TOPICS maps to an existing topic."""
        for view_name, topic in HelpService.VIEW_TOPICS.items():
            with self.subTest(view=view_name):
                self.assertIn(topic, HelpService.TOPICS)

    def test_topic_follows_screen_and_help_id(self):
        """F1 uses the help_id property first, then the screen class."""
        service = HelpService()

        # Same class name as the real screen: F1 matches by name.
        class PlayerListView(QDialog):
            pass

        dialog = PlayerListView()
        field = QLineEdit(dialog)
        self.assertEqual(service.topic_for_widget(field), "cadastro_jogador")

        field.setProperty(HelpService.HELP_ID_PROPERTY, "calibracao")
        self.assertEqual(service.topic_for_widget(field), "calibracao")

        self.assertEqual(
            service.topic_for_widget(None), HelpService.HOME_TOPIC
        )
        dialog.deleteLater()

    def test_help_has_every_topic_in_every_language(self):
        """Each language's .qch contains every page used by F1."""
        for language in (lang["code"] for lang in Language.LANGUAGES):
            with self.subTest(language=language):
                qch = PathConfig.help_file(language)
                self.assertTrue(
                    qch.is_file(),
                    f"{qch} not found. Build it with "
                    "'make -f buildhelp.mk qch' in resources/help.",
                )
                self._assert_pages_exist(qch)

    def _assert_pages_exist(self, qch: Path) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            engine = QHelpEngineCore(str(Path(tmp) / "test.qhc"))
            engine.setReadOnly(False)
            self.assertTrue(engine.setupData(), engine.error())
            self.assertTrue(
                engine.registerDocumentation(str(qch)), engine.error()
            )
            namespace = QHelpEngineCore.namespaceName(str(qch))
            for topic, page in HelpService.TOPICS.items():
                url = QUrl(
                    f"qthelp://{namespace}/"
                    f"{HelpService.VIRTUAL_FOLDER}/{page}"
                )
                self.assertFalse(
                    engine.fileData(url).isEmpty(),
                    f"{qch.name}: topic '{topic}' ({page}) not found",
                )
            # Close the database before the folder is removed (Windows).
            del engine


if __name__ == "__main__":
    unittest.main()
