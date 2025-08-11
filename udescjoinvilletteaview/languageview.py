import os
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
                               QMessageBox, QPushButton, QRadioButton,
                               QVBoxLayout)

# Local module import
from udescjoinvilletteaapp import AppConfig
from udescjoinvilletteautil import PathConfig


class LanguageView(QDialog):
    """A dialog for selecting the application language with flag icons next
    to radio buttons.

    This class creates a dialog window allowing users to select a language for
    the application by choosing from a list of radio buttons, each accompanied
    by a flag icon. The selected language is applied to the application's
    interface using a translator object.

    Attributes
    ----------
    TITLE : str
        The title of the dialog window, retrieved from AppConfig.get_title().
    ICON_APP : str
        Path to the application icon, retrieved from AppConfig.ICON_APP.
    translator : QTranslator
        Translator object used to load and apply language translation files.
    radio_buttons : list[QRadioButton]
        List of radio buttons representing available languages.
    instruction_label : QLabel
        Label displaying instructions for language selection.
    languages_layout : QVBoxLayout
        Layout containing language selection radio buttons and flag icons.
    confirm_button : QPushButton
        Button to confirm the selected language.

    Methods
    -------
    setup_ui()
        Configures the user interface layout and widgets.
    apply_styles()
        Applies CSS styles to the radio buttons.
    populate_languages(languages: list[dict[str, str]])
        Populates the dialog with radio buttons for each language.
    change_language(language_code: str)
        Changes the interface language based on the selected language code.
    update_ui_texts()
        Updates the interface text elements with the current language.
    show_warning()
        Displays a warning if no language is selected.
    get_checked_language() -> Optional[str]
        Returns the code of the selected language, or None if no selection
        is made.
    """

    TITLE = AppConfig.get_title()
    ICON_APP = AppConfig.ICON_APP

    def __init__(self, translator=None, parent=None) -> None:
        """Initialize the LanguageView dialog.

        Parameters
        ----------
        translator : QTranslator, optional
            Translator object for loading language files (default is None).
        parent : QWidget, optional
            Parent widget of the dialog (default is None).

        Returns
        -------
        None
        """
        super().__init__(parent)
        self.translator = translator  # Objeto tradutor do main.py
        self.setWindowTitle(self.TITLE)
        self.setWindowIcon(QIcon(self.ICON_APP))
        self.radio_buttons: list[QRadioButton] = []
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self) -> None:
        """Configure the user interface layout and widgets.

        Sets up a vertical layout with an instruction label, a container
        for language radio buttons, and a confirm button centered horizontally.

        Returns
        -------
        None
        """
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
        """Apply CSS styles to the radio buttons.

        Styles include font size, text color, spacing, and indicator size
        for radio buttons.

        Returns
        -------
        None
        """
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
        """Populate the dialog with radio buttons for each language.

        Each language is represented by a radio button with a flag icon
        and description. The radio buttons are connected
        to the language change functionality.

        Parameters
        ----------
        languages : list[dict[str, str]]
            List of dictionaries containing language details. Each dictionary
            must have:
            - 'code': Language code (e.g., 'en', 'pt').
            - 'description': Language name (e.g., 'English', 'Português').
            - 'flag': Path to the flag icon file.

        Returns
        -------
        None
        """
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
            # Connect the toggled signal to the language switching method
            radio.toggled.connect(
                lambda checked, code=lang["code"]: (
                    self.change_language(code) if checked else None
                )
            )
            self.radio_buttons.append(radio)
            item_layout.addWidget(radio)

            item_layout.addStretch()
            self.languages_layout.addLayout(item_layout)

    def change_language(self, language_code: str) -> None:
        """Change the interface language based on the selected language code.

        Loads the translation file for the given language code and applies it
        to the application. Updates the interface texts accordingly.

        Parameters
        ----------
        language_code : str
            The code of the selected language (e.g., 'en', 'pt').

        Returns
        -------
        None
        """

        # Loads the translation file for the selected language
        translation_file = PathConfig.translation(language_code + ".qm")
        if os.path.exists(translation_file) and self.translator.load(
            translation_file
        ):
            QApplication.instance().installTranslator(self.translator)

            # Updates interface texts
            self.update_ui_texts()

    def update_ui_texts(self) -> None:
        """Update the interface text elements with the current language.

        Updates the window title, instruction label, and confirm button
        text using the current translator.

        Returns
        -------
        None
        """
        self.setWindowTitle(self.tr(AppConfig.get_title()))
        self.instruction_label.setText(
            self.tr("Selecione o idioma da aplicação:")
        )
        self.confirm_button.setText(self.tr("Confirmar"))

    def show_warning(self) -> None:
        """Display a warning message if no language is selected.

        Shows a QMessageBox with a warning indicating that a language
        must be selected.

        Returns
        -------
        None
        """
        QMessageBox.warning(
            self,
            # AppConfig.get_title(),
            self.TITLE,
            self.tr("Você deve selecionar um idioma para continuar."),
            QMessageBox.Ok,
        )

    def get_checked_language(self) -> Optional[str]:
        """Return the code of the selected language.

        Returns
        -------
        Optional[str]
            The language code of the selected radio button, or None
            if no language is selected.
        """
        for radio in self.radio_buttons:
            if radio.isChecked():
                return radio.property("language_code")
        return None
