import io

import pygame
from PySide6.QtCore import QFile, QIODevice


class Image:
    """
    Classe utilitária para carregamento, escala e desenho de imagens.
    Suporta caminhos físicos e recursos Qt (.qrc).
    """

    @staticmethod
    def load_from_qt_resource(resource_path: str) -> pygame.Surface:
        """Carrega recurso Qt via QFile."""
        file = QFile(resource_path)
        if not file.open(QIODevice.ReadOnly):
            raise FileNotFoundError(
                f"Não foi possível abrir recurso Qt: {resource_path}."
            )

        img_data = file.readAll().data()
        file.close()
        return pygame.image.load(io.BytesIO(img_data))
