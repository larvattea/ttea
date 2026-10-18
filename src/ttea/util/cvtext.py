"""Draw Unicode text on OpenCV frames and name OpenCV windows.

OpenCV's ``cv2.putText`` uses Hershey fonts, which only cover ASCII,
so accented letters (é, ó, ñ, ç) are drawn as "??". On Windows the
HighGUI window title is also passed through the ANSI code page, so a
UTF-8 title shows broken characters. This module draws the text with
Pillow and sets the window title with the Unicode Windows API.
"""

import sys
import unicodedata
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# TrueType fonts tried in order: Windows, Linux, macOS.
_FONT_CANDIDATES = (
    "arial.ttf",
    "DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
)


class CvText:
    """Unicode text and window titles for OpenCV (HighGUI) windows.

    Notes
    -----
    The window *name* is the key that every HighGUI call uses
    (``imshow``, ``destroyWindow``, ``setMouseCallback``...). It is
    kept ASCII by ``window_name`` so that it is the same in every
    platform; the text the user sees is set apart with
    ``set_window_title``.

    Examples
    --------
    >>> CvText.window_name("Pantalla de monitorización")
    'Pantalla de monitorizacion'
    """

    @staticmethod
    def window_name(title: str) -> str:
        """Return an ASCII-only window name derived from ``title``.

        Parameters
        ----------
        title : str
            Translated window title, possibly with accents.

        Returns
        -------
        str
            ``title`` without diacritics and non-ASCII characters.
        """
        decomposed = unicodedata.normalize("NFKD", title)
        return decomposed.encode("ascii", "ignore").decode("ascii")

    @staticmethod
    def set_window_title(name: str, title: str) -> None:
        """Show ``title`` (Unicode) in the window called ``name``.

        Parameters
        ----------
        name : str
            Window name given to ``cv2.namedWindow`` (see
            ``window_name``).
        title : str
            Text to show in the title bar.

        Notes
        -----
        On Windows the title is set with ``SetWindowTextW``, because
        ``cv2.setWindowTitle`` uses the ANSI API there. If the window
        is not found, the ASCII name stays as the title. On other
        platforms ``cv2.setWindowTitle`` already handles UTF-8.
        """
        if name == title:
            return
        if sys.platform == "win32":
            import ctypes  # noqa: PLC0415 - Windows only

            user32 = ctypes.windll.user32
            hwnd = user32.FindWindowW(None, name)
            if hwnd:
                user32.SetWindowTextW(hwnd, title)
            return
        try:
            cv2.setWindowTitle(name, title)
        except cv2.error:
            pass

    @staticmethod
    @lru_cache(maxsize=8)
    def font(size: int) -> ImageFont.ImageFont:
        """Return a TrueType font of ``size`` pixels (cached).

        Parameters
        ----------
        size : int
            Font size in pixels.

        Returns
        -------
        PIL.ImageFont.ImageFont
            First available font of ``_FONT_CANDIDATES`` or Pillow's
            default font.
        """
        for candidate in _FONT_CANDIDATES:
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                continue
        return ImageFont.load_default(size)

    @staticmethod
    def wrap(text: str, font: ImageFont.ImageFont, max_width: int) -> list:
        """Split ``text`` into lines no wider than ``max_width`` pixels.

        Parameters
        ----------
        text : str
            Text to split; existing line breaks are kept.
        font : PIL.ImageFont.ImageFont
            Font used to measure the text.
        max_width : int
            Maximum line width in pixels.

        Returns
        -------
        list of str
            Lines of text. A single word wider than ``max_width`` is
            kept on its own line.
        """
        lines = []
        for paragraph in text.split("\n"):
            current = ""
            for word in paragraph.split(" "):
                candidate = f"{current} {word}" if current else word
                if current and font.getlength(candidate) > max_width:
                    lines.append(current)
                    current = word
                else:
                    current = candidate
            lines.append(current)
        return lines

    @staticmethod
    def draw_lines(
        img: np.ndarray,
        lines,
        origin: tuple = (20, 20),
        font_size: int = 20,
        color: tuple = (0, 255, 255),
        outline_color: tuple = (0, 0, 0),
        outline_width: int = 2,
        line_spacing: int = 8,
        margin: int = 20,
    ) -> np.ndarray:
        """Draw lines of Unicode text on a BGR frame, wrapping to fit.

        Parameters
        ----------
        img : numpy.ndarray
            BGR frame (``H x W x 3``, ``uint8``). It is not modified.
        lines : iterable of str
            Lines to draw, top to bottom.
        origin : tuple of int, default (20, 20)
            Top-left corner ``(x, y)`` of the first line, in pixels.
        font_size : int, default 20
            Font size in pixels.
        color : tuple of int, default (0, 255, 255)
            Text color in BGR (yellow by default).
        outline_color : tuple of int, default (0, 0, 0)
            Outline color in BGR, drawn around each letter for contrast.
        outline_width : int, default 2
            Outline width in pixels; 0 draws no outline.
        line_spacing : int, default 8
            Extra space between lines, in pixels.
        margin : int, default 20
            Right margin kept free when wrapping, in pixels.

        Returns
        -------
        numpy.ndarray
            New BGR frame with the text drawn.
        """
        font = CvText.font(font_size)
        x, y = origin
        max_width = max(img.shape[1] - x - margin, font_size)
        line_height = font_size + line_spacing

        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)
        for line in lines:
            for part in CvText.wrap(line, font, max_width):
                draw.text(
                    (x, y),
                    part,
                    font=font,
                    fill=tuple(color[::-1]),
                    stroke_width=outline_width,
                    stroke_fill=tuple(outline_color[::-1]),
                )
                y += line_height
        return cv2.cvtColor(np.asarray(pil_img), cv2.COLOR_RGB2BGR)
