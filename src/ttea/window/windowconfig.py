"""Window configuration helpers for the application windows.

This module provides the ``WindowConfig`` mixin, which centralizes
common window setup logic such as title, icon, sizing and centering.
"""

from typing import Optional, Tuple

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QWidget


class WindowConfig:
    """Mixin that configures title, icon, size and position of a window.

    Used together with a Qt window class (e.g. ``class MainView(
    QMainWindow, Ui_MainView, WindowConfig)``): the size can be changed
    by a percentage relative to the parent window or the screen, and the
    window is centered and gets a fixed size.

    Attributes
    ----------
    STAY_SIZE : int, class attribute
        Keep the base size (0).
    INCREMENT_SIZE_PERCENT : int, class attribute
        Increase the base size by a percentage (1).
    DECREMENT_SIZE_PERCENT : int, class attribute
        Decrease the base size by a percentage (2).

    Methods
    -------
    setup_window(title=None, icon=None, status=STAY_SIZE, ...)
        Configure title, icon, size and position.
    get_base_size(parent)
        Return the base size from the parent window or the screen.
    adjust_size(base, percent, status)
        Adjust a size by a percentage according to ``status``.
    center_window(parent=None, width=None, height=None)
        Center the window on the parent window or the screen.
    """

    STAY_SIZE = 0
    INCREMENT_SIZE_PERCENT = 1
    DECREMENT_SIZE_PERCENT = 2

    def setup_window(
        self,
        title: Optional[str] = None,
        icon: Optional[str] = None,
        status: int = STAY_SIZE,
        width: float = 0.0,
        height: float = 0.0,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Configure title, icon, size and position of the window.

        Parameters
        ----------
        title : str | None, optional
            Window title; None keeps the current one. Default is None.
        icon : str | QIcon | None, optional
            Icon file path (or icon); None keeps the current one.
            Default is None.
        status : int, optional
            ``STAY_SIZE``, ``INCREMENT_SIZE_PERCENT`` or
            ``DECREMENT_SIZE_PERCENT``. Default is ``STAY_SIZE``.
        width : float, optional
            Width change in percent (e.g. 10 means 10%). Default is 0.
        height : float, optional
            Height change in percent. Default is 0.
        parent : QWidget | None, optional
            Reference window for size and centering; None uses the
            screen. Default is None.

        Notes
        -----
        The base size comes from ``get_base_size``, each dimension is
        changed by ``adjust_size``, the window is centered with
        ``center_window`` and its size is then fixed (it cannot be
        resized).
        """
        if title is not None:
            self.setWindowTitle(title)

        if icon is not None:
            self.setWindowIcon(QIcon(icon))

        # Calculate the initial base size
        base_width, base_height = self.get_base_size(parent)

        # Adjust the size based on the status
        new_width = self.adjust_size(base_width, width, status)
        new_height = self.adjust_size(base_height, height, status)

        # Set the size and center the window
        self.center_window(parent, new_width, new_height)
        self.setFixedSize(new_width, new_height)

    def get_base_size(
        self, parent: Optional[QWidget] = None
    ) -> Tuple[int, int]:
        """Return the base size from the parent window or the screen.

        Parameters
        ----------
        parent : QWidget | None, optional
            Reference window. Default is None.

        Returns
        -------
        tuple[int, int]
            The parent's width and height, or half the width and height
            of the primary screen when there is no parent (or it has no
            ``geometry``).
        """
        if parent is not None and hasattr(parent, "geometry"):
            parent_geo = parent.geometry()
            return parent_geo.width(), parent_geo.height()
        screen = QApplication.primaryScreen().geometry()
        return screen.width() // 2, screen.height() // 2

    def adjust_size(self, base: float, percent: float, status: int) -> float:
        """Adjust a size by a percentage according to ``status``.

        Parameters
        ----------
        base : float
            Base size (width or height) in pixels.
        percent : float
            Percentage to add or remove (e.g. 10 for 10%).
        status : int
            ``STAY_SIZE``, ``INCREMENT_SIZE_PERCENT`` or
            ``DECREMENT_SIZE_PERCENT``.

        Returns
        -------
        float
            The adjusted size; ``base`` unchanged when ``percent`` is 0
            or negative or ``status`` is ``STAY_SIZE`` (or unknown).

        Examples
        --------
        >>> cfg = WindowConfig()
        >>> cfg.adjust_size(800, 10, cfg.DECREMENT_SIZE_PERCENT)
        720.0
        >>> cfg.adjust_size(800, 25, cfg.INCREMENT_SIZE_PERCENT)
        1000.0
        >>> cfg.adjust_size(800, 10, cfg.STAY_SIZE)
        800
        """
        if percent <= 0:
            return base
        if status == self.INCREMENT_SIZE_PERCENT:
            return base + (base * percent / 100)
        if status == self.DECREMENT_SIZE_PERCENT:
            return base - (base * percent / 100)
        return base

    def center_window(
        self,
        parent: Optional[QWidget] = None,
        width: Optional[float] = None,
        height: Optional[float] = None,
    ) -> None:
        """Center the window on the parent window or the screen.

        Parameters
        ----------
        parent : QWidget | None, optional
            Reference window; None (or no ``geometry``) uses the primary
            screen. Default is None.
        width : float | None, optional
            Window width in pixels; None uses the current width. Default
            is None.
        height : float | None, optional
            Window height in pixels; None uses the current height.
            Default is None.

        Notes
        -----
        The position and size are set with ``setGeometry``. On the
        screen, the position is computed from the screen size only, so
        the screen is assumed to start at (0, 0).
        """
        if width is None:
            width = self.width()
        if height is None:
            height = self.height()

        if parent is not None and hasattr(parent, "geometry"):
            parent_geo = parent.geometry()
            x = parent_geo.x() + (parent_geo.width() - width) // 2
            y = parent_geo.y() + (parent_geo.height() - height) // 2
        else:
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - width) // 2
            y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)
