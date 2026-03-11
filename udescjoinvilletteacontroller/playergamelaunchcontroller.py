import os
import subprocess
import sys
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QObject, Qt

from udescjoinvilletteamodel import AppModel
from udescjoinvilletteaservice import PlayerGameLaunchService
# Local module imports
from udescjoinvilletteautil import MessageService

if TYPE_CHECKING:
    from udescjoinvilletteaview import PlayerGameLaunchView


class PlayerGameLaunchController(QObject):

    def __init__(
        self,
        view: "PlayerGameLaunchView",
        message_service: Optional[MessageService] = None,
        service: Optional[PlayerGameLaunchService] = None,
    ):
        self.view = view
        self.msg = message_service or MessageService(view)
        self.service = service or PlayerGameLaunchService()

    def handle_cancel(self) -> None:
        self.view.reject()

    def launch_game(self):
        # Recupera os dados do jogo selecionado no combo da View
        game_data = self.view.cbx_game.currentData()
        language_app = AppModel.get_instance().current_language

        if not game_data:
            self.msg.warning(self.tr("Selecione um jogo antes de iniciar."))
            return

        folder = game_data["folder_path"]
        # Pega o 'exec' (ex: main.py) definido no JSON do jogo
        executable = game_data.get("exec", "main.py")
        script_path = os.path.join(folder, executable)

        if os.path.exists(script_path):
            # Executa o Pygame com o ambiente correto e passa o idioma
            subprocess.Popen(
                [sys.executable, script_path, "--lang", language_app],
                cwd=folder,
            )
            self.view.accept()

    def update_tooltip(self, index):
        if index >= 0:
            novo_hint = self.view.cbx_game.itemData(
                index, Qt.ItemDataRole.ToolTipRole
            )
            self.view.cbx_game.setToolTip(novo_hint)
