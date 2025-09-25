from typing import TYPE_CHECKING, Optional

import qtawesome as qta
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPixmap
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox,
                               QFormLayout, QHBoxLayout, QLabel, QPushButton,
                               QSpinBox, QTabWidget, QVBoxLayout, QWidget)

from udescjoinvilletteagames.kartea.model import PlayerKarteaConfig
from udescjoinvilletteagames.kartea.util import KarteaPathConfig
from udescjoinvilletteawindow import WindowConfig

if TYPE_CHECKING:
    from udescjoinvilletteagames.kartea.controller import \
        PlayerKarteaConfigEditController
    from udescjoinvilletteagames.kartea.model import PlayerKarteaSession
    from udescjoinvilletteamodel import Player


class PlayerKarteaConfigEditView(QDialog, WindowConfig):
    """View for editing PlayerKarteaConfig data."""

    def __init__(
        self,
        parent: Optional[QDialog] = None,
        config: Optional["PlayerKarteaConfig"] = None,
        controller: Optional["PlayerKarteaConfigEditController"] = None,
    ) -> None:
        super().__init__(parent)
        self.setModal(True)
        self.translator = (
            parent.translator if hasattr(parent, "translator") else None
        )
        action = "Editar" if config else "Novo"
        title = parent.parent().get_title()
        self.setup_window(
            f"{title} - {action}",
            parent.windowIcon() if parent else None,
            WindowConfig.DECREMENT_SIZE_PERCENT,
            10,
            5,
            parent,
        )
        self.controller = controller

        self._media_player: Optional[QMediaPlayer] = None
        self._audio_output: Optional[QAudioOutput] = None
        self._is_media_status_connected: bool = False

        self.image_options = self.controller.get_list_images()
        self.sound_options = self.controller.get_list_sounds()

        self.tab_widget = QTabWidget()
        self.game_settings_tab = QWidget()
        self.visual_resources_tab = QWidget()
        self.visual_feedback_tab = QWidget()
        self.sound_feedback_tab = QWidget()
        self.interface_settings_tab = QWidget()

        self.tab_widget.addTab(self.game_settings_tab, "Configurações de Jogo")
        self.tab_widget.addTab(self.visual_resources_tab, "Recursos Visuais")
        self.tab_widget.addTab(self.visual_feedback_tab, "Feedback Visual")
        self.tab_widget.addTab(self.sound_feedback_tab, "Feedback Sonoro")
        self.tab_widget.addTab(
            self.interface_settings_tab, "Configurações de Interface"
        )

        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )

        icon_ok = qta.icon("fa6s.check", color="green")
        self.button_box.button(QDialogButtonBox.Ok).setText("OK")
        self.button_box.button(QDialogButtonBox.Ok).setIcon(icon_ok)
        self.button_box.button(QDialogButtonBox.Ok).setToolTip("Salvar")

        icon_cancel = qta.icon("fa6s.xmark", color="red")
        self.button_box.button(QDialogButtonBox.Cancel).setText("Cancelar")
        self.button_box.button(QDialogButtonBox.Cancel).setIcon(icon_cancel)
        self.button_box.button(QDialogButtonBox.Cancel).setToolTip("Cancelar")

        self.button_box.accepted.connect(self.controller.handle_ok)
        self.button_box.rejected.connect(self.controller.handle_cancel)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

        self.setup_game_settings_tab()
        self.setup_visual_resources_tab()
        self.setup_visual_feedback_tab()
        self.setup_sound_feedback_tab()
        self.setup_interface_settings_tab()

    def setup_game_settings_tab(self) -> None:
        layout = QVBoxLayout()
        form = QFormLayout()

        self.player_input = QComboBox()
        players = self.controller.get_all_players()
        for player in players:
            self.player_input.addItem(player.name, player)
        form.addRow("Player:", self.player_input)

        self.session_label = QLabel()
        form.addRow("Session:", self.session_label)

        self.current_phase_input = QComboBox()
        form.addRow("Current Phase:", self.current_phase_input)

        self.current_level_input = QComboBox()
        form.addRow("Current Level:", self.current_level_input)

        self.level_time_input = QSpinBox()
        self.level_time_input.setMinimum(0)
        form.addRow("Level Time:", self.level_time_input)

        layout.addLayout(form)
        layout.addStretch()
        self.game_settings_tab.setLayout(layout)

    def setup_visual_resources_tab(self) -> None:
        layout = QVBoxLayout()
        form = QFormLayout()

        hbox_car = QHBoxLayout()
        self.car_image_input = QComboBox()
        self.car_image_input.setEditable(True)
        self.car_image_input.addItems(self.image_options)
        self.car_preview = QLabel()
        self.car_preview.setFixedSize(100, 100)
        self.car_image_input.currentTextChanged.connect(
            lambda text: self.update_image_preview(text, self.car_preview)
        )
        hbox_car.addWidget(self.car_image_input)
        hbox_car.addWidget(self.car_preview)
        form.addRow("Car Image:", hbox_car)

        hbox_env = QHBoxLayout()
        self.environment_image_input = QComboBox()
        self.environment_image_input.setEditable(True)
        self.environment_image_input.addItems(self.image_options)
        self.env_preview = QLabel()
        self.env_preview.setFixedSize(100, 100)
        self.environment_image_input.currentTextChanged.connect(
            lambda text: self.update_image_preview(text, self.env_preview)
        )
        hbox_env.addWidget(self.environment_image_input)
        hbox_env.addWidget(self.env_preview)
        form.addRow("Environment Image:", hbox_env)

        hbox_tar = QHBoxLayout()
        self.target_image_input = QComboBox()
        self.target_image_input.setEditable(True)
        self.target_image_input.addItems(self.image_options)
        self.tar_preview = QLabel()
        self.tar_preview.setFixedSize(100, 100)
        self.target_image_input.currentTextChanged.connect(
            lambda text: self.update_image_preview(text, self.tar_preview)
        )
        hbox_tar.addWidget(self.target_image_input)
        hbox_tar.addWidget(self.tar_preview)
        form.addRow("Target Image:", hbox_tar)

        hbox_obs = QHBoxLayout()
        self.obstacle_image_input = QComboBox()
        self.obstacle_image_input.setEditable(True)
        self.obstacle_image_input.addItems(self.image_options)
        self.obs_preview = QLabel()
        self.obs_preview.setFixedSize(100, 100)
        self.obstacle_image_input.currentTextChanged.connect(
            lambda text: self.update_image_preview(text, self.obs_preview)
        )
        hbox_obs.addWidget(self.obstacle_image_input)
        hbox_obs.addWidget(self.obs_preview)
        form.addRow("Obstacle Image:", hbox_obs)

        layout.addLayout(form)
        layout.addStretch()
        self.visual_resources_tab.setLayout(layout)

    def setup_visual_feedback_tab(self) -> None:
        layout = QVBoxLayout()
        form = QFormLayout()

        hbox_pos = QHBoxLayout()
        self.positive_feedback_image_input = QComboBox()
        self.positive_feedback_image_input.setEditable(True)
        self.positive_feedback_image_input.addItems(self.image_options)
        self.pos_preview = QLabel()
        self.pos_preview.setFixedSize(100, 100)
        self.positive_feedback_image_input.currentTextChanged.connect(
            lambda text: self.update_image_preview(text, self.pos_preview)
        )
        hbox_pos.addWidget(self.positive_feedback_image_input)
        hbox_pos.addWidget(self.pos_preview)
        form.addRow("Positive Feedback Image:", hbox_pos)

        hbox_neu = QHBoxLayout()
        self.neutral_feedback_image_input = QComboBox()
        self.neutral_feedback_image_input.setEditable(True)
        self.neutral_feedback_image_input.addItems(self.image_options)
        self.neu_preview = QLabel()
        self.neu_preview.setFixedSize(100, 100)
        self.neutral_feedback_image_input.currentTextChanged.connect(
            lambda text: self.update_image_preview(text, self.neu_preview)
        )
        hbox_neu.addWidget(self.neutral_feedback_image_input)
        hbox_neu.addWidget(self.neu_preview)
        form.addRow("Neutral Feedback Image:", hbox_neu)

        hbox_neg = QHBoxLayout()
        self.negative_feedback_image_input = QComboBox()
        self.negative_feedback_image_input.setEditable(True)
        self.negative_feedback_image_input.addItems(self.image_options)
        self.neg_preview = QLabel()
        self.neg_preview.setFixedSize(100, 100)
        self.negative_feedback_image_input.currentTextChanged.connect(
            lambda text: self.update_image_preview(text, self.neg_preview)
        )
        hbox_neg.addWidget(self.negative_feedback_image_input)
        hbox_neg.addWidget(self.neg_preview)
        form.addRow("Negative Feedback Image:", hbox_neg)

        layout.addLayout(form)
        layout.addStretch()
        self.visual_feedback_tab.setLayout(layout)

    def setup_sound_feedback_tab(self) -> None:
        layout = QVBoxLayout()
        form = QFormLayout()

        hbox_pos = QHBoxLayout()
        self.positive_feedback_sound_input = QComboBox()
        self.positive_feedback_sound_input.setEditable(True)
        self.positive_feedback_sound_input.addItems(self.sound_options)
        self.positive_sound_button = QPushButton("▶️ Play")
        self.positive_sound_button.clicked.connect(
            lambda: self.play_sound(
                self.positive_feedback_sound_input.currentText()
            )
        )
        hbox_pos.addWidget(self.positive_feedback_sound_input)
        hbox_pos.addWidget(self.positive_sound_button)
        form.addRow("Positive Feedback Sound:", hbox_pos)

        hbox_neu = QHBoxLayout()
        self.neutral_feedback_sound_input = QComboBox()
        self.neutral_feedback_sound_input.setEditable(True)
        self.neutral_feedback_sound_input.addItems(self.sound_options)
        self.neutral_sound_button = QPushButton("▶️ Play")
        self.neutral_sound_button.clicked.connect(
            lambda: self.play_sound(
                self.neutral_feedback_sound_input.currentText()
            )
        )
        hbox_neu.addWidget(self.neutral_feedback_sound_input)
        hbox_neu.addWidget(self.neutral_sound_button)
        form.addRow("Neutral Feedback Sound:", hbox_neu)

        hbox_neg = QHBoxLayout()
        self.negative_feedback_sound_input = QComboBox()
        self.negative_feedback_sound_input.setEditable(True)
        self.negative_feedback_sound_input.addItems(self.sound_options)
        self.negative_sound_button = QPushButton("▶️ Play")
        self.negative_sound_button.clicked.connect(
            lambda: self.play_sound(
                self.negative_feedback_sound_input.currentText()
            )
        )
        hbox_neg.addWidget(self.negative_feedback_sound_input)
        hbox_neg.addWidget(self.negative_sound_button)
        form.addRow("Negative Feedback Sound:", hbox_neg)

        layout.addLayout(form)
        layout.addStretch()
        self.sound_feedback_tab.setLayout(layout)

    def setup_interface_settings_tab(self) -> None:
        layout = QVBoxLayout()
        form = QFormLayout()

        self.palette_input = QSpinBox()
        self.palette_input.setMinimum(0)
        form.addRow("Palette:", self.palette_input)

        self.hud_input = QCheckBox()
        form.addRow("HUD:", self.hud_input)

        self.sound_input = QCheckBox()
        form.addRow("Sound:", self.sound_input)

        layout.addLayout(form)
        layout.addStretch()
        self.interface_settings_tab.setLayout(layout)

    def update_image_preview(
        self, filename: str, preview_label: QLabel
    ) -> None:
        """Update the image preview label with the selected image."""
        if filename:
            path = KarteaPathConfig.kartea_image(filename)
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                preview_label.setPixmap(
                    pixmap.scaled(preview_label.size(), Qt.KeepAspectRatio)
                )
            else:
                preview_label.clear()
        else:
            preview_label.clear()

    def play_sound(self, filename: str) -> None:
        """Play the selected sound file."""
        if filename:
            if self._media_player is None:
                self._media_player = QMediaPlayer()
                self._audio_output = QAudioOutput()
                self._media_player.setAudioOutput(self._audio_output)
                if not self._is_media_status_connected:
                    self._media_player.mediaStatusChanged.connect(
                        self.on_media_status_changed
                    )
                    self._is_media_status_connected = True

            if self._media_player.playbackState() == QMediaPlayer.PlayingState:
                self._media_player.stop()

            path = KarteaPathConfig.kartea_sound(filename)
            self._media_player.setSource(QUrl.fromLocalFile(path))

    def on_media_status_changed(self, status) -> None:
        """Handle media status changes and play the sound when ready."""
        if status in (QMediaPlayer.LoadedMedia, QMediaPlayer.BufferedMedia):
            self._media_player.play()

    def update_levels(self):
        """Update the current_level_input based on the selected phase."""
        phase_str = self.current_phase_input.currentText()
        self.current_level_input.clear()
        if phase_str:
            phase_id = int(phase_str)  # phase_str is now a string like '1'
            phase = self.controller.dao.phase_dao.select(
                phase_id
            )  # Fetch phase object
            if phase:
                levels = self.controller.get_levels_for_phase(phase)
                self.current_level_input.addItems(
                    [str(l.id) for l in levels or []]
                )
