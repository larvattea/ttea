from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QDialog, QLabel, QPushButton, QTextBrowser,
                               QVBoxLayout)

# Local module import
from udescjoinvilletteaapp import AppConfig
from udescjoinvilletteawindow import WindowConfig


class AboutView(QDialog, WindowConfig):
    """
    A modal dialog window displaying information about the T-TEA project.

    This class creates a modal dialog that provides details about the T-TEA
    project, including a description, logo, link to the platform, developer
    credits, and a close button.
    It inherits from `QDialog` for dialog functionality and `WindowConfig`
    for window configuration.

    Attributes
    ----------
    translator : object or None
        Translator object inherited from the parent widget for
        internationalization. Set to None if the parent does not have
        a translator.
    layout : QVBoxLayout
        The main vertical layout organizing the dialog's widgets.
    project_description : QLabel
        Label displaying the project description with word wrap and centered
        alignment.
    image_label : QLabel
        Label displaying the scaled T-TEA logo image, centered in the dialog.
    link_label : QTextBrowser
        Text browser widget containing a clickable link to the T-TEA platform.
    developers_label : QTextBrowser
        Text browser widget listing the developers and project timeline.
    ok_button : QPushButton
        Button to close the dialog, connected to the `accept` method.

    Methods
    -------
    __init__(parent=None)
        Initializes the AboutView dialog with the specified parent.
    _apply_styles()
        Applies custom styles to the dialog's widgets.
    """

    def __init__(self, parent=None) -> None:
        """
        Initialize the AboutView dialog.

        Sets up the modal dialog with a project description, logo, link,
        developer credits, and an OK button.
        Configures the window using inherited `WindowConfig` methods.

        Parameters
        ----------
        parent : QWidget, optional
            The parent widget for the dialog. Defaults to None.

        Returns
        -------
        None

        Notes
        -----
        - The dialog is set as modal, blocking interaction with the parent
        until closed.
        - The window title, icon, and size are configured using the
        `setup_window` method from the `WindowConfig` parent class.
        - Widgets are arranged in a vertical layout with consistent spacing.
        - The project logo is scaled to a fixed width of 200 pixels for
        consistent display.
        - The link and developer text use `QTextBrowser` for HTML support and
        clickable links.
        """
        super().__init__(parent)
        self.setModal(True)  # Set as modal
        # self.translator = (
        #    parent.translator if hasattr(parent, "translator") else None
        # )
        self.setup_window(
            parent.get_title(),  # title
            parent.windowIcon() if parent else None,  # icon
            WindowConfig.DECREMENT_SIZE_PERCENT,  # status
            25,  # width
            0,  # height
            parent,  # parent
        )

        # Main layout
        layout = QVBoxLayout()

        # Project explanatory text
        project_description = QLabel(
            self.tr(
                "<b>T-TEA</b> é um console para exergames de Chão Interativo "
                "voltados ao público com Transtorno do Espectro Autista (TEA), "
                "mas não exclusivamente. Desenvolvido pela UDESC Joinville - Larva."
            )
        )
        project_description.setWordWrap(True)
        project_description.setAlignment(Qt.AlignCenter)
        layout.addWidget(project_description)
        layout.addSpacing(10)  # Espaço reduzido para consistência

        # Image occupying available area
        image_path = AppConfig.LOGO_APP
        pixmap = QPixmap(image_path)
        image_label = QLabel()
        image_label.setPixmap(
            pixmap.scaledToWidth(200, Qt.SmoothTransformation)
        )  # Scale image to fixed size
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label, stretch=1)  # Prioridade à imagem
        layout.addSpacing(10)  # Espaço consistente após imagem

        # Clickable link
        link_label = QTextBrowser()
        link_label.setOpenExternalLinks(True)
        link_label.setText(
            (
                "<a href='https://udescmove2learn.wordpress.com/2023/06/26/t-tea/'>{}</a>"
            ).format(self.tr("Saiba mais sobre a Plataforma!"))
        )
        link_label.setAlignment(Qt.AlignCenter)
        link_label.setFixedHeight(40)  # Fixed height for consistency
        link_label.setToolTip(self.tr("Link plataforma T-TEA"))
        layout.addWidget(link_label)
        layout.addSpacing(10)  # Consistent space after link

        # Text with developers and date
        developers_text = (
            "<b>{}</b><br>"
            "<span style='font-size: 10px;'>"
            "1. Marcelo da Silva Hounsell<br>"
            "2. Andre Bonetto Trindade<br>"
            "3. Gabriel Brunelli Pereira<br>"
            "4. Marlow Rodrigo Becker Dickel<br>"
            "5. Luis Eduardo Bet<br>"
            "6. Alexandre Altair de Melo<br>"
            "<br>"
            "<i>{}: 2021 - {}</i>"
            "</span>"
        ).format(
            self.tr("Desenvolvido por:"),
            self.tr("Desde"),
            datetime.now().strftime("%Y"),
        )

        developers_label = QTextBrowser()
        developers_label.setHtml(developers_text)
        developers_label.setAlignment(Qt.AlignCenter)
        developers_label.setFixedHeight(
            120
        )  # Fixed height to prevent excessive expansion
        layout.addWidget(developers_label)
        layout.addSpacing(10)  # Espaço consistente antes do botão

        # Centralized OK button
        ok_button = QPushButton("OK")
        ok_button.setFixedWidth(100)
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button, alignment=Qt.AlignCenter)

        # Flexible space at the end
        layout.addStretch(1)  # Keeps the layout balanced

        # Sets the layout in the window
        self.setLayout(layout)
        self._apply_styles()

    def _apply_styles(self) -> None:
        """
        Apply custom styles to the dialog's widgets.

        Configures the appearance of `QLabel`, `QTextBrowser`,
        and `QPushButton` widgets using a stylesheet to ensure consistent
        font sizes, padding, and margins.

        Notes
        -----
        - The stylesheet sets a uniform font size of 14px for most widgets.
        - `QTextBrowser` is styled to be transparent with no border for a
        cleaner look.
        - Padding and margins are applied to ensure consistent spacing.
        """
        self.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                padding: 5px;
                margin: 0px;
            }
            QTextBrowser {
                font-size: 14px;
                padding: 5px;
                margin: 0px;
                border: none;
                background: transparent;
            }
            QPushButton {
                font-size: 14px;
                padding: 5px;
                margin: 5px;
            }
        """
        )
