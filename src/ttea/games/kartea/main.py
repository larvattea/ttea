"""Entry point of the KarTEA exergame (pygame side).

Parses the command line, wires the services, settings and game objects
together and runs the main loop, switching between the menus and the
game. The language, player and professional come from the command
line (``--lang``, ``--player_id`` and ``--professional_id``).
"""

import argparse
import gettext
import os
import sys

import cv2
import pygame

from ttea.games.kartea.gamecontroller import GameController, SessionRecorder
from ttea.games.kartea.gamecore import Camera, PoseTracking
from ttea.games.kartea.gameutil import GameSettings, GameState, regain_focus
from ttea.games.kartea.gameutil.alphablit import alpha_blit
from ttea.games.kartea.gameview import Menu
from ttea.games.kartea.service import (
    KarteaHardwareService,
    KarteaPhaseService,
    PlayerKarteaConfigService,
)
from ttea.games.kartea.util import KarteaPathConfig
from ttea.log import Log
from ttea.util import CriticalHooks


class KarTEA:
    """Main class that manages the KarTEA game.

    The constructor reads the command line arguments, installs the
    translation, creates the services, the settings, the game state, the
    pygame window and the game objects (composition root: everything is
    created once here and injected where needed).

    Attributes
    ----------
    logger : Log
        Application logger (``Log.get_log()``).
    hardware : KarteaHardwareService
        Camera and pose tracking configuration.
    phase_service : KarteaPhaseService
        Phases and levels read from the phase CSV files.
    service : PlayerKarteaConfigService
        Player configuration; also provides the session and session
        detail services, so they share the same sessions DAO.
    player_config : PlayerKarteaConfig
        Configuration of the player given by ``--player_id`` (created
        when missing).
    settings : GameSettings
        Immutable game configuration built from ``player_config``.
    game_state : GameState
        Mutable state of the match.
    screen : pygame.Surface
        Game window.
    clock : pygame.time.Clock
        Frame clock, limited to ``GameSettings.FPS``.
    fps_font : pygame.font.Font
        Font of the FPS counter.
    game : GameController
        Game logic (track, objects, camera, pose tracking, session).
    menu : Menu
        Start, pause and feedback menus.
    state : str
        Current screen: ``"menu"`` or ``"game"``. Starts at ``"menu"``.
    running : bool
        False ends the main loop.
    events : list[pygame.event.Event]
        Events of the current frame, read once per frame by
        ``handle_events`` and passed to the GameController.

    Notes
    -----
    - Command line arguments: ``--lang`` (default ``"pt_BR"``),
      ``--player_id`` and ``--professional_id`` (default 0).
    - With ``GameSettings.FULLSCREEN`` the window is a borderless
      (``pygame.NOFRAME``) window of the screen size, on display
      ``SCREEN_OS_INDEX``, instead of true fullscreen.
    """

    def __init__(self):
        self.logger = Log.get_log()

        parser = argparse.ArgumentParser(description="KarTEA Exergame")

        parser.add_argument(
            "--lang", type=str, default="pt_BR", help="Idioma do app"
        )
        parser.add_argument(
            "--player_id", type=int, default=0, help="ID do Jogador"
        )
        parser.add_argument(
            "--professional_id", type=int, default=0, help="ID do Profissional"
        )

        args = parser.parse_args()

        self.set_game_language(args.lang)

        # Sessions and details come from the configuration service so
        # they share the same sessions DAO (a single ID counter, no
        # stale data).
        self.hardware = KarteaHardwareService()
        self.phase_service = KarteaPhaseService()
        self.service = PlayerKarteaConfigService(
            hardware_service=self.hardware
        )
        self.player_config = self.service.get_or_create_config(args.player_id)

        settings_data = self.service.build_game_settings(self.player_config)
        self.settings = GameSettings(args.lang, settings_data)
        self.game_state = GameState.from_settings(
            settings_data, args.player_id, args.professional_id
        )
        self.game_state.player_name = self.get_player_first_name()

        # The operator works on the other screen and the capture window
        # takes the focus: losing it must not minimize the game.
        os.environ["SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS"] = "0"
        pygame.init()
        pygame.display.set_caption(self.settings.WINDOW_NAME)

        screen_size = (self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT)
        if self.settings.FULLSCREEN:
            # macOS keeps borderless windows under its menu bar; only
            # fullscreen covers the whole projection there.
            flags = (
                pygame.FULLSCREEN
                if sys.platform == "darwin"
                else pygame.NOFRAME
            )
            self.screen = pygame.display.set_mode(
                screen_size, flags, display=self.settings.SCREEN_OS_INDEX
            )
        else:
            self.screen = pygame.display.set_mode(
                screen_size,
                display=self.settings.SCREEN_OS_INDEX,
            )

        regain_focus()

        self.clock = pygame.time.Clock()

        self.fps_font = pygame.font.SysFont("cooperblack", 22)

        pygame.mixer.init()

        recorder = SessionRecorder(
            self.game_state,
            self.service,
            self.service.session_service,
            self.service.session_detail_service,
        )
        camera = Camera(self.hardware.get_camera_config(), self.settings)
        pose_tracking = PoseTracking(
            self.hardware.get_pose_tracking_config(), self.settings
        )
        self.game = GameController(
            self.screen,
            self.settings,
            self.game_state,
            self.service,
            self.phase_service,
            recorder,
            camera,
            pose_tracking,
        )
        self.menu = Menu(self.screen, self.settings, self.game_state)

        self.state = "menu"

        self.running = True

        self.events = []

    def get_player_first_name(self) -> str:
        """Return the first name of the player of this match.

        Returns
        -------
        str
            First word of ``player_config.player.name`` (e.g. "Fulano"
            for "Fulano Silva"), or "" when there is no player or name.
        """
        player = getattr(self.player_config, "player", None)
        name = (getattr(player, "name", "") or "").strip()
        return name.split()[0] if name else ""

    def set_game_language(self, lang_code="pt_BR"):
        """Install the gettext translation of the game.

        Parameters
        ----------
        lang_code : str, optional
            Language code, e.g. ``"pt_BR"`` (default) or ``"en_US"``.

        Notes
        -----
        Installs ``_()`` into builtins with the ``kartea`` catalog from
        ``resources/locales``. A missing catalog falls back to the
        source texts (pt_BR).
        """
        locales_dir = os.path.join(
            KarteaPathConfig.KARTEA_RESOURCES_DIR, "locales"
        )
        translation = gettext.translation(
            "kartea",
            localedir=locales_dir,
            languages=[lang_code],
            fallback=True,
        )
        translation.install()

    def handle_events(self):
        """Handle the global user events.

        Reads the pygame queue once per frame and keeps the events in
        ``self.events`` for the GameController.

        Notes
        -----
        - Closing the window, Esc or Q exit the game; Q also closes the
          OpenCV "Tela de Captura" window.
        - The Space key (pause) is handled by the GameController, which
          records the pause event.
        """
        self.events = pygame.event.get()
        for event in self.events:
            if event.type == pygame.QUIT:
                self.exit_game()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit_game()

                if event.key == pygame.K_q:
                    self.exit_game()
                    cv2.destroyWindow("Tela de Captura")

    def exit_game(self, by_feet: bool = False):
        """Record the exit in the session (if any) and end the loop.

        Parameters
        ----------
        by_feet : bool, optional
            True if the player chose to exit with the feet. Defaults to
            False.

        Notes
        -----
        The exit is recorded only on the first call (while ``running``
        is True).
        """
        if self.running:
            self.game.register_menu_choice("exit", by_feet=by_feet)
        self.running = False

    def update_menu(self):
        """Update the menu and handle the state transitions.

        Notes
        -----
        - The camera and feet tracking keep running in the menus, so the
          capture window shows the player; with feet click enabled
          (``GameState.feet_click``), the feet can trigger the buttons.
        - Choices made with the feet are recorded as "Controle do
          Jogador"; with mouse/keyboard, as "Controle UFE".
        - ``"game"`` (Play or Continue) and ``"play"`` (feedback screen)
          are recorded only when chosen with the feet: with
          mouse/keyboard, the Unpause is recorded when the game resumes,
          and the level result was already applied and saved by the
          GameController.
        - ``"prev"``, ``"rest"`` and ``"next"`` (pause menu) are
          recorded before the level changes, so the event carries the
          source phase/level; the level is then reset.
        """
        feet_pos = self.game.track_feet_for_menu()
        if not self.game_state.feet_click:
            feet_pos = None

        menu_result = self.menu.update(feet_pos)
        by_feet = self.menu.selected_by_feet

        if menu_result == "exit":
            self.exit_game(by_feet=by_feet)
        elif menu_result == "game":
            # Play (start menu) or Continue (pause); with mouse or
            # keyboard the Unpause is recorded when the game resumes.
            if by_feet:
                self.game.register_menu_choice("game", by_feet=True)
            self.state = "game"
            regain_focus()
        elif menu_result in ("prev", "rest", "next"):
            # Pause menu. Record before applying (event with the
            # source phase/level).
            self.game.register_menu_choice(menu_result, by_feet=by_feet)
            self.game.change_level(menu_result)
            self.game.reset()
            self.state = "game"
        elif menu_result == "play":
            # Feedback screen: the level result was already applied and
            # saved by the GameController; just start the level.
            if by_feet:
                self.game.register_menu_choice("play", by_feet=True)
            self.game.reset()
            self.state = "game"

    def update_game(self):
        """Update the game logic and go back to the menu when asked.

        Notes
        -----
        The level clock advances in the GameController, using the delta
        time of the GameState.
        """
        if self.game.update(self.events) == "menu":
            self.state = "menu"

    def update(self):
        """Update the current screen (menu or game)."""
        if self.state == "menu":
            self.update_menu()
        elif self.state == "game":
            self.update_game()

    def draw_fps(self):
        """Draw the FPS counter in the top left corner.

        Notes
        -----
        Drawn only when ``GameSettings.DRAW_FPS`` is True.
        """
        if self.settings.DRAW_FPS:
            fps_label = self.fps_font.render(
                f"FPS: {int(self.clock.get_fps())}", True, (255, 200, 20)
            )
            alpha_blit(self.screen, fps_label, (5, 5))

    def run(self):
        """Run the main game loop.

        Notes
        -----
        - Each frame handles the events, waits for ``GameSettings.FPS``
          and sets ``GameState.delta_time`` to the real elapsed time in
          seconds, capped at ``GameSettings.MAX_DELTA_TIME``.
        - On any exit, including errors, the session is saved one last
          time (so the level in progress also reaches the session) and
          pygame is shut down. A failure while saving is logged and does
          not hide the original error.
        """
        try:
            while self.running:
                self.handle_events()
                self.clock.tick(self.settings.FPS)

                raw_dt = self.clock.get_time() / 1000.0
                self.game_state.delta_time = min(
                    raw_dt, self.settings.MAX_DELTA_TIME
                )

                self.update()
                pygame.display.update()
                self.draw_fps()
        finally:
            # Last session save on any exit, including errors, so the
            # level in progress also reaches the session.
            try:
                self.game.save_session()
            except Exception as e:
                # Do not let a failure here hide the original error
                log = getattr(self.logger, "log_error", None) or getattr(
                    self.logger, "error", print
                )
                log(f"Erro ao gravar a sessão: {e}")
            pygame.quit()


def main() -> None:
    """Start the KarTEA game.

    Notes
    -----
    Installs the critical exception hooks and the log file
    (``KarteaPathConfig.KARTEA_LOG_FILENAME``), then runs the game. A
    critical error is logged with its stack trace and re-raised; the
    process always ends with ``sys.exit`` (exit code 1 on error, 0
    otherwise).
    """
    CriticalHooks.setup_exception_hooks()

    log_file_path = KarteaPathConfig.log(KarteaPathConfig.KARTEA_LOG_FILENAME)
    logger = Log(log_file=log_file_path)
    logger.log_info("KarTEA started successfully.")

    exit_code = 0
    try:
        kartea = KarTEA()
        kartea.run()
    except Exception as e:
        exit_code = 1
        logger.log_error(f"Critical error KarTEA: {e}")
        logger.log_error_with_stack(e)
        raise e
    finally:
        logger.log_info("KarTEA process finished.")
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
