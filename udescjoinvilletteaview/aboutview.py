from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextBrowser, QPushButton
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from datetime import datetime
from udescjoinvilletteaapp.windowconfig import WindowConfig
from udescjoinvilletteautil.pathconfig import PathConfig

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
            25,                                  # width
            0,                                  # height
            parent                               # parent
        )

        # Layout principal
        layout = QVBoxLayout()

        # Texto explicativo do projeto
        project_description = QLabel(
            "<b>T-TEA</b> é um console para exergames de Chão Interativo "
            "voltados ao público com Transtorno do Espectro Autista (TEA), "
            "mas não exclusivamente. Desenvolvido pela UDESC Joinville - Larva."
        )
        project_description.setWordWrap(True)
        project_description.setAlignment(Qt.AlignCenter)
        layout.addWidget(project_description)
        layout.addSpacing(10)  # Espaço reduzido para consistência

        # Imagem ocupando área disponível
        image_path = PathConfig.image("ttealogo.png")
        pixmap = QPixmap(image_path)
        image_label = QLabel()
        image_label.setPixmap(pixmap.scaledToWidth(200, Qt.SmoothTransformation))  # Escala imagem para tamanho fixo
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label, stretch=1)  # Prioridade à imagem
        layout.addSpacing(10)  # Espaço consistente após imagem

        # Link clicável
        link_label = QTextBrowser()
        link_label.setOpenExternalLinks(True)
        link_label.setText("<a href='https://udescmove2learn.wordpress.com/2023/06/26/t-tea/'>Saiba mais sobre a Plataforma!</a>")
        link_label.setAlignment(Qt.AlignCenter)
        link_label.setFixedHeight(40)  # Altura fixa para consistência
        link_label.setToolTip("Link plataforma T-TEA")
        layout.addWidget(link_label)
        layout.addSpacing(10)  # Espaço consistente após o link

        # Texto com desenvolvedores e data
        developers_text = (
            "<b>Desenvolvido por:</b><br>"
            "<span style='font-size: 10px;'>"
            "1. Marcelo da Silva Hounsell<br>"
            "2. Andre Bonetto Trindade<br>"
            "3. Gabriel Brunelli Pereira<br>"
            "4. Marlow Rodrigo Becker Dickel<br>"
            "5. Luis Eduardo Bet<br>"
            "6. Alexandre Altair de Melo<br>"
            "<br>"
            f"<i>Desde: 2021 - {datetime.now().strftime('%Y')}</i>"
            "</span>"
        )
        developers_label = QTextBrowser()
        developers_label.setHtml(developers_text)
        developers_label.setAlignment(Qt.AlignCenter)
        developers_label.setFixedHeight(120)  # Altura fixa para evitar expansão excessiva
        layout.addWidget(developers_label)
        layout.addSpacing(10)  # Espaço consistente antes do botão

        # Botão OK centralizado
        ok_button = QPushButton("OK")
        ok_button.setFixedWidth(100)
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button, alignment=Qt.AlignCenter)
        
        # Espaço flexível no final
        layout.addStretch(1)  # Mantém o layout balanceado

        # Configura o layout na janela
        self.setLayout(layout)
        self._apply_styles()

    def _apply_styles(self):
        """Aplica estilos à interface"""
        self.setStyleSheet("""
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
        """)