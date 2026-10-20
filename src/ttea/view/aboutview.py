"""About dialog view for the T-TEA application.

This module defines the ``AboutView`` dialog, which displays project
information, developer credits and the current year in a Qt modal
window.
"""

from datetime import datetime
from typing import Optional

from PySide6.QtWidgets import QDialog

from ttea.ui import Ui_AboutView
from ttea.window import WindowConfig


class AboutView(QDialog, Ui_AboutView, WindowConfig):
    """Modal dialog showing information about the T-TEA project.

    Displays the project description, logo, platform link, developer
    credits and a close button.

    Parameters
    ----------
    parent : QDialog | None, optional
        Parent widget. Default is None.

    Notes
    -----
    The window is fixed at 25% narrower than the parent. A line "Desde:
    2021 - <current year>" (translated with ``self.tr()``) is appended
    to the HTML of ``lbl_developer``.
    """

    def __init__(
        self,
        parent: Optional[QDialog] = None,
    ) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.setup_window(
            None,
            None,
            WindowConfig.DECREMENT_SIZE_PERCENT,  # status
            25,  # width
            0,  # height
            parent,  # parent
        )

        # Dynamic part: current year, translated
        current_year = datetime.now().strftime("%Y")

        year_text = self.tr("Desde: 2021 - {}").format(current_year)

        # HTML for the year line only
        year_html = f"""
        <p align="center" style="margin-top:12px; margin-bottom:12px;">
        <span style="font-size:10pt; font-weight:700; font-style:italic;">
            {year_text}
        </span>
        </p>
        """
        base_html = self.lbl_developer.toHtml()

        updated_html = base_html.replace("</body>", year_html + "</body>")

        self.lbl_developer.setHtml(updated_html)
