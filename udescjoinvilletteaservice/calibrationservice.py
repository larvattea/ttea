from typing import Dict, List, Optional
from PySide6.QtCore import QRect
from PySide6.QtGui import QGuiApplication, QScreen
from PySide6.QtMultimedia import QMediaDevices, QCameraDevice

from udescjoinvilletteamodel import Calibration


class CalibrationService:
    def __init__(self):
        # Cache opcional se os monitores não mudarem durante a execução
        self._screens = QGuiApplication.screens()

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
