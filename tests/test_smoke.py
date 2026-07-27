import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QFile
from PySide6.QtWidgets import QApplication, QMainWindow

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
            (PathConfig.MODELS_PATH / "pose_landmarker_full.task").is_file()
        )

        window.close()


if __name__ == "__main__":
    unittest.main()
