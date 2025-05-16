import os
from typing import Optional
from PySide6.QtCore import Qt, QTranslator
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QMessageBox,
    QApplication,  # Added import for QApplication
)

from udescjoinvilletteautil.pathconfig import PathConfig
from udescjoinvilletteaapp.tteaapp import TTeaApp

class LanguageView(QDialog):
    """Diálogo para seleção de idioma com bandeiras alinhadas ao lado de botões de rádio."""

    TITLE = TTeaApp.get_title()
    ICON_APP = PathConfig.icon("larva.ico")

    def __init__(self, translator=None, parent=None) -> None:
        super().__init__(parent)
        self.translator = translator  # Objeto tradutor do main.py
        self.setWindowTitle(self.TITLE)
        self.setWindowIcon(QIcon(self.ICON_APP))
        self.radio_buttons: list[QRadioButton] = []
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self) -> None:
        """Configura a interface do usuário."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.instruction_label = QLabel(
            self.tr("Selecione o idioma da aplicação:")
        )
        self.instruction_label.setObjectName("instructionLabel")
        main_layout.addWidget(self.instruction_label)

        self.languages_layout = QVBoxLayout()
        self.languages_layout.setSpacing(10)
        main_layout.addLayout(self.languages_layout)

        main_layout.addStretch()

        self.confirm_button = QPushButton(self.tr("Confirmar"))
        self.confirm_button.setObjectName("confirmButton")
        self.confirm_button.setFixedWidth(150)
        main_layout.addWidget(self.confirm_button, alignment=Qt.AlignHCenter)

    def apply_styles(self) -> None:
        """Aplica estilos CSS aos botões de rádio."""
        self.setStyleSheet(
            """
            QRadioButton#languageRadio {
                font-size: 13px;
                color: #333333;
                spacing: 8px;
            }
            QRadioButton#languageRadio::indicator {
                width: 16px;
                height: 16px;
            }
            """
        )

    def populate_languages(self, languages: list[dict[str, str]]) -> None:
        """Preenche a interface com botões de rádio para cada idioma."""
        for lang in languages:
            item_layout = QHBoxLayout()
            item_layout.setSpacing(12)

            flag_label = QLabel()
            flag_pixmap = QPixmap(lang["flag"]).scaled(
                24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            flag_label.setPixmap(flag_pixmap)
            flag_label.setFixedSize(24, 24)
            flag_label.setAlignment(Qt.AlignVCenter)
            item_layout.addWidget(flag_label)

            radio = QRadioButton(lang["description"])
            radio.setProperty("language_code", lang["code"])
            radio.setObjectName("languageRadio")
            # Conecta o sinal toggled ao método de troca de idioma
            radio.toggled.connect(lambda checked, code=lang["code"]: self.change_language(code) if checked else None)
            self.radio_buttons.append(radio)
            item_layout.addWidget(radio)

            item_layout.addStretch()
            self.languages_layout.addLayout(item_layout)

    def change_language(self, language_code: str) -> None:
        """Troca o idioma da interface quando um radio button é selecionado."""

        # Carrega o arquivo de tradução para o idioma selecionado
        translation_file = PathConfig.translation(language_code + ".qm")
        if os.path.exists(translation_file) and self.translator.load(translation_file):
            QApplication.instance().installTranslator(self.translator)

            # Atualiza os textos da interface
            self.update_ui_texts()

    def update_ui_texts(self) -> None:
        """Atualiza os textos da interface com o idioma atual."""
        self.setWindowTitle(self.tr(TTeaApp.get_title()))
        self.instruction_label.setText(self.tr("Selecione o idioma da aplicação:"))
        self.confirm_button.setText(self.tr("Confirmar"))

    def show_warning(self) -> None:
        """Exibe uma mensagem de aviso se nenhum idioma for selecionado."""
        QMessageBox.warning(
            self,
            TTeaApp.get_title(),
            self.tr("Você deve selecionar um idioma para continuar."),
            QMessageBox.Ok,
        )

    def get_checked_language(self) -> Optional[str]:
        """Retorna o código do idioma selecionado."""
        for radio in self.radio_buttons:
            if radio.isChecked():
                return radio.property("language_code")
        return None