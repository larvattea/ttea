import os
import sys
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QRect, QSettings
from PySide6.QtGui import QGuiApplication, QScreen
from PySide6.QtMultimedia import QCameraDevice, QMediaDevices

from ttea.dao import CalibrationIniDAO, CalibrationPointDAO
from ttea.model import Calibration, CalibrationPoint
from ttea.util import PathConfig


class CalibrationService:
    def __init__(
        self,
        dao: Optional[CalibrationIniDAO] = None,
        dao_calibration_point: Optional[CalibrationPointDAO] = None,
    ):
        # Cache opcional se os monitores não mudarem durante a execução
        self._screens = QGuiApplication.screens()
        self.settings = QSettings(PathConfig.config(), QSettings.IniFormat)
        self.dao = dao or CalibrationIniDAO()
        self.dao_calibration_point = (
            dao_calibration_point or CalibrationPointDAO()
        )

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

    def create_calibration_point(
        self, data: Dict[str, Any]
    ) -> Optional[CalibrationPoint]:
        """
        Create a new calibration point from a dictionary of attributes.

        Parameters
        ----------
        data : dict
            Must contain the key ``id`` (int),  ``name`` (str),
            ``birth_date`` (date) and optionally ``observation`` (str).

        Returns
        -------
        CalibrationPoint or None
            The created ``CalibrationPoint`` instance if validation and insertion
            succeed; ``None`` otherwise.
        """
        calibration_point = CalibrationPoint(**data)

        new_id = self.dao_calibration_point.insert(calibration_point)
        return self.dao.select(new_id) if new_id > 0 else None
