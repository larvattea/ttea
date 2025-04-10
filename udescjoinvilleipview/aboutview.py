from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextBrowser
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from datetime import datetime
from udescjoinvilleipapp.windowconfig import WindowConfig
from udescjoinvilleiputil.pathconfig import PathConfig

class AboutView(QDialog, WindowConfig): 
    """Exibe janela de sobre como modal"""
    TITLE = "Sobre"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)  # Define como modal
        self._setup_window(
            self.TITLE,                          # title
            parent.windowIcon() if parent else None,  # icon
            WindowConfig.DECREMENT_SIZE_PERCENT, # status
            20,                                  # width
            10,                                  # height
            parent                               # parent
        )

        # Layout principal
        layout = QVBoxLayout()

        # Texto explicativo do projeto (acima)
        project_description = QLabel(
            "T-TEA é um console para exergames de Chão Interativo " 
            "voltados ao público com Transtorno do Espectro Autista (TEA), " 
            "mas não exclusivamente. Desenvolvido pela UDESC Joinville - Larva."
        )
        project_description.setWordWrap(True)
        project_description.setAlignment(Qt.AlignCenter)
        layout.addWidget(project_description)

        # Imagem centralizada
        image_path = PathConfig.image("ttealogo.png")
        pixmap = QPixmap(image_path)
        image_label = QLabel()
        image_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))  # Redimensiona mantendo proporção
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)

        # Link clicável (abaixo da imagem)
        link_label = QTextBrowser()
        link_label.setOpenExternalLinks(True)  # Permite abrir links no navegador
        link_label.setText("<a href='https://udescmove2learn.wordpress.com/2023/06/26/t-tea/'>Saiba mais sobre a Plataforma!</a>")
        link_label.setAlignment(Qt.AlignCenter)
        link_label.setMaximumHeight(30)  # Limita a altura para não ocupar muito espaço
        link_label.setToolTip("Link plataforma T-TEA")  # Tooltip para indicar que é clicável
        layout.addWidget(link_label)

        # Texto com desenvolvedores e data (abaixo do link)
        developers_text = (
            "Desenvolvido por:\n"
            "1. Marcelo da Silva Hounsell\n"
            "2. Andre Bonetto Trindade\n"
            "3. Aluno Kartea\n"
            "4. Marlow Rodrigo Becker Dickel\n"           
            "5. Luis Bet\n"
            "6. Alexandre Altair de Melo\n\n"
            f"Desde: 2021 - {datetime.now().strftime('%d/%m/%Y')}"
        )
        developers_label = QLabel(developers_text)
        developers_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(developers_label)

        # Configura o layout na janela
        self.setLayout(layout)
        self._apply_styles()

    def _apply_styles(self):
        """Aplica estilos à interface"""
        self.setStyleSheet("""
            QLabel { font-size: 14px; padding: 5px; }
            QTextBrowser { 
                font-size: 14px; 
                padding: 5px; 
                border: none; 
                background: transparent; 
            }
        """)