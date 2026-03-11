import os
import sys
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QRect, QSettings
from PySide6.QtGui import QGuiApplication, QScreen
from PySide6.QtMultimedia import QCameraDevice, QMediaDevices

from udescjoinvilletteadao import CalibrationIniDAO
from udescjoinvilletteamodel import Calibration
from udescjoinvilletteautil import PathConfig


class CalibrationService:
    def __init__(self, dao: Optional[CalibrationIniDAO] = None):
        # Cache opcional se os monitores não mudarem durante a execução
        self._screens = QGuiApplication.screens()
        self.settings = QSettings(PathConfig.config(), QSettings.IniFormat)
        self.dao = dao or CalibrationIniDAO()

    def get_proportions(self) -> Dict[str, tuple[int, int]]:
        """Retorna o dicionário completo de proporções."""
        return Calibration.PROPORTIONS.items()

    def get_screens(self) -> List[QScreen]:
        """Atualiza e retorna a lista de monitores disponíveis."""
        return QGuiApplication.screens()

    def get_video_inputs(self) -> List[QCameraDevice]:
        """Retorna os inputs de vídeo disponíveis."""
        return QMediaDevices.videoInputs()

    def _get_screen(self, index: int) -> Optional[QScreen]:
        """Método privado para validar e recuperar um monitor com segurança."""
        screens = self.get_screens()
        if 0 <= index < len(screens):
            return screens[index]
        return None

    def get_geometry_of_screen(self, index: int) -> Optional[QRect]:
        screen = self._get_screen(index)
        return screen.geometry() if screen else None

    def get_available_geometry_of_screen(self, index: int) -> Optional[QRect]:
        screen = self._get_screen(index)
        return screen.availableGeometry() if screen else None

    def is_raspberry_pi(self) -> bool:
        """Verifica centralizadamente se o hardware é um Raspberry Pi."""
        if not sys.platform.startswith("lin"):
            return False
        try:
            if os.path.exists("/proc/device-tree/model"):
                with open("/proc/device-tree/model", "r") as f:
                    return "raspberry pi" in f.read().lower()
            return False
        except Exception:
            return False

    def is_windows(self) -> bool:
        """Verifica se o sistema operacional é Windows."""
        return sys.platform.startswith("win")

    def create_update_calibration(
        self, data: Dict[str, Any]
    ) -> Optional[Calibration]:
        calibration = Calibration(**data)
        calibration.set_data(data)

        if not calibration.is_valid():
            return None

        return self.dao.update(calibration)
