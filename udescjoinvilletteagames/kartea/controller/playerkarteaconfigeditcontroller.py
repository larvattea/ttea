from typing import TYPE_CHECKING, Dict, List, Optional, Union

from PySide6.QtWidgets import QMessageBox

from udescjoinvilletteacontroller import PlayerListController
from udescjoinvilletteagames.kartea.dao.config import PlayerKarteaConfigCsvDAO
from udescjoinvilletteagames.kartea.model import PlayerKarteaConfig
from udescjoinvilletteagames.kartea.model.karteaphase import KarteaPhase
from udescjoinvilletteagames.kartea.model.karteaphaselevel import \
    KarteaPhaseLevel
from udescjoinvilletteagames.kartea.util import KarteaPathConfig

if TYPE_CHECKING:
    from udescjoinvilletteagames.kartea.model import PlayerKarteaSession
    from udescjoinvilletteagames.kartea.view import PlayerKarteaConfigEditView
    from udescjoinvilletteamodel import Player


class PlayerKarteaConfigEditController:
    """Controller for managing the PlayerKarteaConfigEditView dialog.

    This class handles the logic for editing or creating player configuration
    data within a dialog, including input validation and data retrieval.

    Attributes
    ----------
    view : PlayerKarteaConfigEditView
        The dialog view for editing player configuration data.
    config : PlayerKarteaConfig, optional
        The configuration object being edited, if provided.
    ok_clicked : bool
        Flag indicating if the OK button was clicked.
    player_list_controller : PlayerListController
        Controller for managing player list data.
    dao : PlayerKarteaConfigCsvDAO
        DAO for accessing configuration data.
    """

    def __init__(
        self,
        view: Optional["PlayerKarteaConfigEditView"] = None,
        config: Optional["PlayerKarteaConfig"] = None,
        player_list_controller: Optional[PlayerListController] = None,
    ) -> None:
        """Initialize the controller with view, optional configuration,
        and player list controller."""
        self.view = view
        self.config = config
        self.ok_clicked = False
        self.player_list_controller = (
            player_list_controller or PlayerListController(None, None)
        )
        self.dao = PlayerKarteaConfigCsvDAO()
        if self.view:
            self.initialize_view()

    def set_view(self, view: "PlayerKarteaConfigEditView") -> None:
        """Set the view and initialize view-dependent fields."""
        self.view = view
        self.initialize_view()

    def initialize_view(self) -> None:
        """Initialize view-dependent fields."""
        if self.config:
            self.view.player_input.setCurrentText(
                self.config.player.name if self.config.player else ""
            )
            self.view.session_label.setText(
                str(self.config.session) if self.config.session else ""
            )
            self.view.current_phase_input.setCurrentText(
                str(self.config.phase.id)
                if self.config.phase
                else ""  # Use phase ID
            )
            self.view.update_levels()
            self.view.current_level_input.setCurrentText(
                str(self.config.level.id)
                if self.config.level
                else ""  # Use level ID
            )
            self.view.level_time_input.setValue(self.config.level_time)
            self.view.car_image_input.setCurrentText(self.config.car_image)
            self.view.environment_image_input.setCurrentText(
                self.config.environment_image
            )
            self.view.target_image_input.setCurrentText(
                self.config.target_image
            )
            self.view.obstacle_image_input.setCurrentText(
                self.config.obstacle_image
            )
            self.view.positive_feedback_image_input.setCurrentText(
                self.config.positive_feedback_image
            )
            self.view.neutral_feedback_image_input.setCurrentText(
                self.config.neutral_feedback_image
            )
            self.view.negative_feedback_image_input.setCurrentText(
                self.config.negative_feedback_image
            )
            self.view.positive_feedback_sound_input.setCurrentText(
                self.config.positive_feedback_sound
            )
            self.view.neutral_feedback_sound_input.setCurrentText(
                self.config.neutral_feedback_sound
            )
            self.view.negative_feedback_sound_input.setCurrentText(
                self.config.negative_feedback_sound
            )
            self.view.palette_input.setValue(self.config.palette)
            self.view.hud_input.setChecked(self.config.hud)
            self.view.sound_input.setChecked(self.config.sound)
        else:
            default_config = self.get_kartea_ini_config()
            self.view.player_input.setCurrentText("")
            self.view.session_label.setText("")

            default_phase_id = int(
                default_config["game_settings"]["phase_default"]
            )
            default_phase = self.dao.phase_dao.select(default_phase_id)
            self.view.current_phase_input.setCurrentText(
                str(default_phase.id) if default_phase else ""  # Use phase ID
            )
            self.view.update_levels()
            default_level_id = int(
                default_config["game_settings"]["level_default"]
            )
            levels = self.get_levels_for_phase(default_phase)
            default_level = next(
                (l for l in levels if l.id == default_level_id), None
            )
            self.view.current_level_input.setCurrentText(
                str(default_level.id) if default_level else ""  # Use level ID
            )
            self.view.level_time_input.setValue(
                int(default_config["game_settings"]["level_time_default"])
            )
            self.view.car_image_input.setCurrentText(
                default_config["visual_resources"]["car_image_default"]
            )
            self.view.environment_image_input.setCurrentText(
                default_config["visual_resources"]["environment_image_default"]
            )
            self.view.target_image_input.setCurrentText(
                default_config["visual_resources"]["target_image_default"]
            )
            self.view.obstacle_image_input.setCurrentText(
                default_config["visual_resources"]["obstacle_image_default"]
            )
            self.view.positive_feedback_image_input.setCurrentText(
                default_config["visual_feedback"][
                    "positive_feedback_image_default"
                ]
            )
            self.view.neutral_feedback_image_input.setCurrentText(
                default_config["visual_feedback"][
                    "neutral_feedback_image_default"
                ]
            )
            self.view.negative_feedback_image_input.setCurrentText(
                default_config["visual_feedback"][
                    "negative_feedback_image_default"
                ]
            )
            self.view.positive_feedback_sound_input.setCurrentText(
                default_config["sound_feedback"][
                    "positive_feedback_sound_default"
                ]
            )
            self.view.neutral_feedback_sound_input.setCurrentText(
                default_config["sound_feedback"][
                    "neutral_feedback_sound_default"
                ]
            )
            self.view.negative_feedback_sound_input.setCurrentText(
                default_config["sound_feedback"][
                    "negative_feedback_sound_default"
                ]
            )
            self.view.palette_input.setValue(
                int(default_config["interface_settings"]["palette_default"])
            )
            self.view.hud_input.setChecked(
                default_config["interface_settings"]["hud_default"].lower()
                == "true"
            )
            self.view.sound_input.setChecked(
                default_config["interface_settings"]["sound_default"].lower()
                == "true"
            )

        # Populate phase combo box with phase IDs
        phases = self.get_all_phases()
        self.view.current_phase_input.clear()
        self.view.current_phase_input.addItems([str(p.id) for p in phases])

        # Connect phase change to update levels
        self.view.current_phase_input.currentIndexChanged.connect(
            self.view.update_levels
        )

        # Set initial phase and level values
        if self.config:
            self.view.current_phase_input.setCurrentText(
                str(self.config.phase.id) if self.config.phase else ""
            )
            self.view.update_levels()
            self.view.current_level_input.setCurrentText(
                str(self.config.level.id) if self.config.level else ""
            )
        else:
            default_config = self.get_kartea_ini_config()
            default_phase = default_config["game_settings"]["phase_default"]
            self.view.current_phase_input.setCurrentText(default_phase)
            self.view.update_levels()
            default_level = default_config["game_settings"]["level_default"]
            self.view.current_level_input.setCurrentText(default_level)

    def handle_ok(self) -> None:
        """Validate input and accept dialog if valid."""
        if self.is_input_valid():
            self.ok_clicked = True
            self.view.accept()

    def handle_cancel(self) -> None:
        """Close dialog without saving."""
        self.view.reject()

    def is_input_valid(self) -> bool:
        """Validate input fields."""
        error_message = ""

        if not self.view.player_input.currentText():
            error_message += "Player is required!\n"
        if self.config and not self.view.session_label.text():
            error_message += "Session is required!\n"
        if not self.view.car_image_input.currentText():
            error_message += "Car image is required!\n"
        if not self.view.environment_image_input.currentText():
            error_message += "Environment image is required!\n"
        if not self.view.target_image_input.currentText():
            error_message += "Target image is required!\n"
        if not self.view.obstacle_image_input.currentText():
            error_message += "Obstacle image is required!\n"

        if error_message:
            QMessageBox.critical(
                self.view,
                "Invalid Fields",
                "Please correct invalid fields:\n" + error_message,
            )
            return False
        return True

    def get_data(
        self,
    ) -> Dict[
        str,
        Union[
            str,
            int,
            bool,
            "Player",
            "PlayerKarteaSession",
            "KarteaPhase",
            "KarteaPhaseLevel",
        ],
    ]:
        """Return configuration data from input fields."""
        player_name = self.view.player_input.currentText()
        player = next(
            (p for p in self.get_all_players() if p.name == player_name), None
        )

        session_text = self.view.session_label.text()
        session = (
            self.dao.session_dao.select(int(session_text))
            if session_text and session_text.isdigit()
            else None
        )

        phase_text = self.view.current_phase_input.currentText()
        phase = (
            self.dao.phase_dao.select(int(phase_text))
            if phase_text and phase_text.isdigit()
            else None
        )

        level_text = self.view.current_level_input.currentText()
        level = (
            self.dao.level_dao.select(int(level_text))
            if level_text and level_text.isdigit()
            else None
        )

        return {
            "player": player,
            "session": session,
            "phase": phase,
            "level": level,
            "level_time": self.view.level_time_input.value(),
            "car_image": self.view.car_image_input.currentText(),
            "environment_image": self.view.environment_image_input.currentText(),
            "target_image": self.view.target_image_input.currentText(),
            "obstacle_image": self.view.obstacle_image_input.currentText(),
            "positive_feedback_image": self.view.positive_feedback_image_input.currentText(),
            "neutral_feedback_image": self.view.neutral_feedback_image_input.currentText(),
            "negative_feedback_image": self.view.negative_feedback_image_input.currentText(),
            "positive_feedback_sound": self.view.positive_feedback_sound_input.currentText(),
            "neutral_feedback_sound": self.view.neutral_feedback_sound_input.currentText(),
            "negative_feedback_sound": self.view.negative_feedback_sound_input.currentText(),
            "palette": self.view.palette_input.value(),
            "hud": self.view.hud_input.isChecked(),
            "sound": self.view.sound_input.isChecked(),
        }

    def get_all_players(self) -> List["Player"]:
        """Retrieve all players sorted alphabetically by name."""
        return sorted(
            self.player_list_controller.dao.list(), key=lambda p: p.name
        )

    def get_all_phases(self) -> List["KarteaPhase"]:
        """Retrieve all available phases from DAO."""
        return self.dao.get_all_phases()

    def get_levels_for_phase(
        self, phase: "KarteaPhase"
    ) -> List["KarteaPhaseLevel"]:
        """Retrieve levels for a specific phase from DAO."""
        return self.dao.get_levels_for_phase(phase)

    def get_list_images(self) -> List[str]:
        return KarteaPathConfig.list_images()

    def get_list_sounds(self) -> List[str]:
        return KarteaPathConfig.list_sounds()

    def get_kartea_ini_config(self) -> Dict[str, str]:
        return KarteaPathConfig.read_config()
