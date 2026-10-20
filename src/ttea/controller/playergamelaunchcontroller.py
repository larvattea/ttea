"""Controller of the game launch window: checks and game process.

Attributes
----------
PSUTIL_AVAILABLE : bool
    Whether ``psutil`` could be imported; without it, the game process
    tree is not monitored or terminated as a whole.
"""

import os
import subprocess
import sys
from datetime import datetime
from typing import TYPE_CHECKING, Optional

# psutil is optional; the app still runs without it
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False

from PySide6.QtCore import QObject, Qt, QTimer

from ttea.model import AppModel, Calibration, CalibrationPoint
from ttea.service import CalibrationService, PlayerGameLaunchService

from ttea.util import MessageService

if TYPE_CHECKING:
    from ttea.view import PlayerGameLaunchView


class PlayerGameLaunchController(QObject):
    """Controller of the game launch window.

    Validates the selection and the calibration, starts the chosen game
    as a separate process and stops it when the window closes.

    Parameters
    ----------
    view : PlayerGameLaunchView
        The game launch dialog.
    message_service : MessageService | None, optional
        Service used to show messages. Default is None, which creates
        ``MessageService(view)``.
    service : PlayerGameLaunchService | None, optional
        Launch service. Default is None, which creates a new one.
    calibration_service : CalibrationService | None, optional
        Calibration service. Default is None, which creates a new one.

    Attributes
    ----------
    view : PlayerGameLaunchView
        The game launch dialog.
    msg : MessageService
        Service used to show messages.
    service : PlayerGameLaunchService
        Launch service.
    calibration_service : CalibrationService
        Calibration service.
    current_process : subprocess.Popen | None
        Process of the running game, if any.
    monitor_timer : QTimer | None
        Timer that checks whether the game has started.

    Notes
    -----
    All messages are translated with ``self.tr()``.
    """

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
        """Close the window, asking first if a game is running.

        Notes
        -----
        "No" is the default answer. The game itself is stopped by
        ``cleanup`` when the window closes.
        """
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
        """Show the developers, version and years of the selected game.

        A warning is shown when the metadata has no developers or
        version.
        """
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
        """Return the saved calibration points, if any."""
        return self.calibration_service.find_by_id_calibration_point(
            calibration_point_id
        )

    def _find_by_id_calibration(self, calibration_id: int) -> bool:
        """Return the saved hardware calibration, if any."""
        return self.calibration_service.find_by_id_calibration(calibration_id)

    def _verify_hardware_configuration(self) -> bool:
        """Check that the saved camera and screen are still connected.

        Returns
        -------
        bool
            True if everything matches or the user chooses to start the
            game anyway; False otherwise.

        Notes
        -----
        The camera matches when a current camera has the saved ID or
        description. The screen matches when the screen at the saved
        index has the saved width and height and, if a model was saved,
        the same model. Mismatches are listed in a question whose
        default answer is "No".
        """
        mismatches = []

        # Camera
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

        # Screen
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

        if mismatches:
            details = "\n".join(mismatches)
            msg_text = self.tr(
                "Foram detectadas divergências nos equipamentos configurados:\n\n"
                "{0}\n\n"
                "Recomenda-se verificar a instalação física, salvar os dados do hardware\n"
                "atualizados na tela de calibração e/ou realizar a calibração novamente.\n\n"
                "Deseja iniciar o jogo mesmo assim?"
            ).format(details)

            # "No" is the default answer, to be safe
            return self.msg.question(msg_text, None, True)

        return True

    def launch_game(self):
        """Validate the selection and start the selected game.

        Notes
        -----
        A player, a professional and a game must be selected, no game
        may be running, the game entry point must exist and both the
        calibration points and the hardware calibration must be saved;
        then ``_verify_hardware_configuration`` is checked.

        The game runs in its folder with the arguments ``--lang``,
        ``--player_id`` and ``--professional_id``; ``.py`` and ``.pyw``
        entry points run with the current Python interpreter. On Windows
        it starts in a new process group. The buttons stay disabled
        until the game is up (checked every 500 ms) or for at most 7 s.
        """
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
        executable = game_data.entrypoint
        script_path = str(game_data.entrypoint_path)

        if not os.path.exists(script_path):
            self.msg.critical(
                self.tr(
                    "Erro: Executável do jogo não encontrado em: {0}.\n"
                    "Verifique se o arquivo existe e se os metadados de configuração estão corretos."
                ).format(script_path)
            )
            return

        if not self._find_by_id_calibration_point(CalibrationPoint.ID_VALUE):
            self.msg.warning(
                self.tr(
                    "O arquivo de calibração não foi encontrado.\n"
                    "Por favor, execute a calibração antes de iniciar o jogo."
                )
            )
            return

        if not self._find_by_id_calibration(Calibration.ID_VALUE):
            self.msg.warning(
                self.tr(
                    "O arquivo de configuração do hardware não foi encontrado.\n"
                    "Por favor, salve a configuração do hardware antes de iniciar o jogo."
                )
            )
            return

        if not self._verify_hardware_configuration():
            return

        ext = os.path.splitext(executable.lower())[1] if executable else ""
        if ext in (".py", ".pyw"):
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
            cmd = [
                script_path,
                "--lang",
                language_app,
                "--player_id",
                player_id,
                "--professional_id",
                professional_id,
            ]

        # UX: disable the buttons while the game starts
        self.view.pb_play.setEnabled(False)
        self.view.pb_cancel.setEnabled(False)
        self.view.pb_play.setText(self.tr("Aguarde..."))
        self.view.repaint()

        # A new process group gives better control of the process
        # tree on Windows
        creationflags = (
            subprocess.CREATE_NEW_PROCESS_GROUP
            if sys.platform.startswith("win")
            else 0
        )

        self.current_process = subprocess.Popen(
            cmd, cwd=folder, creationflags=creationflags
        )

        # Poll until the game window is really open
        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self._check_if_game_is_visible)
        self.monitor_timer.start(500)

        # Fallback in case the launch fails
        QTimer.singleShot(7000, self._restore_buttons_after_timeout)

    def _restore_buttons_after_timeout(self) -> None:
        """Re-enable the buttons if the game is still starting."""
        if self.monitor_timer and self.monitor_timer.isActive():
            self.monitor_timer.stop()
            self._restore_buttons_state()

    def is_game_running(self) -> bool:
        """Check whether the game process is still running.

        Returns
        -------
        bool
            True if a game process exists and has not exited.
        """
        return bool(
            self.current_process and self.current_process.poll() is None
        )

    def _check_if_game_is_visible(self) -> None:
        """Check whether the game is up and re-enable the buttons.

        Notes
        -----
        Called by ``monitor_timer``. If the process has exited, the
        buttons are restored. Without ``psutil`` the game is considered
        ready at once. Otherwise, on Windows a process of the tree must
        be running with more than one thread; on other systems it must
        be running or sleeping. Errors are ignored.
        """
        if not self.current_process or self.current_process.poll() is not None:
            if self.monitor_timer and self.monitor_timer.isActive():
                self.monitor_timer.stop()
            self._restore_buttons_state()
            return

        if not PSUTIL_AVAILABLE:
            # Without psutil the threads cannot be checked, so the
            # buttons are released at once.
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
        """Stop the monitor timer and re-enable the buttons."""
        if self.monitor_timer and self.monitor_timer.isActive():
            self.monitor_timer.stop()
        self._restore_buttons_state()

    def _restore_buttons_state(self) -> None:
        """Restore the text and state of the Play and Cancel buttons."""
        self.view.pb_play.setText(self.tr("Jogar"))
        self.view.pb_play.setEnabled(True)
        self.view.pb_cancel.setEnabled(True)

    def update_tooltip(self, index):
        """Show the tooltip of the selected game on the game combo box.

        Parameters
        ----------
        index : int
            Index of the selected game; negative values are ignored.
        """
        if index >= 0:
            novo_hint = self.view.cbx_game.itemData(
                index, Qt.ItemDataRole.ToolTipRole
            )
            self.view.cbx_game.setToolTip(novo_hint)

    def cleanup(self) -> None:
        """Stop the game and all its child processes.

        Notes
        -----
        Called when the window closes. With ``psutil``, the children and
        the game are terminated, and those still alive after 2 s are
        killed; without it, only the game process is terminated (and
        killed on error). The monitor timer is stopped and the buttons
        are restored in every case.
        """
        if not self.is_game_running():
            # Clean up even when no game is running
            if self.monitor_timer and self.monitor_timer.isActive():
                self.monitor_timer.stop()
            self.current_process = None
            self._restore_buttons_state()
            return

        try:
            if PSUTIL_AVAILABLE:
                parent = psutil.Process(self.current_process.pid)
                children = parent.children(recursive=True)

                # Try a graceful shutdown first
                for child in children:
                    child.terminate()
                parent.terminate()

                _, alive = psutil.wait_procs(children + [parent], timeout=2.0)

                # Kill whatever is still alive
                for survivor in alive:
                    survivor.kill()
            else:
                # Fallback without psutil
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
