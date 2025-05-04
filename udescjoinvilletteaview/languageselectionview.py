import sys
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QRadioButton, QPushButton, QLabel, QHBoxLayout, QMessageBox
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QSize, Qt
from udescjoinvilletteaapp.tteaapp import TTeaApp
from udescjoinvilletteautil.pathconfig import PathConfig
from udescjoinvilletteaapp.windowconfig import WindowConfig

class LanguageSelectionView(QDialog, WindowConfig):
    """Diálogo para seleção de idioma com bandeiras alinhadas ao lado de radio buttons"""
    LANGUAGES = [
        {
            "code": "pt",
            "description": "Português",
            "flag": PathConfig.image("brazil.png"),
        },
        {
            "code": "en",
            "description": "English",
            "flag": PathConfig.image("usa.png"),
        }
    ]

    TITLE = "Seleção de Idioma / Language Selection"
    ICON_APP = PathConfig.icon("larva.ico")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_window(
            self.TITLE,                          # title
            self.ICON_APP,                      # icon
            WindowConfig.DECREMENT_SIZE_PERCENT, # status
            45,                                  # width
            55,                                  # height
            parent                               # parent
        )
        self.selected_language = None
        self.radio_buttons = []
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Instrução
        label = QLabel("Selecione o idioma da aplicação / Select the application language:")
        label.setObjectName("instructionLabel")
        main_layout.addWidget(label)

        # Layout para os radio buttons
        self.languages_layout = QVBoxLayout()
        self.languages_layout.setSpacing(10)
        main_layout.addLayout(self.languages_layout)

        # Preencher com radio buttons para cada idioma
        for lang in self.LANGUAGES:
            item_layout = QHBoxLayout()
            item_layout.setSpacing(12)

            # Bandeira
            flag_label = QLabel()
            flag_pixmap = QPixmap(lang["flag"]).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            flag_label.setPixmap(flag_pixmap)
            flag_label.setFixedSize(24, 24)
            flag_label.setAlignment(Qt.AlignVCenter)
            item_layout.addWidget(flag_label)

            # Radio button com descrição
            radio = QRadioButton(lang["description"])
            radio.setProperty("language_code", lang["code"])
            radio.setObjectName("languageRadio")
            self.radio_buttons.append(radio)
            item_layout.addWidget(radio)

            item_layout.addStretch()
            self.languages_layout.addLayout(item_layout)

        main_layout.addStretch()

        # Botão de confirmação
        confirm_button = QPushButton("Confirmar / Confirm")
        confirm_button.setObjectName("confirmButton")
        confirm_button.clicked.connect(self.accept)
        confirm_button.setFixedWidth(150)
        main_layout.addWidget(confirm_button, alignment=Qt.AlignHCenter)

    def apply_styles(self):
        """Apply stylesheet for radio buttons"""
        self.setStyleSheet("""
            QRadioButton#languageRadio {
                font-size: 13px;
                color: #333333;
                spacing: 8px;
            }
            QRadioButton#languageRadio::indicator {
                width: 16px;
                height: 16px;
            }
        """)

    def accept(self):
        """Salva o idioma selecionado e fecha o diálogo com aceitação"""
        for radio in self.radio_buttons:
            if radio.isChecked():
                self.selected_language = radio.property("language_code")
                break
        if self.selected_language:
            super().accept()  # Fecha o diálogo com resultado 'Accepted'

    def get_selected_language(self):
        """Retorna o código do idioma selecionado"""
        return self.selected_language

    def closeEvent(self, event):
        """Sobrescreve o evento de fechamento para exibir um aviso e controlar o fechamento"""
        # Verifica se um idioma foi selecionado
        for radio in self.radio_buttons:
            if radio.isChecked():
                self.selected_language = radio.property("language_code")
                break

        if not self.selected_language:
            # Exibe mensagem de aviso
            QMessageBox.warning(
                self,
                "Aviso / Warning",
                "Você deve selecionar um idioma para continuar.\n"
                "You must select a language to proceed.",
                QMessageBox.Ok
            )
            # Impede o fechamento da janela
            event.ignore()
        else:
            # Aceita o diálogo para prosseguir ao menu principal
            self.accept()  # Fecha o diálogo com resultado 'Accepted'
            event.accept()  # Garante que o evento de fechamento seja aceito