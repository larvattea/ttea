"""Language selection dialog."""

from typing import Dict, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QIcon, QPixmap
from PySide6.QtWidgets import QDialog, QWidget

from ttea.ui import Ui_LanguageView
from ttea.window import WindowConfig


class LanguageView(QDialog, Ui_LanguageView, WindowConfig):
    """Dialog to choose the application language.

    Selecting a language previews it; confirming or closing applies it.
    The logic is in ``LanguageController``.

    Parameters
    ----------
    parent : QWidget | None, optional
        Parent widget. Default is None.

    Attributes
    ----------
    controller : LanguageController
        Controller of the dialog.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        from ttea.controller import LanguageController

        super().__init__(parent)
        self.setupUi(self)

        self.setup_window(
            None,
            None,
            WindowConfig.DECREMENT_SIZE_PERCENT,
            60,
            60,
            parent,
        )

        self.controller = LanguageController(self)

        self.pb_ok.clicked.connect(self.controller.handle_confirm)
        self.cbx_language.currentIndexChanged.connect(
            self.controller.handle_preview
        )

    def populate_languages(self, languages: List[Dict[str, str]]) -> None:
        """Fill the language combo box.

        Parameters
        ----------
        languages : list[dict[str, str]]
            Languages with ``"code"``, ``"description"`` and ``"flag"``
            (Qt resource path of a flag, shown as a 32 px icon).
        """
        self.cbx_language.clear()
        for lang in languages:
            pixmap = QPixmap(lang["flag"])
            icon = QIcon()
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                icon.addPixmap(scaled)
            self.cbx_language.addItem(icon, lang["description"], lang["code"])

    def set_preselected_language(self, code: str) -> None:
        """Select the language with the given code, if listed.

        Parameters
        ----------
        code : str
            Language code, e.g. ``"pt_BR"``.
        """
        for i in range(self.cbx_language.count()):
            if self.cbx_language.itemData(i) == code:
                self.cbx_language.setCurrentIndex(i)
                break

    def get_selected_language(self) -> Optional[str]:
        """Return the code of the selected language.

        Returns
        -------
        str | None
            The code, or None when nothing is selected.
        """
        if self.cbx_language.currentIndex() == -1:
            return None
        return self.cbx_language.currentData()

    def show_warning(self) -> None:
        """Ask the user to select a language (translated warning)."""
        from ttea.util import MessageService

        MessageService(self).warning(
            self.tr("Por favor, selecione um idioma.")
        )

    def closeEvent(self, event: QCloseEvent) -> None:
        """Let the controller apply the language or keep the dialog.

        Parameters
        ----------
        event : QCloseEvent
            Close event, accepted or ignored by
            ``LanguageController.handle_close_event``.
        """
        self.controller.handle_close_event(event)
