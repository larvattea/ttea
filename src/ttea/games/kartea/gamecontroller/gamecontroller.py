"""Match controller of the KarTEA game: rules and frame flow."""

import random
import time
from typing import TYPE_CHECKING

import cv2
import pygame

from ttea.games.kartea.gamecore import OUT_OF_AREA, LaneDetector
from ttea.games.kartea.gamemodel import (
    Background,
    Car,
    Image,
    KillResult,
    Line,
    Obstacle,
    Target,
)
from ttea.games.kartea.gameui import UI
from ttea.games.kartea.gameutil import regain_focus
from ttea.games.kartea.gameview import FeedbackView, HudView
from ttea.games.kartea.model import PlayerKarteaSessionDetail
from ttea.games.kartea.model.levelrules import OBJ_TYPE_OBSTACLE

if TYPE_CHECKING:
    from ttea.games.kartea.gamecontroller.sessionrecorder import (
        SessionRecorder,
    )
    from ttea.games.kartea.gamecore import Camera, PoseTracking
    from ttea.games.kartea.gameutil import GameSettings, GameState
    from ttea.games.kartea.model import LevelRules
    from ttea.games.kartea.service import (
        KarteaPhaseService,
        PlayerKarteaConfigService,
    )

EventType = PlayerKarteaSessionDetail.EventType


class GameController:
    """KarTEA game controller: match rules and frame flow.

    Everything arrives by injection (created once in main): GameSettings
    (configuration), GameState (match state), the configuration service
    (player interface options), the phase service (progression and level
    rules), the SessionRecorder (persistence), the camera and the pose
    tracking.

    Delegated responsibilities:

    - LaneDetector: feet position -> lane;
    - HudView: drawing of the HUD;
    - FeedbackView: hit/miss sound and image;
    - SessionRecorder: session, events and configuration;
    - models (Target, Obstacle, Car): return KillResult.

    Parameters
    ----------
    surface : pygame.Surface
        Game screen.
    settings : GameSettings
        Game configuration.
    state : GameState
        Match state (phase/level, score, counters...).
    config_service : PlayerKarteaConfigService
        Player interface options (sound, HUD, feet marker/click).
    phase_service : KarteaPhaseService
        Phase/level progression and level rules (CSV files).
    recorder : SessionRecorder
        Recording of the session, events and configuration.
    camera : Camera
        Video capture.
    pose_tracking : PoseTracking
        Feet detection (MediaPipe).

    Attributes
    ----------
    FINISH_LINE_LEAD_TIME : float, class attribute
        Minimum time (s) before the end at which the finish line appears
        (12).
    FINISH_COUNTDOWN_DURATION : float, class attribute
        Duration (s) of the timer animation to zero after the finish
        line is crossed (2).
    LANE_CHANGE_POINTS : int, class attribute
        Points per lane change (2).
    LEVEL_COUNTER_BY_EVENT : dict[EventType, str], class attribute
        Removal event -> level counter (LevelStats) it increments.
    MENU_CHOICE_EVENTS : dict[str, EventType], class attribute
        Menu choice made with mouse/keyboard (pause or end of level) ->
        "Controle UFE" detail event.
    FEET_MENU_CHOICE_EVENTS : dict[str, EventType], class attribute
        The same choices made by the player with the feet ->
        "Controle do Jogador" event. "game" depends on the screen:
        "Jogar" in the start menu, "Continuar" in the pause menu.
    INTERFACE_OPTION_EVENTS : dict, class attribute
        Interface option -> (event when enabled, event when disabled).
    surface : pygame.Surface
        Game screen.
    settings : GameSettings
        Game configuration.
    state : GameState
        Match state.
    config_service : PlayerKarteaConfigService
        Configuration service.
    phase_service : KarteaPhaseService
        Phase service.
    recorder : SessionRecorder
        Session recorder.
    cap : Camera
        Video capture.
    pose_tracking : PoseTracking
        Feet detection.
    ui : UI
        Drawing helpers shared by HUD and menus.
    hud : HudView
        HUD drawing.
    feedback : FeedbackView
        Hit/miss sound and image.
    lane_detector : LaneDetector
        Feet x -> lane.
    awaiting_unpause : bool
        True while the game is paused (Space or leaving the game area);
        on the first update after the pause the "Controle UFE: Unpause"
        event is recorded, which allows measuring the pause time.
    pause_requested : bool
        Automatic pause requested in this frame (player left the area).
    level_rules : LevelRules | None
        Rules of the current level (phase CSV).
    background : Background
        Road and sprites of the level.
    car : Car
        Player's car.
    targets : list[Target]
        Active targets and obstacles.
    last_lane : int
        Lane of the last object created (-1 at the level start).
    targets_spawn_timer : float
        Time after which the next object may be created.
    spawned : int
        Objects already created in the level (index in
        LevelRules.obj_types).
    game_start_time : float
        Real time when the level started.
    time_left : int
        Seconds left in the level (shown in the HUD).
    finish : int
        1 after the finish line was placed, 0 before.
    finish_line_segment : Line | None
        Road line holding the finish line.
    crossed_finish_line : bool
        Whether the car crossed the finish line.
    finish_countdown_active : bool
        Whether the timer is animating down to zero.
    finish_countdown_start_time_left : int
        ``time_left`` when the countdown started.
    finish_countdown_start_real_time : float
        Game time (ms) when the countdown started.
    level_complete_pending : bool
        True when the countdown reached zero and the level must end.

    Notes
    -----
    ``PoseTracking`` is created once in main: recreating it at each
    level would reload the MediaPipe model.
    """

    FINISH_LINE_LEAD_TIME = 12.0

    FINISH_COUNTDOWN_DURATION = 2.0

    LANE_CHANGE_POINTS = 2

    LEVEL_COUNTER_BY_EVENT = {
        EventType.COLLIDED_TARGET: "targets_collided",
        EventType.AVOIDED_TARGET: "targets_avoided",
        EventType.COLLIDED_OBSTACLE: "obstacles_collided",
        EventType.AVOIDED_OBSTACLE: "obstacles_avoided",
    }

    MENU_CHOICE_EVENTS = {
        "next": EventType.UFE_CONTROL_ADVANCE_LEVEL,
        "rest": EventType.UFE_CONTROL_RESTART_LEVEL,
        "prev": EventType.UFE_CONTROL_REGRESS_LEVEL,
        "exit": EventType.UFE_CONTROL_EXIT_GAME,
    }

    FEET_MENU_CHOICE_EVENTS = {
        "next": EventType.PLAYER_CONTROL_ADVANCE_LEVEL,
        "rest": EventType.PLAYER_CONTROL_RESTART_LEVEL,
        "prev": EventType.PLAYER_CONTROL_REGRESS_LEVEL,
        "exit": EventType.PLAYER_CONTROL_EXIT_GAME,
        "play": EventType.PLAYER_CONTROL_PLAY,
        "game": EventType.PLAYER_CONTROL_PLAY,
    }

    INTERFACE_OPTION_EVENTS = {
        "sound": (
            EventType.UFE_CONTROL_ENABLE_SOUND,
            EventType.UFE_CONTROL_DISABLE_SOUND,
        ),
        "hud": (
            EventType.UFE_CONTROL_ENABLE_HUD,
            EventType.UFE_CONTROL_DISABLE_HUD,
        ),
        "feet_marker": (
            EventType.UFE_CONTROL_ENABLE_FEET_MARKER,
            EventType.UFE_CONTROL_DISABLE_FEET_MARKER,
        ),
        "feet_click": (
            EventType.UFE_CONTROL_ENABLE_FEET_CLICK,
            EventType.UFE_CONTROL_DISABLE_FEET_CLICK,
        ),
    }

    # Level state: annotations only (no class value); the attributes are
    # set by _start_level() at each level start.
    background: Background
    car: Car
    targets: list[Target]
    last_lane: int
    targets_spawn_timer: float
    spawned: int
    game_start_time: float
    time_left: int
    finish: int
    finish_line_segment: Line | None
    crossed_finish_line: bool
    finish_countdown_active: bool
    finish_countdown_start_time_left: int
    finish_countdown_start_real_time: float
    level_complete_pending: bool

    def __init__(
        self,
        surface: pygame.Surface,
        settings: "GameSettings",
        state: "GameState",
        config_service: "PlayerKarteaConfigService",
        phase_service: "KarteaPhaseService",
        recorder: "SessionRecorder",
        camera: "Camera",
        pose_tracking: "PoseTracking",
    ):
        self.surface = surface
        self.settings = settings
        self.state = state
        self.config_service = config_service
        self.phase_service = phase_service
        self.recorder = recorder
        self.cap = camera
        self.pose_tracking = pose_tracking

        self.ui = UI(settings)
        self.hud = HudView(settings, self.ui)
        self.feedback = FeedbackView(settings, state.sound)
        self.lane_detector = LaneDetector(settings)

        self.awaiting_unpause = False

        self.pause_requested = False

        self.level_rules: LevelRules | None = None
        self._start_level()

    # ======================
    # Level
    # ======================
    def _start_level(self) -> None:
        """Prepare a new level (components, rules and counters).

        Notes
        -----
        Rebuilds the road and the car, reads the level rules from the
        phase CSV, sets the object speed to the level number and the
        spawn interval to the CSV ``interval``, clears the previous
        feedback image and resets the level counters and the finish line
        state.
        """
        self.background = Background(self.settings)
        # PoseTracking is created once in main: recreating it at each
        # level would reload the MediaPipe model.
        self.car = Car(self.settings)

        self.level_rules = self.phase_service.get_level_rules(
            self.state.phase, self.state.level
        )
        self.state.targets_move_speed = self.state.level
        self.state.targets_spawn_time = self.level_rules.interval

        self.targets = []
        self.last_lane = -1
        self.feedback.clear()
        self.targets_spawn_timer = 0
        self.spawned = 0

        self.game_start_time = time.time()
        self.time_left = self.state.level_time
        self.state.time_past = 0
        self.state.level_stats.reset()

        self.finish = 0
        self.finish_line_segment = None
        self.crossed_finish_line = False

        self.finish_countdown_active = False
        self.finish_countdown_start_time_left = 0
        self.finish_countdown_start_real_time = 0
        self.level_complete_pending = False

    def _speed_level(self) -> int:
        """Return the speed range of the current level."""
        return self.level_rules.speed

    def _finish_lead_time(self) -> float:
        """Return how long (s) before the end the finish line appears.

        The line must appear before the time runs out, with margin to
        reach the car: never less than the arrival time of the current
        speed + 2 s, even if OBJECT_ARRIVAL_TIME is increased.
        """
        arrival = self.settings.OBJECT_ARRIVAL_TIME[self._speed_level()]
        return max(self.FINISH_LINE_LEAD_TIME, arrival + 2.0)

    def change_level(self, action: str) -> None:
        """Apply a level change to the GameState.

        Used by the end-of-level result (the game's recommendation) and
        by the professional's choices in the pause menu. The progression
        rule belongs to the service, from the phase CSV files.

        Parameters
        ----------
        action : str
            "next", "prev" or "rest" (see
            KarteaPhaseService.change_level).
        """
        self.state.phase, self.state.level = self.phase_service.change_level(
            self.state.phase, self.state.level, action
        )

    def reset(self):
        """Start a new level (after advance, regress or restart).

        Notes
        -----
        The session totals are not reset: the score and lane changes of
        the ending level are added to the session accumulated values.
        Session and configuration are saved right away, since
        phase/level just changed.
        """
        self.state.session_stats.close_level(self.state.level_stats)
        self._start_level()

        self.save_session()

    # ======================
    # Recording (delegated to SessionRecorder)
    # ======================
    def register_menu_choice(
        self, choice: str, by_feet: bool = False
    ) -> None:
        """Record a decision made in a menu.

        Must be called BEFORE the choice is applied, so that the event
        phase and level are those of the level where the decision was
        made.

        Parameters
        ----------
        choice : str
            "next", "rest", "prev", "exit", "play" or "game".
        by_feet : bool, optional
            True when the player chose with the feet (feet click).

        Notes
        -----
        With mouse or keyboard (``by_feet`` False) the decision is the
        professional's ("Controle UFE"); "Jogar" and "Continuar" are not
        recorded (the Unpause is recorded when the game resumes). With
        the feet (``by_feet`` True) the decision is the player's own
        ("Controle do Jogador"), including "Jogar" and "Continuar".

        Without an open session, exiting records nothing, so that no
        empty session is created; "Jogar" with the feet opens the
        session, which would start at the first game event anyway. The
        session totals are saved before the choice is applied.
        """
        if by_feet:
            event_type = self.FEET_MENU_CHOICE_EVENTS.get(choice)
            if choice == "game" and self.state.menu == "Pause":
                event_type = EventType.PLAYER_CONTROL_CONTINUE
            if event_type is None:
                return
            if choice == "exit" and not self.recorder.has_session:
                return
        else:
            event_type = self.MENU_CHOICE_EVENTS.get(choice)
            if event_type is None or not self.recorder.has_session:
                return
        self.recorder.record(event_type)
        # Save the totals before the choice is applied: includes what
        # was done in the interrupted level (and, on exit, the current
        # level).
        self.save_session()

    def save_session(self) -> None:
        """Save the session and the configuration (current values)."""
        self.recorder.save()

    def _register_kill(self, result: KillResult) -> None:
        """Apply the result of a removed target/obstacle.

        Shows the feedback, adds the points, updates the level counter
        and records the event (which also updates the session totals).
        """
        self.feedback.show(self.surface, result)
        stats = self.state.level_stats
        stats.score += result.points
        counter = self.LEVEL_COUNTER_BY_EVENT.get(result.event_type)
        if counter is not None:
            setattr(stats, counter, getattr(stats, counter) + 1)
        self.recorder.record(result.event_type, result.road)

    # ======================
    # Objects
    # ======================
    def _next_object_is_obstacle(self) -> bool:
        """Return whether the next object is an obstacle (CSV obj_type).

        Without a type defined for this object, it is drawn at random
        (50%).
        """
        obj_type = self.level_rules.object_type(self.spawned)
        if obj_type is None:
            return random.randint(0, 100) < 50
        return obj_type == OBJ_TYPE_OBSTACLE

    def _next_lane(self) -> int:
        """Return the lane of the next object, avoiding the last one.

        Notes
        -----
        The first object gets a random lane. On odd levels, an object
        after a side lane goes to the middle and one after the middle
        goes to a random different lane; on even levels, any lane
        different from the previous one is drawn.
        """
        if self.last_lane == -1:
            r = random.randint(0, 2)
        else:
            r = self.last_lane
            if self.state.level % 2 == 1:
                if r == 0:
                    r = 1
                elif r == 1:
                    while r == self.last_lane:
                        r = random.randint(0, 2)
                else:
                    r = 1
            else:
                while r == self.last_lane:
                    r = random.randint(0, 2)
        self.last_lane = r
        return r

    def spawn_targets(self):
        """Create a target or obstacle according to the level rules.

        Notes
        -----
        Interval, maximum amount and type of each object come from the
        phase CSV (LevelRules). Nothing is created while the spawn timer
        has not expired or the level limit was reached. The object is
        attached to the road line ahead of the camera and a "Criou"
        event is recorded.
        """
        if not self.level_rules.allows_more(self.spawned):
            return

        t = time.time()
        if t <= self.targets_spawn_timer:
            return
        self.targets_spawn_timer = t + self.state.targets_spawn_time

        pos = self.background.get_start_pos()
        r = self._next_lane()
        spawn_obstacle = self._next_object_is_obstacle()
        self.spawned += 1

        speed = self.state.targets_move_speed
        if spawn_obstacle:
            obj = Obstacle(r, self.settings, move_speed=speed)
            self.state.level_stats.obstacles += 1
            event_type = EventType.CREATED_OBSTACLE
        else:
            obj = Target(r, self.settings, move_speed=speed)
            self.state.level_stats.targets += 1
            event_type = EventType.CREATED_TARGET

        self.targets.append(obj)
        self.background.lines[pos].target = obj
        self.recorder.record(event_type, r)

    def spawn_finish(self):
        """Place the finish line on the road.

        Notes
        -----
        The road is a loop: the same line may have been passed on an
        earlier lap, so its ``passed`` mark is reset to detect only the
        crossing of this finish line.
        """
        pos = self.background.get_start_pos()
        self.background.lines[pos].sprite = Image.load(
            self.settings.FINISH_IMAGE
        )
        self.background.lines[pos].sprite_x = -0.5
        self.background.lines[pos].passed = False

        self.finish_line_segment = self.background.lines[pos]
        self.crossed_finish_line = False

    # ======================
    # Camera and feet input
    # ======================
    def load_camera(self) -> bool:
        """Load/update the camera frame.

        Returns
        -------
        bool
            True if a frame was read.
        """
        return self.cap.load_camera()

    def track_feet_for_menu(self) -> tuple[int, int] | None:
        """Read the camera and the pose outside the game (menus).

        Keeps the OpenCV capture window live, with the skeleton, and
        gives the feet position to the feet click.

        Returns
        -------
        tuple[int, int] | None
            Real (x, y) position of the feet on screen, or None without
            a camera image or without a detected player.
        """
        if not self.load_camera():
            return None
        self.cap.frame = self.pose_tracking.scan_feets(self.cap.frame)
        self.cap.show()
        cv2.waitKey(1)
        return self.pose_tracking.get_feet_marker_position()

    def set_feet_position(self):
        """Position the car from the detected feet position."""
        self.cap.frame = self.pose_tracking.scan_feets(self.cap.frame)
        self.cap.show()
        x, y = self.pose_tracking.get_feet_center()
        car_y = self.surface.get_height() - self.settings.CAR_SIZE / 2
        self.car.rect.center = (x, car_y)

    def _update_lane(self, x: float) -> None:
        """Update the player lane and apply the lane change rules.

        Notes
        -----
        A change between valid lanes gives +2 points, +1 movement and a
        "Trocou de Pista" event. Leaving the area records "Saiu da área
        do jogo", requests an automatic pause and resets the lane to 0.
        """
        previous = self.state.lane
        self.state.lane = self.lane_detector.lane_for_x(x)

        if self.state.lane == previous:
            return
        if self.state.lane != OUT_OF_AREA and previous != OUT_OF_AREA:
            self.state.level_stats.score += self.LANE_CHANGE_POINTS
            self.state.level_stats.movement += 1
            self.recorder.record(EventType.CHANGED_LANE, previous)
        elif self.state.lane == OUT_OF_AREA:
            self.recorder.record(EventType.LEFT_GAME_AREA, previous)
            self.pause_requested = True
            self.state.lane = 0

    # ======================
    # Drawing
    # ======================
    def draw(self):
        """Draw the road, the car and the HUD.

        Notes
        -----
        The road stops while a pause is requested. The feet dot is drawn
        when the player's ``feet_marker`` option is on.
        """
        if not self.pause_requested:
            self.background.set_speed_level(self._speed_level())
        else:
            self.background.stop()

        self.background.draw(self.surface, self.state.delta_time)
        self.car.draw(self.surface)
        if self.state.feet_marker:
            self.ui.draw_player_marker(
                self.surface, self.pose_tracking.get_feet_marker_position()
            )
        self.hud.draw(self.surface, self.state, self.time_left)

    def game_time_update(self):
        """Update the time left in the level from the game clock."""
        self.time_left = self.state.level_time - int(
            self.state.time_past / 1000
        )

    # ======================
    # Frame
    # ======================
    def update(self, events=None) -> str | None:
        """Run one frame of the game (main update loop).

        Parameters
        ----------
        events : list, optional
            Pygame events already read by the main loop (main.py). The
            event queue must be read only once per frame; if None, the
            queue is read here (compatibility).

        Returns
        -------
        str | None
            "menu" when the game must go to a menu (pause or end of
            level); None to stay in the game.

        Notes
        -----
        Order of a frame: clock and autosave, camera and feet, automatic
        pause, timer, spawning, finish line and countdown, drawing,
        active play (until the finish line), feedback image, end of
        level and keyboard events. Without a camera frame, the frame
        ends early.
        """
        self._begin_frame()

        if not self.load_camera():
            return None

        self.set_feet_position()

        # Automatic pause (player left the game area)
        if self.pause_requested:
            return self._auto_pause()

        self.game_time_update()
        self._update_spawn()
        self._update_finish_line()
        self._update_finish_countdown()

        # Draw elements and HUD with the updated time
        self.draw()

        # Active play until the finish line is crossed
        if not self.crossed_finish_line:
            self._update_active_play()

        # Feedback image (hit/miss) on top of everything, for the time
        # configured for the player (feedback_image_time)
        self.feedback.draw(self.surface, self.state.delta_time)

        if self.crossed_finish_line and self.level_complete_pending:
            return self._finish_level()

        # Pygame events
        if events is None:
            events = pygame.event.get()

        result = self._handle_events(events)
        if result is not None:
            return result

        cv2.waitKey(1)
        return None

    def _begin_frame(self) -> None:
        """Advance the clock, handle the return from pause and autosave.

        The level clock (ms) advances by the frame delta time; on the
        first update after a pause the Unpause event is recorded.
        """
        # Level clock (ms), by the frame delta time (main)
        self.state.time_past += self.state.delta_time * 1000

        # First update after a pause: the game is running again
        # (Continue, Restart, Advance or Regress in the pause menu).
        if self.awaiting_unpause:
            self.awaiting_unpause = False
            self.recorder.record(EventType.UFE_CONTROL_UNPAUSE)

        # Periodic autosave during the game
        self.recorder.autosave_if_due()

    def _auto_pause(self) -> str:
        """Open the pause menu when the player leaves the game area.

        Returns
        -------
        str
            "menu".
        """
        self.state.menu = "Pause"
        self.pause_requested = False
        self.awaiting_unpause = True
        self.save_session()
        return "menu"

    def _update_spawn(self) -> None:
        """Create targets/obstacles or, at the end, the finish line.

        The finish line always appears with the same lead time
        (_finish_lead_time), regardless of phase/level.
        """
        if (
            self.time_left > self._finish_lead_time()
            and not self.crossed_finish_line
        ):
            self.spawn_targets()
        elif self.finish == 0:
            self.spawn_finish()
            self.finish += 1

    def _update_finish_line(self) -> None:
        """Detect the crossing of the finish line.

        Notes
        -----
        Before the line appears, if the clock runs out it is held at 1 s
        (the level only ends by crossing the line). The line is crossed
        when its y passes the car wheels, when the camera already went
        past it (at high speed or low FPS the road may skip right past
        it) or when it left the screen. Crossing starts the timer
        animation to zero, whatever time was left.
        """
        if self.crossed_finish_line:
            return

        finish_line = self.finish_line_segment
        if self.finish <= 0 or finish_line is None:
            if self.time_left <= 0:
                self.time_left = 1
            return

        if (
            finish_line.screen_y >= self.car.rect.bottom
            or finish_line.passed
            or finish_line.sprite is None
        ):
            self.crossed_finish_line = True
            self.finish_countdown_active = True
            self.finish_countdown_start_time_left = self.time_left
            self.finish_countdown_start_real_time = self.state.time_past

    def _update_finish_countdown(self) -> None:
        """Animate the timer down to zero after the finish line.

        At the end of FINISH_COUNTDOWN_DURATION,
        ``level_complete_pending`` becomes True.
        """
        if not self.finish_countdown_active:
            return

        elapsed = (
            self.state.time_past - self.finish_countdown_start_real_time
        ) / 1000.0
        progress = min(1.0, elapsed / self.FINISH_COUNTDOWN_DURATION)
        self.time_left = round(
            self.finish_countdown_start_time_left * (1 - progress)
        )
        if progress >= 1.0:
            self.time_left = 0
            self.finish_countdown_active = False
            self.level_complete_pending = True

    def _update_active_play(self) -> None:
        """Update lane, car position and collisions of the frame.

        Objects that left the screen without colliding are always
        recorded as avoided.
        """
        x, y = self.pose_tracking.get_feet_center()
        self._update_lane(x)

        # Car position and interaction with targets
        self.car.rect.center = (x, y)
        self.car.left_click = self.pose_tracking.feet_closed
        # Lane collision: record the player lane in this frame
        self.car.record_lane(self.state.lane)
        for result in self.car.kill_targets(self.targets):
            self._register_kill(result)

        limit_y = self.surface.get_height() + 100
        for obj in self.targets[:]:
            if obj.current_pos[1] > limit_y:
                self._register_kill(obj.kill(self.targets, collided=False))

    def _finish_level(self) -> str:
        """End the level: evaluate, apply and save the result.

        Returns
        -------
        str
            "menu" (the feedback screen).

        Notes
        -----
        The maximum score is 12 points per object created. A score of at
        least 3/4 of it advances the level ("Feedback_3"), at least 1/4
        keeps it ("Feedback_2") and less regresses it ("Feedback_1").
        The event is recorded with the phase/level of the level that
        ended, and the result is applied right away, so session and
        configuration reflect the new level even if the professional
        leaves from the feedback screen.
        """
        self.level_complete_pending = False
        self.time_left = 0

        stats = self.state.level_stats
        max_score = stats.targets * 12 + stats.obstacles * 12

        if stats.score >= (3 * max_score) / 4:
            event_type, action = EventType.GAME_CONTROL_ADVANCE_LEVEL, "next"
            self.state.menu = "Feedback_3"
        elif stats.score >= max_score / 4:
            event_type, action = EventType.GAME_CONTROL_MAINTAIN_LEVEL, "rest"
            self.state.menu = "Feedback_2"
        else:
            event_type, action = EventType.GAME_CONTROL_REGRESS_LEVEL, "prev"
            self.state.menu = "Feedback_1"

        # Event with the phase/level of the level that ended...
        self.recorder.record(event_type, self.state.lane)
        # ...and the result is applied right away: session and
        # configuration reflect the new level even if the professional
        # leaves from the feedback screen, without clicking "Jogar".
        self.change_level(action)

        # Final session save
        self.save_session()
        return "menu"

    def _handle_events(self, events) -> str | None:
        """Handle keyboard and window focus events.

        Returns
        -------
        str | None
            "menu" when Space pauses the game; None otherwise.

        Notes
        -----
        - Space always pauses (records Pause; Unpause is recorded when
          the game resumes).
        - S or 1 toggles sound; H or 2 toggles the HUD; T or 3 toggles
          the feet marker; C or 4 toggles the feet click.
        - Losing window focus calls ``regain_focus``.
        - ``pygame.QUIT`` is handled by the main loop (main.py).
        """
        for event in events:
            # pygame.QUIT is handled by the main loop (main.py), which
            # ends the game and calls pygame.quit() safely.

            if event.type == pygame.ACTIVEEVENT:
                if getattr(event, "gain", 1) == 0:
                    regain_focus()

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_SPACE:
                # Space always pauses. Do not set self.pause_requested:
                # returning "menu" already shows the pause menu, and
                # setting it would make the menu reappear right after
                # the player continues.
                self.recorder.record(EventType.UFE_CONTROL_PAUSE)
                self.background.stop()
                self.state.menu = "Pause"
                self.awaiting_unpause = True
                self.save_session()
                return "menu"

            # Sound and HUD shortcuts
            if event.key in (pygame.K_s, pygame.K_1):
                self.toggle_sound()

            if event.key in (pygame.K_h, pygame.K_2):
                self.toggle_hud()

            # Feet marker and feet click shortcuts
            if event.key in (pygame.K_t, pygame.K_3):
                self.toggle_feet_marker()

            if event.key in (pygame.K_c, pygame.K_4):
                self.toggle_feet_click()
        return None

    def _toggle_interface_option(self, option: str) -> bool:
        """Toggle an interface option, save it and record the event.

        Parameters
        ----------
        option : str
            "sound", "hud", "feet_marker" or "feet_click".

        Returns
        -------
        bool
            The new value of the option.
        """
        enabled = not getattr(self.state, option)
        setattr(self.state, option, enabled)
        self.config_service.set_interface_option(
            self.state.player_id, option, enabled
        )
        enable_event, disable_event = self.INTERFACE_OPTION_EVENTS[option]
        self.recorder.record(enable_event if enabled else disable_event)
        return enabled

    def toggle_sound(self) -> None:
        """Toggle the sound and apply it to the feedback sounds."""
        self.feedback.set_sound_enabled(self._toggle_interface_option("sound"))

    def toggle_hud(self) -> None:
        """Toggle the HUD."""
        self._toggle_interface_option("hud")

    def toggle_feet_marker(self) -> None:
        """Toggle the feet marker (dot at the real feet position)."""
        self._toggle_interface_option("feet_marker")

    def toggle_feet_click(self) -> None:
        """Toggle the selection of menu buttons with the feet."""
        self._toggle_interface_option("feet_click")
