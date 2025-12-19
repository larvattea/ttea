from typing import TYPE_CHECKING

from PySide6.QtWidgets import QApplication

if TYPE_CHECKING:
    from udescjoinvilletteamodel import AppModel
    from udescjoinvilletteautil import MessageService


class MainService:
    """Serviço global da aplicação principal (saída, futuras funcionalidades globais)"""

    def __init__(self, model: "AppModel", message_service: "MessageService"):
        self.model = model
        self.msg = message_service

    def confirm_exit(self) -> bool:
        """Pergunta ao usuário se deseja realmente sair"""
        return self.msg.question(
            text="Deseja sair do sistema?",
            title="Plataforma T-TEA",
            default_no=True,
        )

    def quit_application(self) -> None:
        QApplication.quit()
