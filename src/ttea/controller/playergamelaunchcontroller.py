import subprocess
import sys
from datetime import datetime
from typing import TYPE_CHECKING, Optional

# Import opcional do psutil (não quebra o programa se não estiver instalado)
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False

from PySide6.QtCore import QObject, Qt, QTimer
from packaging.version import Version

from ttea.model import AppModel, Calibration, CalibrationPoint
from ttea.service import CalibrationService, PlayerGameLaunchService
# Local module imports
from ttea.util import MessageService

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

    def handle_game_info(self) -> None:
        game_data = self.view.cbx_game.currentData()
        if not game_data:
            return

        if (
            game_data.get("authors") is not None
            and game_data.get("version") is not None
            and game_data.get("since") is not None
        ):
            self.msg.info(
                self.tr(
                    "Este jogo foi desenvolvido por:\n\n{0}\n\n"
                    "Versão: {1}\n"
                    "Desde: {2} - {3}"
                ).format(
                    "\n".join(game_data.get("authors", [])),
                    game_data.get("version", "N/A"),
                    game_data.get("since", "N/A"),
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
                "Recomenda-se verificar a instalação física, gravar os dados do hardware\n"
                "atualizados na tela de calibração e ou realizar a calibração novamente.\n\n"
                "Deseja iniciar o jogo mesmo assim?"
            ).format(details)

            # default_no=True para focar no 'Não' por segurança
            return self.msg.question(msg_text, None, True)

        return True

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
                self.tr("Selecione um professional antes de iniciar.")
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

        if not game_data.get("installed"):
            self.msg.warning(self.tr("Instale um cartucho compatível antes de iniciar."))
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
        self.view.pb_play.setText(self.tr("Espere"))
        self.view.repaint()

        try:
            config = self.runtime_configuration()
            config.update({
                "language": language_app,
                "player_id": player_id,
                "professional_id": professional_id,
            })
            self.current_process = self.service.launch_game(game_data, config)
        except (OSError, ValueError) as error:
            self._restore_buttons_state()
            self.msg.critical(str(error))
            return

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
        self.update_library_actions()
        self.view.pb_cancel.setEnabled(True)


    def runtime_configuration(self):
        hardware = self.calibration_service.find_by_id_calibration(Calibration.ID_VALUE)
        points = self.calibration_service.find_by_id_calibration_point(CalibrationPoint.ID_VALUE)
        if hardware is None or points is None:
            raise ValueError(self.tr("Calibração ausente; calibre novamente."))
        calibration = points.runtime_calibration()
        return {
            "hardware": {"camera_index": hardware.camera_position,
                         "width": points.capture_width, "height": points.capture_height},
            "calibration": calibration,
            "width": hardware.content_width,
            "height": hardware.content_height,
        }

    def install_game(self):
        game = self.view.cbx_game.currentData()
        if not game or self.is_game_running():
            return
        if game.get("installed") and not self.msg.question(
            self.tr("Atualizar este jogo para a versão compatível selecionada?"), None, True
        ):
            return
        try:
            self.service.install_game(game)
        except (OSError, ValueError) as error:
            self.msg.critical(str(error))
        self.view.populate_games()

    def uninstall_game(self):
        game = self.view.cbx_game.currentData()
        if not game or self.is_game_running():
            return
        if self.msg.question(self.tr("Desinstalar o jogo? Resultados e saves serão preservados."), None, True):
            try:
                self.service.uninstall_game(game)
            except (OSError, ValueError) as error:
                self.msg.critical(str(error))
            self.view.populate_games()

    def update_library_actions(self):
        game = self.view.cbx_game.currentData() or {}
        installed = bool(game.get("installed"))
        release = game.get("release")
        newer = release is not None and (
            not installed or Version(release["version"]) > Version(game["version"])
        )
        self.view.pb_play.setEnabled(installed)
        self.view.pb_install.setEnabled(newer)
        self.view.pb_install.setText(self.tr("Atualizar") if installed else self.tr("Instalar"))
        self.view.pb_uninstall.setEnabled(installed)
        self.view.lbl_library_status.setText(
            self.tr("Instalado: {0}").format(game["version"]) if installed else
            self.tr("Disponível para instalar") if release else
            self.tr("Nenhum cartucho compatível publicado")
        )
    def update_tooltip(self, index):
        """Atualiza o tooltip do combobox quando o jogo selecionado muda."""
        if index >= 0:
            novo_hint = self.view.cbx_game.itemData(
                index, Qt.ItemDataRole.ToolTipRole
            )
            self.view.cbx_game.setToolTip(novo_hint)
        self.update_library_actions()

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
