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

    def handle_cancel(self) -> None:
        if self.current_process and self.current_process.poll() is None:
            if self.msg.question(
                self.tr(
                    "Existe um jogo em execução, ele será finalizado. Deseja sair da tela de sessão de jogo?"
                ),
                None,
                True,
            ):
                self.view.reject()
            else:
                return
        else:
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
        # Pega o 'exec' (ex: main.py, jogo.exe) definido no JSON do jogo
        executable = game_data.get("exec")
        script_path = os.path.join(folder, executable)

        if os.path.exists(script_path):
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

            # 1. Muda o estado do botão ANTES de lançar
            # self.view.pb_play.setEnabled(False)
            # self.view.pb_cancel.setEnabled(False)
            # self.view.pb_play.setText(self.tr("Carregando jogo..."))

            # Força o Qt a repintar a interface imediatamente
            # self.view.repaint()

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
        """Encerra o jogo e todos os seus processos filhos quando a janela é fechada."""
        if self.current_process and self.current_process.poll() is None:
            try:
                import psutil

                # Captura o processo pai criado pelo subprocess
                parent = psutil.Process(self.current_process.pid)

                # Captura recursivamente todos os processos filhos gerados pelo .exe
                children = parent.children(recursive=True)

                # 1. Tenta encerrar de forma amigável (SIGTERM) todos os filhos e o pai
                for child in children:
                    child.terminate()
                parent.terminate()

                # Aguarda um curto período para o encerramento amigável
                _, alive = psutil.wait_procs(children + [parent], timeout=3.0)

                # 2. Se algum processo ainda insistir em ficar vivo, força o encerramento (Kill)
                for survivor in alive:
                    survivor.kill()

            except ImportError:
                # Caso o psutil não esteja instalado por algum motivo,
                # mantém o seu fallback nativo original
                try:
                    self.current_process.terminate()
                    self.current_process.wait(timeout=3.0)
                except subprocess.TimeoutExpired:
                    try:
                        self.current_process.kill()
                        self.current_process.wait(timeout=2.0)
                    except Exception:
                        pass
                except Exception:
                    pass
            except psutil.NoSuchProcess:
                # O processo já havia fechado sozinho
                pass
            except Exception:
                pass
            finally:
                self.current_process = None

                # Restaura os botões originais
                # self.view.pb_play.setText(self.tr("Jogar"))
                # self.view.pb_play.setEnabled(True)
                # self.view.pb_cancel.setEnabled(True)
