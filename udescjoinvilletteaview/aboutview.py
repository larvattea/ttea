from typing import Optional

from PySide6.QtWidgets import QDialog

# Local module import
from udescjoinvilletteaui import Ui_AboutView
from udescjoinvilletteawindow import WindowConfig


class AboutView(QDialog, Ui_AboutView, WindowConfig):
    """
    A modal dialog window displaying information about the T-TEA project.

    This class creates a modal dialog that provides details about the T-TEA
    project, including a description, logo, link to the platform, developer
    credits, and a close button.
    It inherits from `QDialog` for dialog functionality and `WindowConfig`
    for window configuration.

    Methods
    -------
    __init__(parent=None)
        Initializes the AboutView dialog with the specified parent.
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

        # === Parte dinâmica: ano e tradução ===
        current_year = datetime.now().strftime("%Y")

        # Texto traduzível
        year_text = self.tr("Desde: 2021 - {}").format(current_year)

        # HTML só da linha do ano
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
