"""Loading, scaling and drawing of game images (pygame)."""

import io
from typing import Literal

import pygame
from PySide6.QtCore import QFile, QIODevice

from ttea.games.kartea.gameutil.alphablit import alpha_blit
from ttea.games.kartea.util import KarteaPathConfig


class Image:
    """Utility class for loading, scaling and drawing images.

    Supports physical paths and Qt resources (.qrc).

    Attributes
    ----------
    IMAGE_SIZE_DEFAULT_NAME : str, class attribute
        ``size`` value that keeps the original size ("default").
    IMAGE_CONVERT_ALPHA, IMAGE_CONVERT_BASE : str, class attribute
        Pixel format conversion: ``convert_alpha()`` ("alpha") or
        ``convert()`` ("base").
    IMAGE_POS_TOP_LEFT, IMAGE_POS_CENTER : str, class attribute
        Anchor modes of ``draw`` ("top_left", "center").
    IMAGE_POS_BOTTOM_CENTER : str, class attribute
        Anchor mode of ``draw`` ("bottom_center").
    _cache : dict, class attribute
        Decoded and converted images (before scaling), by (path,
        conversion, flip). Avoids rereading the file/QRC every frame in
        Target.move and kill().
    """

    IMAGE_SIZE_DEFAULT_NAME = "default"
    IMAGE_CONVERT_ALPHA = "alpha"
    IMAGE_CONVERT_BASE: str = "base"

    IMAGE_POS_TOP_LEFT = "top_left"
    IMAGE_POS_CENTER = "center"
    IMAGE_POS_BOTTOM_CENTER = "bottom_center"

    _cache: dict = {}

    @staticmethod
    def load(
        img_name: str,
        size: Literal["default"] | tuple[int, int] = IMAGE_SIZE_DEFAULT_NAME,
        convert: str = IMAGE_CONVERT_ALPHA,
        flip: bool = False,
    ) -> pygame.Surface:
        """Load an image (file or Qt), converted and scaled.

        Parameters
        ----------
        img_name : str
            QRC alias, ``:/...`` path or file path.
        size : "default" | tuple[int, int], optional
            Target size; "default" keeps the original size.
        convert : str, optional
            IMAGE_CONVERT_ALPHA (default) or IMAGE_CONVERT_BASE; any
            other value converts with alpha.
        flip : bool, optional
            Mirror horizontally.

        Returns
        -------
        pygame.Surface
            A new surface (a copy, so callers may change it without
            affecting the cache); a magenta 32x32 surface if the image
            cannot be loaded.

        Notes
        -----
        Requires an initialized pygame display (``convert``). Errors are
        printed to the console, not raised.
        """
        full_path = KarteaPathConfig.game_builtin_image(img_name)

        if (img_name) and (not full_path):
            full_path = img_name

        if not full_path:
            return Image._fallback_surface()

        try:
            cache_key = (full_path, convert, flip)
            base = Image._cache.get(cache_key)

            if base is None:
                if full_path.startswith(":/"):
                    base = Image._load_from_qt_resource(full_path)
                else:
                    base = pygame.image.load(full_path)

                # Pixel format conversion
                if convert == Image.IMAGE_CONVERT_BASE:
                    base = base.convert()
                else:
                    base = base.convert_alpha()

                # Transformations
                if flip:
                    base = pygame.transform.flip(base, True, False)

                Image._cache[cache_key] = base

            if (
                size != Image.IMAGE_SIZE_DEFAULT_NAME
                and isinstance(size, (tuple, list))
                and len(size) == 2
            ):
                # Image.scale already returns a new Surface
                return Image.scale(base, size)

            # Copy: callers may change the Surface (alpha etc.) without
            # affecting the cache.
            return base.copy()
        except Exception as e:
            print(f"[Image.load] Erro ao carregar '{img_name}': {e}.")
            return Image._fallback_surface()

    @staticmethod
    def _load_from_qt_resource(resource_path: str) -> pygame.Surface:
        """Load a Qt resource via QFile.

        Raises
        ------
        FileNotFoundError
            If the resource cannot be opened.
        """
        file = QFile(resource_path)
        if not file.open(QIODevice.ReadOnly):
            raise FileNotFoundError(
                f"Não foi possível abrir recurso Qt: {resource_path}."
            )

        img_data = file.readAll().data()
        file.close()
        return pygame.image.load(io.BytesIO(img_data))

    @staticmethod
    def scale(img: pygame.Surface, size: tuple[int, int]) -> pygame.Surface:
        """Resize with smoothscale and a safe minimum size.

        Parameters
        ----------
        img : pygame.Surface
            Image to resize.
        size : tuple[int, int]
            Target size; each side is at least 1 px.

        Returns
        -------
        pygame.Surface
            A new resized surface.
        """
        width = max(1, int(size[0]))
        height = max(1, int(size[1]))
        return pygame.transform.smoothscale(img, (width, height))

    @staticmethod
    def draw(
        surface: pygame.Surface,
        img: pygame.Surface,
        pos: tuple[int, int],
        pos_mode: str = IMAGE_POS_TOP_LEFT,
    ):
        """Draw the image with different anchor modes.

        Parameters
        ----------
        surface : pygame.Surface
            Surface drawn on.
        img : pygame.Surface
            Image to draw.
        pos : tuple[int, int]
            Anchor position (x, y).
        pos_mode : str, optional
            IMAGE_POS_TOP_LEFT (default), IMAGE_POS_CENTER or
            IMAGE_POS_BOTTOM_CENTER (case-insensitive).

        Raises
        ------
        ValueError
            If ``pos`` is not a tuple/list with exactly 2 values.
        """
        if not isinstance(pos, (tuple, list)) or len(pos) != 2:
            raise ValueError(
                "POS deve ser uma tupla/lista com exatamente 2 valores (x, y)."
            )

        render_pos = list(pos)
        mode = pos_mode.lower()

        if mode == Image.IMAGE_POS_CENTER:
            render_pos[0] -= img.get_width() // 2
            render_pos[1] -= img.get_height() // 2
        elif mode == Image.IMAGE_POS_BOTTOM_CENTER:
            render_pos[0] -= img.get_width() // 2
            render_pos[1] -= img.get_height()

        alpha_blit(surface, img, render_pos)

    @staticmethod
    def _fallback_surface() -> pygame.Surface:
        """Return a magenta 32x32 surface marking a missing image."""
        surf = pygame.Surface((32, 32))
        surf.fill((255, 0, 255))
        return surf
