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
        self.current_process: Optional[subprocess.Popen] = None

        self.view.finished.connect(self.cleanup)

    def handle_cancel(self) -> None:
        self.view.reject()

    def launch_game(self):
        # Recupera os dados do jogo selecionado no combo da View
        game_data = self.view.cbx_game.currentData()
        player_id = str(self.view.cbx_player.currentData())
        professional_id = str(self.view.cbx_professional.currentData())

        language_app = AppModel.get_instance().current_language

        if not game_data:
            self.msg.warning(self.tr("Selecione um jogo antes de iniciar."))
            return

        if self.current_process and self.current_process.poll() is None:
            self.msg.warning(
                self.tr(
                    "Já existe um jogo em execução.\n"
                    "Feche o jogo atual antes de iniciar outro."
                )
            )
            return

        folder = game_data["folder_path"]
        # Pega o 'exec' (ex: main.py) definido no JSON do jogo
        executable = game_data.get("exec")
        script_path = os.path.join(folder, executable)

        if os.path.exists(script_path):
            # Detecta o tipo de executável de forma cross-platform
            # Executa o Pygame com o ambiente correto e passa o idioma
            # self.current_process = subprocess.Popen(
            #    [
            #        sys.executable,
            #        script_path,
            #        "--lang",
            #        language_app,
            #        "--player_id",
            #        player_id,
            #        "--professional_id",
            #        professional_id,
            #    ],
            #    cwd=folder,
            # )

            ext = os.path.splitext(executable.lower())[1] if executable else ""
            if ext in (".py", ".pyw"):
                # Jogos em Python -> usa o interpretador Python
                # (funciona em Win/Linux/mac)
                cmd = [
                    sys.executable,
                    script_path,
                    "--lang",
                    language_app,
                    "--player_id",
                    player_id,
                    "--professional_id",
                    professional_id,
                ]
            else:
                # Qualquer outro executável (.exe no Windows,
                # binário sem extensão no Linux/mac, etc.)
                # O sistema operacional vai tratar corretamente
                cmd = [
                    script_path,
                    "--lang",
                    language_app,
                    "--player_id",
                    player_id,
                    "--professional_id",
                    professional_id,
                ]

            self.current_process = subprocess.Popen(cmd, cwd=folder)
        else:
            self.msg.critical(
                self.tr(
                    "Erro: Executável do jogo não encontrado em: {0}.\n"
                    "Verifique se o arquivo existe e se os metadados de configuração estão corretos."
                ).format(script_path)
            )

    def update_tooltip(self, index):
        if index >= 0:
            novo_hint = self.view.cbx_game.itemData(
                index, Qt.ItemDataRole.ToolTipRole
            )
            self.view.cbx_game.setToolTip(novo_hint)

    def cleanup(self) -> None:
        """Encerra o jogo em execução quando a janela do launcher é fechada."""
        if self.current_process and self.current_process.poll() is None:
            try:
                # Tenta encerrar via (SIGTERM)
                self.current_process.terminate()
                # Dá um tempo para o jogo fechar
                self.current_process.wait(timeout=3.0)
            except Exception:
                # Ignora erros (processo já pode ter sido fechado)
                pass
            finally:
                self.current_process = None
