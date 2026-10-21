import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

# Import opcional do psutil (não quebra o programa se não estiver instalado)
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False

from PySide6.QtCore import QObject, Qt, QTimer

from ttea.model import AppModel, Calibration, CalibrationPoint, GameMetadata
from ttea.service import CalibrationService, PlayerGameLaunchService

# Local module imports
from ttea.util import MessageService, PathConfig

if TYPE_CHECKING:
    from ttea.view import PlayerGameLaunchView


class PlayerGameLaunchController(QObject):

    def __init__(
        self,
        view: "PlayerGameLaunchView",
        message_service: Optional[MessageService] = None,
        service: Optional[PlayerGameLaunchService] = None,
        calibration_service: Optional[CalibrationService] = None,
    ):
        super().__init__()
        self.view = view
        self.msg = message_service or MessageService(view)
        self.service = service or PlayerGameLaunchService()
        self.calibration_service = calibration_service or CalibrationService()
        self.current_process: Optional[subprocess.Popen] = None
        self.monitor_timer: Optional[QTimer] = None

    def handle_cancel(self) -> None:
        """Trata o clique no botão Cancelar baseado no estado do jogo."""
        if self.is_game_running():
            if self.msg.question(
                self.tr(
                    "Há um jogo em execução e ele será encerrado. Deseja sair da tela de sessão de jogo?"
                ),
                None,
                True,
            ):
                self.view.reject()
            else:
                return
        else:
            self.view.reject()

    def handle_game_info(self) -> None:
        game_data = self.view.cbx_game.currentData()

        if game_data and game_data.developers and game_data.version:
            self.msg.info(
                self.tr(
                    "Este jogo foi desenvolvido por:\n\n{0}\n\n"
                    "Versão: {1}\n"
                    "Desde: {2} - {3}"
                ).format(
                    "\n".join(game_data.developers),
                    game_data.version,
                    game_data.release_year or "N/A",
                    datetime.now().strftime("%Y"),
                )
            )
        else:
            self.msg.warning(
                self.tr(
                    "Informações de autoria do jogo não estão disponíveis.\n"
                    "Verifique se os metadados de configuração estão corretos."
                )
            )

    def _find_by_id_calibration_point(self, calibration_point_id: int) -> bool:
        return self.calibration_service.find_by_id_calibration_point(
            calibration_point_id
        )

    def _find_by_id_calibration(self, calibration_id: int) -> bool:
        return self.calibration_service.find_by_id_calibration(calibration_id)

    def _verify_hardware_configuration(self) -> bool:
        """
        Verifica se os dispositivos físicos atuais coincidem com os dados
        salvos no arquivo de calibração do hardware.
        """
        mismatches = []

        # Validação da Câmera
        cam_info = self.calibration_service.get_camera_info()
        if cam_info:
            saved_cam_id = cam_info.get("camera_id")
            saved_cam_desc = cam_info.get("camera_description")

            current_cameras = self.calibration_service.get_video_inputs()
            camera_found = any(
                cam.id().data().decode(errors="ignore") == saved_cam_id
                or cam.description() == saved_cam_desc
                for cam in current_cameras
            )

            if not camera_found:
                cam_name = (
                    saved_cam_desc or saved_cam_id or self.tr("Desconhecida")
                )
                mismatches.append(
                    self.tr(
                        "- Câmera: O dispositivo '{0}' não foi detectado ou foi desconectado."
                    ).format(cam_name)
                )

        # Validação do Monitor/Tela
        screen_info = self.calibration_service.get_screen_info()
        if screen_info:
            saved_screen_pos = screen_info.get("screen_position", -1)
            saved_screen_model = screen_info.get("screen_model")
            saved_width = screen_info.get("screen_width")
            saved_height = screen_info.get("screen_height")

            current_screens = self.calibration_service.get_screens()
            screen_found = False

            if 0 <= saved_screen_pos < len(current_screens):
                target_screen = current_screens[saved_screen_pos]
                geo = target_screen.geometry()

                # Valida compatibilidade de dimensões e modelo
                if geo.width() == saved_width and geo.height() == saved_height:
                    if (
                        not saved_screen_model
                        or target_screen.model() == saved_screen_model
                    ):
                        screen_found = True

            if not screen_found:
                screen_name = (
                    saved_screen_model or f"Display #{saved_screen_pos}"
                )
                mismatches.append(
                    self.tr(
                        "- Monitor: A tela configurada ('{0}' - {1}x{2}) não corresponde à disposição atual do sistema."
                    ).format(screen_name, saved_width, saved_height)
                )

        # Exibição de Alerta ao Usuário
        if mismatches:
            details = "\n".join(mismatches)
            msg_text = self.tr(
                "Foram detectadas divergências nos equipamentos configurados:\n\n"
                "{0}\n\n"
                "Recomenda-se verificar a instalação física, salvar os dados do hardware\n"
                "atualizados na tela de calibração e/ou realizar a calibração novamente.\n\n"
                "Deseja iniciar o jogo mesmo assim?"
            ).format(details)

            # default_no=True para focar no 'Não' por segurança
            return self.msg.question(msg_text, None, True)

        return True

    @staticmethod
    def build_game_command(
        game_data: GameMetadata,
        language: str,
        player_id: str,
        professional_id: str,
    ) -> Optional[List[str]]:
        """Monta o comando que inicia o jogo.

        Cartuchos .ttea são executados pelo comando externo ``tsdk``,
        procurado no PATH e na pasta de ferramentas do uv
        (``~/.local/bin``), pois apps abertos pelo Finder não herdam o PATH
        do shell. Retorna None se o jogo for um cartucho e o ``tsdk`` não
        estiver instalado.
        """
        executable = game_data.entrypoint
        script_path = str(game_data.entrypoint_path)
        args = [
            "--lang",
            language,
            "--player_id",
            player_id,
            "--professional_id",
            professional_id,
        ]

        ext = os.path.splitext(executable.lower())[1] if executable else ""
        if ext == GameMetadata.CARTRIDGE_EXTENSION:
            tsdk = shutil.which("tsdk") or shutil.which(
                "tsdk", path=str(Path.home() / ".local" / "bin")
            )
            if tsdk is None:
                return None
            return [
                tsdk,
                "play",
                script_path,
                *args,
                "--data-dir",
                str(PathConfig.BASE_DIR),
            ]
        if ext in (".py", ".pyw"):
            return [sys.executable, script_path, *args]
        return [script_path, *args]

    def launch_game(self):
        """Valida e inicia o processo do jogo selecionado."""
        game_data = self.view.cbx_game.currentData()
        player_id = self.view.cbx_player.currentData()
        professional_id = self.view.cbx_professional.currentData()

        language_app = AppModel.get_instance().current_language

        if player_id is None:
            self.msg.warning(self.tr("Selecione um jogador antes de iniciar."))
            return
        else:
            player_id = str(player_id)

        if professional_id is None:
            self.msg.warning(
                self.tr("Selecione um profissional antes de iniciar.")
            )
            return
        else:
            professional_id = str(professional_id)

        if not game_data:
            self.msg.warning(self.tr("Selecione um jogo antes de iniciar."))
            return

        if self.is_game_running():
            self.msg.warning(
                self.tr(
                    "Já existe um jogo em execução.\n"
                    "Feche o jogo atual antes de iniciar outro."
                )
            )
            return

        folder = str(game_data.folder_path)
        script_path = str(game_data.entrypoint_path)

        if not os.path.exists(script_path):
            self.msg.critical(
                self.tr(
                    "Erro: Executável do jogo não encontrado em: {0}.\n"
                    "Verifique se o arquivo existe e se os metadados de configuração estão corretos."
                ).format(script_path)
            )
            return

        cmd = self.build_game_command(
            game_data, language_app, player_id, professional_id
        )
        if cmd is None:
            self.msg.warning(
                self.tr(
                    "O comando 'tsdk', necessário para jogos .ttea, não foi encontrado.\n"
                    "Instale o TSDK e reinicie o T-TEA."
                )
            )
            return

        # Validação da calibração antes de iniciar o jogo
        if not self._find_by_id_calibration_point(CalibrationPoint.ID_VALUE):
            self.msg.warning(
                self.tr(
                    "O arquivo de calibração não foi encontrado.\n"
                    "Por favor, execute a calibração antes de iniciar o jogo."
                )
            )
            return

        # Validação do ambiente de hardware antes de iniciar o jogo
        if not self._find_by_id_calibration(Calibration.ID_VALUE):
            self.msg.warning(
                self.tr(
                    "O arquivo de configuração do hardware não foi encontrado.\n"
                    "Por favor, salve a configuração do hardware antes de iniciar o jogo."
                )
            )
            return

        # Validação do hardware antes de iniciar o jogo
        if not self._verify_hardware_configuration():
            return

        # UX: desabilita botões durante o lançamento
        self.view.pb_play.setEnabled(False)
        self.view.pb_cancel.setEnabled(False)
        self.view.pb_play.setText(self.tr("Aguarde..."))
        self.view.repaint()

        # Cria um novo grupo de processos (melhora o controle da árvore no Windows)
        creationflags = (
            subprocess.CREATE_NEW_PROCESS_GROUP
            if sys.platform.startswith("win")
            else 0
        )

        # Inicia o processo do jogo
        self.current_process = subprocess.Popen(
            cmd, cwd=folder, creationflags=creationflags
        )

        # Monitora quando o jogo realmente abre a janela
        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self._check_if_game_is_visible)
        self.monitor_timer.start(500)

        # Proteção contra falha no lançamento
        QTimer.singleShot(7000, self._restore_buttons_after_timeout)

    def _restore_buttons_after_timeout(self) -> None:
        """Garante que a interface seja liberada após o tempo limite."""
        if self.monitor_timer and self.monitor_timer.isActive():
            self.monitor_timer.stop()
            self._restore_buttons_state()

    def is_game_running(self) -> bool:
        """Retorna True se existe um jogo realmente em execução."""
        return bool(
            self.current_process and self.current_process.poll() is None
        )

    def _check_if_game_is_visible(self) -> None:
        """Verifica se o processo do jogo já abriu uma janela gráfica."""
        if not self.current_process or self.current_process.poll() is not None:
            if self.monitor_timer and self.monitor_timer.isActive():
                self.monitor_timer.stop()
            self._restore_buttons_state()
            return

        if not PSUTIL_AVAILABLE:
            # Sem psutil, liberamos os botões imediatamente para o usuário
            # já que não temos como monitorar o estado das threads.
            self._game_ready()
            return

        try:
            parent = psutil.Process(self.current_process.pid)
            processes = [parent] + parent.children(recursive=True)

            for proc in processes:
                if sys.platform.startswith("win"):
                    if (
                        proc.num_threads() > 1
                        and proc.status() == psutil.STATUS_RUNNING
                    ):
                        self._game_ready()
                        return
                else:
                    if proc.status() in (
                        psutil.STATUS_RUNNING,
                        psutil.STATUS_SLEEPING,
                    ):
                        self._game_ready()
                        return
        except Exception:
            pass

    def _game_ready(self) -> None:
        """Chamado quando o jogo está pronto (janela visível)."""
        if self.monitor_timer and self.monitor_timer.isActive():
            self.monitor_timer.stop()
        self._restore_buttons_state()

    def _restore_buttons_state(self) -> None:
        """Restaura o estado original dos botões da interface."""
        self.view.pb_play.setText(self.tr("Jogar"))
        self.view.pb_play.setEnabled(True)
        self.view.pb_cancel.setEnabled(True)

    def update_tooltip(self, index):
        """Atualiza o tooltip do combobox quando o jogo selecionado muda."""
        if index >= 0:
            novo_hint = self.view.cbx_game.itemData(
                index, Qt.ItemDataRole.ToolTipRole
            )
            self.view.cbx_game.setToolTip(novo_hint)

    def cleanup(self) -> None:
        """Encerra o jogo e todos os seus processos filhos quando a janela é fechada."""
        if not self.is_game_running():
            # Limpeza final mesmo sem processo rodando
            if self.monitor_timer and self.monitor_timer.isActive():
                self.monitor_timer.stop()
            self.current_process = None
            self._restore_buttons_state()
            return

        try:
            if PSUTIL_AVAILABLE:
                parent = psutil.Process(self.current_process.pid)
                children = parent.children(recursive=True)

                # Tenta encerramento gracioso
                for child in children:
                    child.terminate()
                parent.terminate()

                # Aguarda
                _, alive = psutil.wait_procs(children + [parent], timeout=2.0)

                # Força kill no que sobrar
                for survivor in alive:
                    survivor.kill()
            else:
                # Fallback sem psutil
                self.current_process.terminate()
                self.current_process.wait(timeout=2.0)

        except Exception:
            try:
                self.current_process.kill()
            except Exception:
                pass

        finally:
            if self.monitor_timer and self.monitor_timer.isActive():
                self.monitor_timer.stop()
            self.current_process = None
            self._restore_buttons_state()
