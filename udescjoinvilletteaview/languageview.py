from typing import Dict, List, Optional

from PySide6.QtCore import Qt, QTranslator, QSize
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QWidget,
)

from udescjoinvilletteaapp import AppConfig
from udescjoinvilletteaui import Ui_LanguageView
from udescjoinvilletteawindow import WindowConfig


class LanguageView(QDialog, Ui_LanguageView, WindowConfig):
    """View para seleção de idioma usando QComboBox com ícones de bandeiras."""

    def __init__(self, parent: Optional[QWidget] = None):
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
        self.btn_confirm.setDefault(True)

        # Configura o ComboBox para mostrar ícones e texto
        self.comboBox.setIconSize(QSize(32, 32))
        self.comboBox.setStyleSheet("QComboBox { padding-left: 10px; }")

    def populate_languages(self, languages: List[Dict[str, str]]) -> None:
        """Preenche o QComboBox com os idiomas, exibindo bandeira + descrição."""
        self.comboBox.clear()

        for lang in languages:
            pixmap = QPixmap(lang["flag"])
            icon = QIcon()

            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                icon.addPixmap(scaled_pixmap)
            else:
                icon = QIcon()  # ícone vazio se a bandeira não carregar

            # Armazena o código do idioma como userData
            self.comboBox.addItem(icon, lang["description"], lang["code"])

    def set_preselected_language(self, code: str) -> None:
        """Seleciona o idioma previamente salvo no ComboBox."""
        for i in range(self.comboBox.count()):
            if self.comboBox.itemData(i) == code:
                self.comboBox.setCurrentIndex(i)
                break

    def get_checked_language(self) -> Optional[str]:
        """Retorna o código do idioma selecionado."""
        if self.comboBox.currentIndex() == -1:
            return None
        return self.comboBox.currentData()

    def show_warning(self) -> None:
        from udescjoinvilletteautil import MessageService

        MessageService(self).warning(
            self.tr("Por favor, selecione um idioma.")
        )

    # Em languageview.py
    def apply_translator(self, translator: QTranslator):
        app = QApplication.instance()
        app.installTranslator(translator)
        self.retranslateUi(self)
