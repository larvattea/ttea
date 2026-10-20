"""Load images from Qt resources as pygame surfaces.

Lets the pygame side of the application use images compiled into
the Qt resource file (``.qrc``).
"""

import io

import pygame
from PySide6.QtCore import QFile, QIODevice


class Image:
    """Utility class for loading images.

    Images are read from Qt resource paths (``:/...``).
    """

    @staticmethod
    def load_from_qt_resource(resource_path: str) -> pygame.Surface:
        """Load an image from a Qt resource using QFile.

        Parameters
        ----------
        resource_path : str
            Qt resource path to the image file.

        Returns
        -------
        pygame.Surface
            Loaded image surface.

        Raises
        ------
        FileNotFoundError
            If the Qt resource cannot be opened.

        Notes
        -----
        The whole file is read into memory and decoded by
        ``pygame.image.load``, so the image format is detected from
        its content.
        """
        file = QFile(resource_path)
        if not file.open(QIODevice.ReadOnly):
            raise FileNotFoundError(
                f"Não foi possível abrir recurso Qt: {resource_path}."
            )

        img_data = file.readAll().data()
        file.close()
        return pygame.image.load(io.BytesIO(img_data))
