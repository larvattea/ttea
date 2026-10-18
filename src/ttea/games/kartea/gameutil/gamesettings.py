"""Immutable configuration of the KarTEA game (pygame side)."""

from types import MappingProxyType
from typing import Any

import numpy as np
import pygame

from ttea.games.kartea.util import (
    KarteaArrivalTimeFields,
    KarteaPalettes,
    KarteaPathConfig,
    KarteaResourceFields,
)


class GameSettings:
    """KarTEA game configuration: screen, sizes, colors and resources.

    A single instance is created by ``main`` and injected where needed
    (GameController, Menu, models, views). There is no global reading:
    no module imports an already configured GameSettings. Once created,
    the instance cannot be changed (``AttributeError``).

    The match state (phase/level, score, counters, lane, menu, clock)
    lives in ``GameState``; data access, in the services.

    The class constants below apply to any resolution; the instance
    attributes depend on the screen and on the player's configuration.
    Since the instance is frozen at the end of ``__init__``, all
    attributes are constants and follow the PEP 8 convention
    (uppercase).

    Parameters
    ----------
    lang : str
        Game language.
    settings : dict[str, Any]
        Effective configuration built by
        ``PlayerKarteaConfigService.build_game_settings``: screen,
        calibration points and the player's configuration already
        completed with the kartea.ini defaults.

    Attributes
    ----------
    WINDOW_NAME, GAME_TITLE : str, class attribute
        Window title ("KarTEA").
    BASE_WIDTH, BASE_HEIGHT : int, class attribute
        Reference resolution of the original design (800x600).
    FPS : int, class attribute
        Target frames per second (60).
    DRAW_FPS : bool, class attribute
        Whether the FPS counter is drawn.
    MAX_DELTA_TIME : float, class attribute
        Safety cap (s) for ``GameState.delta_time``: avoids big jumps in
        the game position after a real pause (window switch, loading,
        debugger breakpoint).
    ROAD_WIDTH, SEGMENT_LENGTH, CAMERA_DEPTH : int, class attribute
        Pseudo-3D road geometry.
    DRAW_HITBOX : bool, class attribute
        Whether the car hitbox is drawn (debugging).
    ANIMATION_SPEED : float, class attribute
        Animation speed.
    COLLISION_LANE_TOLERANCE : float, class attribute
        Tolerance (s) of the player lane before an object passes the
        car. 0 uses only the lane at that instant; > 0 collides if the
        player was in the object's lane for most of the last N seconds,
        absorbing the feet reading jitter near the lane boundary.
    OBJECT_SPAWN_SEGMENTS : int, class attribute
        Segments ahead of the camera where targets, obstacles and the
        finish line appear.
    OBJECT_ARRIVAL_SEGMENTS : int, class attribute
        Distance (segments) from that point to the front of the car,
        used to turn the arrival time into speed (measured: ~191 in
        SVGA, HD and Full HD).
    COLORS : dict, class attribute
        RGB colors of title, score, timer and buttons.
    CALIBRATION_POINT_COLOR, CALIBRATION_LINE_COLOR : tuple, class
    attribute
        BGR (OpenCV) colors of the calibration area drawn over the
        camera image: points in red, sides in green.
    CONTROL_WIDTH, CONTROL_HEIGHT : int, class attribute
        Resolution of the control (camera) image used in the mapping.
    FEEDBACK_IMAGE_TIME_MIN, FEEDBACK_IMAGE_TIME_MAX : float, class
    attribute
        Range (s) of the feedback image display time.
    FEET_CLICK_TIME_MIN, FEET_CLICK_TIME_MAX : float, class attribute
        Range (s) of the time standing on a button to select it.
    FEET_CLICK_TIME_DEFAULT : float, class attribute
        Default selection time (1.2 s).
    FEET_CLICK_BASE_MARGIN : int, class attribute
        Selection hysteresis: once selection starts, the button "grows"
        this many px (800x600 base) on each side.
    FEET_CLICK_EXIT_TOLERANCE : float, class attribute
        Leaving the button for less than this time (s) does not
        interrupt the count.
    FEET_MARKER_BASE_RADIUS : int, class attribute
        Radius of the feet dot (800x600 base).
    FEET_MARKER_COLOR, FEET_MARKER_BORDER_COLOR : tuple, class attribute
        RGB colors of the feet dot and its border.
    BASE_OBJ_POS : list[tuple[int, int]], class attribute
        Reference positions (800x600) where objects appear, per lane.
    CURRENT_LANG : str
        Game language.
    SCREEN_WIDTH, SCREEN_HEIGHT : int
        Screen size (px).
    SCREEN_OS_INDEX, SCREEN_POS_X, SCREEN_POS_Y : int
        Monitor index and window position.
    FULLSCREEN : bool
        Whether the game runs fullscreen.
    CALIBRATION_POINTS : numpy.ndarray
        Read-only 4x2 int array with the calibrated area; zeros when
        there is no calibration.
    LANE_DIV_0, LANE_DIV_1, LANE_DIV_2, LANE_DIV_3 : int
        Screen x of the lane boundaries (thirds of the width).
    UI_SCALE : float
        UI scale factor (smallest of the width/height scales, so nothing
        is distorted).
    WIDTH_RATIO, HEIGHT_RATIO : float
        Camera -> screen mapping; without it the car cannot cross the
        whole screen at resolutions other than 800x600.
    BUTTONS_SIZES : tuple[int, int]
        Menu button size, scaled.
    FONTS : dict[str, pygame.font.Font]
        "small", "medium" and "big" fonts, scaled.
    CAR_SIZE : int
        Car size (1/5 of the screen width).
    CAR_HITBOX_SIZE : tuple[int, int]
        Car hitbox size.
    TARGETS_SIZES, OBSTACLE_SIZES : tuple[int, int]
        Size of targets and obstacles before perspective (100x100).
    OBJ_POS : list[tuple[int, int]]
        BASE_OBJ_POS scaled to the screen.
    VEHICLE_IMAGE, ENVIRONMENT_IMAGE_RIGHT, ENVIRONMENT_IMAGE_LEFT : str
        Resolved paths (":/..." or mods file) of the image resources.
    HORIZON_IMAGE : str
        Resolved path of the horizon (environment background) image.
    TARGET_IMAGE, OBSTACLE_IMAGE : str
        Resolved paths of the target and obstacle images.
    POSITIVE_FEEDBACK_IMAGE, NEUTRAL_FEEDBACK_IMAGE : str
        Resolved paths of the feedback images (also
        NEGATIVE_FEEDBACK_IMAGE).
    POSITIVE_FEEDBACK_SOUND, NEUTRAL_FEEDBACK_SOUND : str
        Resolved paths of the feedback sounds (also
        NEGATIVE_FEEDBACK_SOUND).
    FEEDBACK_IMAGE_TIME : float
        Time (s) the positive/negative feedback image stays on screen,
        clamped to the allowed range.
    FEET_CLICK_TIME : float
        Time (s) on a button to select it with the feet, clamped.
    FEET_CLICK_MARGIN : int
        FEET_CLICK_BASE_MARGIN scaled.
    FEET_MARKER_RADIUS : int
        Radius of the feet dot, scaled (at least 4 px).
    OBJECT_ARRIVAL_TIME : Mapping[int, float]
        Read-only ``{speed: seconds}`` from the player's configuration.
    PALETTE : int
        Number of the track color palette (KarteaPalettes).
    MENU_BACKGROUND, MENU_FEEDBACK_25, MENU_FEEDBACK_50 : str
        Built-in menu images (also MENU_FEEDBACK_75).
    MENU_CLICK_SOUND : str
        Menu's own click sound ("click" alias in the QRC), independent
        of the player's positive feedback sound.
    MISS_SOUND, POINT_SOUND : str
        Miss and hit sounds: the player's negative and positive feedback
        sounds.
    CRASH_SOUND, WIN_SOUND, CLOCK_TICK_SOUND : str
        Sounds of the user's sounds folder.
    FINISH_IMAGE : str
        Built-in finish line image.
    HORIZON_BG_IMAGE : str
        Horizon image: HORIZON_IMAGE or, if it does not resolve, the
        built-in "horizon".

    Notes
    -----
    Speed is defined by the ARRIVAL (reaction) TIME: seconds between an
    object appearing on the road and reaching the front of the car.
    Since the road advances by delta-time (real seconds), the time is
    the same on any machine, FPS and resolution; FPS only affects the
    visual smoothness. The speed range of each level (1, 2 or 3) comes
    from LevelRules.speed; the time of each range comes from the
    player's configuration, clamped and ordered by
    KarteaArrivalTimeFields.order.

    Collision is decided by LANE: when the base of a target/obstacle
    passes the front of the car, it collides if the player is in the
    object's lane (see COLLISION_LANE_TOLERANCE); it does not depend on
    resolution, image sizes, depth or FPS.

    Each resource field of KarteaResourceFields.ALL becomes an uppercase
    attribute. The configuration stores the name chosen on the screen
    (built-in alias, e.g. "defaultvehicle", or mods file, e.g.
    "mycar.png"); here it becomes the path to load. If the name no
    longer exists (e.g. a file deleted from mods), the field default is
    used.
    """

    # ========== Constants ==========
    WINDOW_NAME = "KarTEA"
    GAME_TITLE = WINDOW_NAME

    BASE_WIDTH = 800
    BASE_HEIGHT = 600

    FPS = 60
    DRAW_FPS = False

    # Without the cap, a single very long frame would make the game
    # skip a whole stretch of the track at once.
    MAX_DELTA_TIME = 0.25

    ROAD_WIDTH = 400
    SEGMENT_LENGTH = 200
    CAMERA_DEPTH = 3

    # Drawing and debugging
    DRAW_HITBOX = False

    # Animation
    ANIMATION_SPEED = 0.01

    # ========== Collision (by lane) ==========
    COLLISION_LANE_TOLERANCE = 0.2

    # ========== Speed (arrival time) ==========
    # Arrival segments measured: ~191 in SVGA, HD and Full HD.
    OBJECT_SPAWN_SEGMENTS = 200
    OBJECT_ARRIVAL_SEGMENTS = 191

    # ========== Colors ==========
    COLORS = {
        "title": (38, 61, 39),
        "score": (38, 61, 39),
        "timer": (38, 61, 39),
        "buttons": {
            "default": (56, 67, 209),
            "second": (87, 99, 255),
            "text": (255, 255, 255),
            "shadow": (46, 54, 163),
        },
    }

    CALIBRATION_POINT_COLOR = (0, 0, 255)
    CALIBRATION_LINE_COLOR = (0, 255, 0)

    CONTROL_WIDTH = 640
    CONTROL_HEIGHT = 480

    # 0 = a single frame, as in the original game.
    FEEDBACK_IMAGE_TIME_MIN = 0.0
    FEEDBACK_IMAGE_TIME_MAX = 2.0

    # ========== Feet: marker and button selection ==========
    FEET_CLICK_TIME_MIN = 0.5
    FEET_CLICK_TIME_MAX = 3.0
    FEET_CLICK_TIME_DEFAULT = 1.2
    # Selection hysteresis: the tracking jitters a few pixels from
    # one frame to the next.
    FEET_CLICK_BASE_MARGIN = 30
    FEET_CLICK_EXIT_TOLERANCE = 0.4
    FEET_MARKER_BASE_RADIUS = 15
    FEET_MARKER_COLOR = (255, 255, 0)
    FEET_MARKER_BORDER_COLOR = (0, 0, 0)

    BASE_OBJ_POS = [(368, 80), (393, 80), (419, 80)]

    def __init__(self, lang: str, settings: dict[str, Any]) -> None:
        self.CURRENT_LANG = lang

        # ========== Screen ==========
        self.SCREEN_WIDTH: int = settings["screen_width"]
        self.SCREEN_HEIGHT: int = settings["screen_height"]
        self.SCREEN_OS_INDEX: int = settings["screen_os_index"]
        self.SCREEN_POS_X: int = settings["screen_pos_x"]
        self.SCREEN_POS_Y: int = settings["screen_pos_y"]
        self.FULLSCREEN: bool = settings["fullscreen"]

        # ========== Calibration ==========
        points = np.zeros((4, 2), dtype=int)
        for index, (x, y) in enumerate(
            settings.get("calibration_points") or []
        ):
            points[index][0] = x
            points[index][1] = y
        points.setflags(write=False)
        self.CALIBRATION_POINTS = points

        # ========== Lane boundaries ==========
        self.LANE_DIV_0 = 0
        self.LANE_DIV_1 = self.SCREEN_WIDTH // 3
        self.LANE_DIV_2 = 2 * (self.SCREEN_WIDTH // 3)
        self.LANE_DIV_3 = self.SCREEN_WIDTH

        # ========== Scale factors ==========
        width_scale = self.SCREEN_WIDTH / self.BASE_WIDTH
        height_scale = self.SCREEN_HEIGHT / self.BASE_HEIGHT
        # for the UI, without distortion
        self.UI_SCALE = min(width_scale, height_scale)

        # ========== Camera -> screen mapping ==========
        self.WIDTH_RATIO = self.SCREEN_WIDTH / self.CONTROL_WIDTH
        self.HEIGHT_RATIO = self.SCREEN_HEIGHT / self.CONTROL_HEIGHT

        # ========== UI sizes (menus, buttons, fonts) ==========
        self.BUTTONS_SIZES: tuple[int, int] = (
            int(150 * self.UI_SCALE),
            int(45 * self.UI_SCALE),
        )
        pygame.font.init()
        self.FONTS = {
            "small": pygame.font.Font(None, max(1, int(10 * self.UI_SCALE))),
            "medium": pygame.font.Font(None, max(1, int(25 * self.UI_SCALE))),
            "big": pygame.font.Font(None, max(1, int(50 * self.UI_SCALE))),
        }

        # ========== Game object sizes and positions ==========
        self.CAR_SIZE = int(self.SCREEN_WIDTH / 5)
        self.CAR_HITBOX_SIZE = (
            self.CAR_SIZE + int(50 * self.UI_SCALE),
            self.CAR_SIZE + int(50 * self.UI_SCALE),
        )
        self.TARGETS_SIZES = (100, 100)
        self.OBSTACLE_SIZES = self.TARGETS_SIZES
        self.OBJ_POS: list[tuple[int, int]] = [
            (int(x * width_scale), int(y * height_scale))
            for (x, y) in self.BASE_OBJ_POS
        ]

        # ===== Visual resources, visual and sound feedback =====
        # One uppercase attribute per KarteaResourceFields.ALL field.
        for field in KarteaResourceFields.ALL:
            setattr(
                self,
                field.setting_name,
                KarteaPathConfig.resolve_for_field_or_default(
                    field.name, settings.get(field.name) or ""
                ),
            )

        # Feedback image time (s), clamped to the allowed range
        feedback_time = settings.get(
            "feedback_image_time", self.FEEDBACK_IMAGE_TIME_MIN
        )
        try:
            feedback_time = float(str(feedback_time).replace(",", "."))
        except (TypeError, ValueError):
            feedback_time = self.FEEDBACK_IMAGE_TIME_MIN
        self.FEEDBACK_IMAGE_TIME: float = round(
            max(
                self.FEEDBACK_IMAGE_TIME_MIN,
                min(self.FEEDBACK_IMAGE_TIME_MAX, feedback_time),
            ),
            2,
        )

        # ========== Feet: marker and button selection ==========
        click_time = settings.get(
            "feet_click_time", self.FEET_CLICK_TIME_DEFAULT
        )
        try:
            click_time = float(str(click_time).replace(",", "."))
        except (TypeError, ValueError):
            click_time = self.FEET_CLICK_TIME_DEFAULT
        self.FEET_CLICK_TIME: float = round(
            max(
                self.FEET_CLICK_TIME_MIN,
                min(self.FEET_CLICK_TIME_MAX, click_time),
            ),
            2,
        )
        self.FEET_CLICK_MARGIN = int(
            self.FEET_CLICK_BASE_MARGIN * self.UI_SCALE
        )
        self.FEET_MARKER_RADIUS = max(
            4, int(self.FEET_MARKER_BASE_RADIUS * self.UI_SCALE)
        )

        # ========== Speed (arrival time) ==========
        arrival_times = KarteaArrivalTimeFields.order(settings)
        self.OBJECT_ARRIVAL_TIME = MappingProxyType(
            {
                field.speed: arrival_times[field.name]
                for field in KarteaArrivalTimeFields.ALL
            }
        )

        # ========== Interface ==========
        self.PALETTE = KarteaPalettes.id_of(settings["palette"])

        # ========== Menu resources ==========
        self.MENU_BACKGROUND = KarteaPathConfig.game_builtin_image("menu")
        self.MENU_CLICK_SOUND = KarteaPathConfig.game_builtin_sound("click")
        self.MENU_FEEDBACK_25 = KarteaPathConfig.game_builtin_image("trophy25")
        self.MENU_FEEDBACK_50 = KarteaPathConfig.game_builtin_image("trophy50")
        self.MENU_FEEDBACK_75 = KarteaPathConfig.game_builtin_image("trophy75")

        # ========== Sounds ==========
        self.MISS_SOUND = self.NEGATIVE_FEEDBACK_SOUND
        self.CRASH_SOUND = KarteaPathConfig.game_sound("crash.wav")
        self.POINT_SOUND = self.POSITIVE_FEEDBACK_SOUND
        self.WIN_SOUND = KarteaPathConfig.game_sound("win.wav")
        self.CLOCK_TICK_SOUND = KarteaPathConfig.game_sound("clocktick.wav")

        # ========== Game images ==========
        self.FINISH_IMAGE = KarteaPathConfig.game_builtin_image("finish")
        # Horizon chosen in the player's config; falls back to the
        # built-in "horizon" if the chosen one cannot be resolved.
        self.HORIZON_BG_IMAGE = (
            self.HORIZON_IMAGE
            or KarteaPathConfig.game_builtin_image("horizon")
        )

        self._frozen = True

    def __setattr__(self, name: str, value: Any) -> None:
        """Set an attribute while the instance is being built.

        Raises
        ------
        AttributeError
            After ``__init__`` (the instance is frozen): match state
            belongs in GameState.
        """
        if getattr(self, "_frozen", False):
            raise AttributeError(
                f"GameSettings é imutável: não é possível alterar '{name}'. "
                "Estado da partida fica no GameState."
            )
        super().__setattr__(name, value)
