"""View (Qt dialog) to create or edit a player Kartea configuration."""

from collections.abc import Iterable
from functools import partial
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QCoreApplication, QEvent, Qt, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import QComboBox, QDialog

from ttea.games.kartea.ui import Ui_PlayerKarteaConfigEditView
from ttea.games.kartea.util import (
    KarteaArrivalTimeFields,
    KarteaPalettes,
    KarteaPathConfig,
    KarteaResourceFields,
)
from ttea.window import WindowConfig

if TYPE_CHECKING:
    from ttea.games.kartea.controller import PlayerKarteaConfigEditController


class PlayerKarteaConfigEditView(
    QDialog, Ui_PlayerKarteaConfigEditView, WindowConfig
):
    """Modal dialog to create or edit a player Kartea config.

    Loads the UI from the .ui file, applies consistent styling (icons,
    size, title), and delegates all validation and data handling to
    PlayerKarteaConfigEditController. The view does not create its
    controller: KarteaViewFactory creates both and calls
    ``bind(controller)`` to connect the signals. The controller only
    uses the methods below; it never touches widgets.

    Parameters
    ----------
    parent : QWidget | None, optional
        Parent widget.
    editing : bool, optional
        True when editing an existing config (title "Editar"); False
        when creating a new one ("Novo"). Defaults to False.

    Attributes
    ----------
    RESOURCE_COMBOS : dict[str, str], class attribute
        Form field -> name of its resource (image/sound) combo box,
        built from KarteaResourceFields.ALL.
    PREVIEW_COMBOS : dict[str, tuple[str, str, bool]], class attribute
        Image combo -> (field, type shown in the preview, is feedback?).
        Feedback images use the feedback tab preview; the others, the
        Visual Resource tab preview.
    SOUND_COMBOS : tuple[tuple[str, str, str], ...], class attribute
        (field, sound combo, button that plays the sound).
    OPEN_MODS_BUTTONS : dict[str, str], class attribute
        "Open resources folder" button of each tab -> mods subfolder it
        opens.
    controller : PlayerKarteaConfigEditController | None
        Handles field initialization, validation, and data extraction;
        None until ``bind`` is called.
    sound_effects : dict[str, QSoundEffect]
        Preloaded sound of each sound combo, created by ``bind``.

    Methods
    -------
    bind(controller)
        Connect the widgets' signals to the controller.
    set_player_choices(players) / set_resource_choices(resources)
        Fill the player and resource combo boxes.
    set_phase_choices(phase_ids) / set_level_choices(level_ids)
        Fill the phase and level combo boxes.
    set_form_data(data) / get_form_data()
        Write/read all form fields as a dict (same keys as the service).
    set_player_editable(editable)
        Enable/disable the player combo box.
    open_mods_folder(subdir="")
        Open the KarTEA mods folder in the file manager.
    update_resource_preview(...) / update_feedback_preview(...)
        Show an image preview in the visual resource or feedback tab.

    Notes
    -----
    The widgets (``cbx_*``, ``spn_*``, ``chk_*``, ``pb_*``, ``lbl_*``)
    come from the generated Ui_PlayerKarteaConfigEditView (``setupUi``).

    The arrival time spin boxes keep their ranges consistent: each speed
    must be faster than the previous one (see KarteaArrivalTimeFields).
    The feet click time is enabled only while feet click is checked.

    Localized texts (title, preview labels, messages) are translated
    with ``self.tr()``. The palette names/descriptions and the preview
    labels are ``QT_TRANSLATE_NOOP`` source texts of KarteaPalettes and
    KarteaResourceFields in this class context
    ("PlayerKarteaConfigEditView") (i18n).
    """

    RESOURCE_COMBOS = {
        field.name: field.combo_name for field in KarteaResourceFields.ALL
    }

    PREVIEW_COMBOS = {
        field.combo_name: (field.name, field.preview_label, field.feedback)
        for field in KarteaResourceFields.images()
    }

    SOUND_COMBOS = tuple(
        (field.name, field.combo_name, field.play_button)
        for field in KarteaResourceFields.sounds()
    )

    # Each button opens the mods subfolder that holds the folders of
    # its tab's fields.
    OPEN_MODS_BUTTONS = {
        "pb_open_mods_visual": "images",
        "pb_open_mods_feedback": "images/feedback",
        "pb_open_mods_sound": "sounds/feedback",
    }

    def __init__(self, parent=None, editing: bool = False):
        super().__init__(parent)
        self.setupUi(self)
        self.controller: PlayerKarteaConfigEditController | None = None

        # Arrival times: each speed must be faster than the previous
        # one, so each spin box range follows its neighbors.
        for field in KarteaArrivalTimeFields.ALL:
            getattr(self, field.widget_name).valueChanged.connect(
                self._update_arrival_time_ranges
            )
        self._reset_arrival_time_ranges()
        self._update_arrival_time_ranges()

        # Color palettes are fixed (KarteaPalettes.ALL): they do not
        # depend on the controller
        self._fill_palette_choices()

        # Feet click time: enabled only while feet click is on
        self.chk_feet_click.toggled.connect(
            self._update_feet_click_time_enabled
        )
        self._update_feet_click_time_enabled()

        # Window config
        action = self.tr("Editar") if editing else self.tr("Novo")

        self.setup_window(
            f"{self.windowTitle()} - {action}",
            self.windowIcon(),
            WindowConfig.INCREMENT_SIZE_PERCENT,
            15,
            55,
            parent,
        )

    def bind(self, controller: "PlayerKarteaConfigEditController") -> None:
        """Connect the widgets' signals to the controller.

        Called by KarteaViewFactory after the controller has filled the
        form, so the initial filling does not trigger previews; the
        sounds already selected are preloaded here.

        Parameters
        ----------
        controller : PlayerKarteaConfigEditController
            Controller of this view.

        Notes
        -----
        Also connects the "Open resources folder" buttons (a screen-only
        action), the phase combo (reloads the levels through the
        controller), the image previews (on selection change and on
        focus) and creates ``sound_effects``.
        """
        self.controller = controller

        self.pb_ok.clicked.connect(self.controller.handle_ok)
        self.pb_cancel.clicked.connect(self.controller.handle_cancel)
        # "Open resources folder" buttons do not depend on the
        # controller: they are just a screen action.
        for button_name, subdir in self.OPEN_MODS_BUTTONS.items():
            getattr(self, button_name).clicked.connect(
                partial(self.open_mods_folder, subdir)
            )

        self.cbx_current_phase.currentIndexChanged.connect(
            lambda _index: self.controller.handle_phase_changed(
                self._int_or_none(self.cbx_current_phase.currentText())
            )
        )

        # Image previews: on selection change and on combo focus
        for combo_name in self.PREVIEW_COMBOS:
            combo = getattr(self, combo_name)
            combo.installEventFilter(self)
            combo.currentTextChanged.connect(
                partial(self._preview_combo, combo_name)
            )

        # Sounds: preload on selection change (setSource "unpacks" the
        # QRC resource into RAM) so the button plays instantly.
        self.sound_effects: dict[str, QSoundEffect] = {}
        for field_name, combo_name, button_name in self.SOUND_COMBOS:
            effect = QSoundEffect(self)
            combo = getattr(self, combo_name)
            combo.currentTextChanged.connect(
                partial(self._prepare_sound, effect, field_name)
            )
            # Items already selected when the dialog opens
            self._prepare_sound(effect, field_name, combo.currentText())
            getattr(self, button_name).clicked.connect(effect.play)
            self.sound_effects[combo_name] = effect

        # Optional: initial state of the resource preview
        self.lbl_visual_current_type.setText(
            self.tr("Selecione um recurso visual para visualizar")
        )
        self.lbl_visual_preview.clear()

    def _fill_palette_choices(self) -> None:
        """Fill the palette combo box.

        Shows the translated name of each palette and keeps its number
        as the item data: the number is what goes into the player
        config. The palette description appears in the item tooltip.
        """
        self.cbx_palette.clear()
        for number, palette in KarteaPalettes.ALL.items():
            self.cbx_palette.addItem(self.tr(palette.name), number)
            self.cbx_palette.setItemData(
                self.cbx_palette.count() - 1,
                self.tr(palette.description),
                Qt.ItemDataRole.ToolTipRole,
            )

    def open_mods_folder(self, subdir: str = "", *_args) -> None:
        """Open the KarTEA mods folder in the file manager.

        Parameters
        ----------
        subdir : str, optional
            Subfolder to open (e.g. "sounds/feedback"); the mods folder
            itself if it does not exist.
        *_args
            Absorbs the ``checked`` sent by the clicked signal.
        """
        KarteaPathConfig.ensure_kartea_dirs()
        folder = KarteaPathConfig.KARTEA_MODS_DIR / subdir
        if not folder.is_dir():
            folder = KarteaPathConfig.KARTEA_MODS_DIR
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    @staticmethod
    def _resource_url(path: str) -> QUrl:
        """Return the QUrl of a resource.

        Uses the qrc scheme for ":/..." and a local file URL for the
        mods folder files (a Windows path passed straight to ``QUrl()``
        would be an invalid URL).
        """
        if path.startswith(":/"):
            return QUrl("qrc" + path)
        return QUrl.fromLocalFile(path)

    def _prepare_sound(
        self, effect: QSoundEffect, field_name: str, filename: str
    ):
        """Load the chosen sound into the memory buffer.

        ``filename`` is searched only in field ``field_name``: first
        among the built-in ones (QRC), then in the mods folder (e.g. the
        "miss" of the negative feedback, not the neutral one). Without a
        valid sound the source is cleared, so the button does not play
        the previous one.
        """
        path = KarteaPathConfig.resolve_for_field(field_name, filename)
        effect.setSource(self._resource_url(path) if path else QUrl())
        effect.setLoopCount(1)
        QCoreApplication.processEvents()

    def _preview_combo(self, combo_name: str, filename: str) -> None:
        """Show the preview of the image chosen in ``combo_name``."""
        field_name, resource_type, is_feedback = self.PREVIEW_COMBOS.get(
            combo_name, ("", self.tr("Desconhecido"), False)
        )
        # The name comes from KarteaResourceFields.ALL, marked for
        # translation with QT_TRANSLATE_NOOP in this class context.
        resource_type = self.tr(resource_type)
        if is_feedback:
            self.update_feedback_preview(filename, resource_type, field_name)
        else:
            self.update_resource_preview(filename, resource_type, field_name)

    def update_resource_preview(
        self, filename: str, resource_type: str, field_name: str = ""
    ) -> None:
        """Update the single preview of the Visual Resource tab.

        Parameters
        ----------
        filename : str
            Resource name chosen in the combo.
        resource_type : str
            Translated resource type shown above the preview.
        field_name : str, optional
            Config field used to resolve the image (built-in or mods).
        """
        self.lbl_visual_current_type.setText(
            self.tr("Visualizando: {}").format(resource_type)
        )
        self._show_preview(self.lbl_visual_preview, filename, field_name)

    def update_feedback_preview(
        self, filename: str, feedback_type: str, field_name: str = ""
    ) -> None:
        """Update the single preview of the visual feedback tab.

        Parameters
        ----------
        filename : str
            Resource name chosen in the combo.
        feedback_type : str
            Translated feedback type shown above the preview.
        field_name : str, optional
            Config field used to resolve the image (built-in or mods).
        """
        self.lbl_current_feedback_type.setText(
            self.tr("Feedback {} – Pré-visualização").format(feedback_type)
        )
        self._show_preview(self.lbl_feedback_preview, filename, field_name)

    def _show_preview(
        self, label, filename: str, field_name: str = ""
    ) -> None:
        """Show image ``filename`` of ``field_name`` in ``label``.

        The image may be built-in or from the mods folder; without a
        field it is searched among all built-in images. Shows a message
        when no image is selected or it is not found.
        """
        if not filename or not filename.strip():
            label.clear()
            label.setText(self.tr("Nenhuma imagem selecionada"))
            return

        if field_name:
            path = KarteaPathConfig.resolve_for_field(field_name, filename)
        else:
            path = KarteaPathConfig.game_builtin_image(filename)
        pixmap = QPixmap(path) if path else QPixmap()
        if pixmap.isNull():
            label.clear()
            label.setText(self.tr("Imagem não encontrada"))
            return

        label.setPixmap(
            pixmap.scaled(
                label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

    # ==================================================================
    # API used by the controller (it never touches widgets)
    # ==================================================================
    @staticmethod
    def _int_or_none(text: str) -> int | None:
        """Convert a widget text to int (None if not digits only)."""
        text = (text or "").strip()
        return int(text) if text.isdigit() else None

    def set_player_choices(self, players: Iterable[tuple[str, int]]) -> None:
        """Fill the player combo box.

        Parameters
        ----------
        players : Iterable[tuple[str, int]]
            ``(name, id)`` pairs; the id is kept as item data. No player
            is selected afterwards.
        """
        self.cbx_player.clear()
        for name, player_id in players:
            self.cbx_player.addItem(name, player_id)
        self.cbx_player.setCurrentIndex(-1)

    def set_resource_choices(
        self, resources: dict[str, list[tuple[str, str]]]
    ) -> None:
        """Fill the resource combo boxes.

        Parameters
        ----------
        resources : dict[str, list[tuple[str, str]]]
            ``{field: [(name, path), ...]}``; the path is kept as item
            data.
        """
        for field, combo_name in self.RESOURCE_COMBOS.items():
            combo = getattr(self, combo_name)
            combo.clear()
            for name, path in resources.get(field, []):
                combo.addItem(name, path)

    def set_phase_choices(self, phase_ids: Iterable[int]) -> None:
        """Fill the phase combo box (without emitting signals).

        Parameters
        ----------
        phase_ids : Iterable[int]
            Ids of the available phases.
        """
        self.cbx_current_phase.blockSignals(True)
        self.cbx_current_phase.clear()
        self.cbx_current_phase.addItems([str(p) for p in phase_ids])
        self.cbx_current_phase.blockSignals(False)

    def set_level_choices(self, level_ids: Iterable[int]) -> None:
        """Fill the level combo box.

        Parameters
        ----------
        level_ids : Iterable[int]
            Ids of the levels of the selected phase.
        """
        self.cbx_current_level.clear()
        self.cbx_current_level.addItems([str(level) for level in level_ids])

    def set_player_editable(self, editable: bool) -> None:
        """Enable or disable the player combo box.

        Parameters
        ----------
        editable : bool
            False when editing (the player cannot be changed).
        """
        self.cbx_player.setEnabled(editable)

    def set_form_data(self, data: dict[str, Any]) -> None:
        """Fill the form.

        Parameters
        ----------
        data : dict[str, Any]
            Same keys as ``get_form_data``.

        Notes
        -----
        The levels of the phase must have been loaded before
        (``set_level_choices``). Arrival times are ordered and clamped
        (KarteaArrivalTimeFields.order); an unknown palette falls back
        to the default one; a missing feet click time becomes 1.2 s.
        """
        player_id = data.get("player_id")
        self.cbx_player.setCurrentIndex(
            self.cbx_player.findData(player_id)
            if player_id is not None
            else -1
        )
        session_id = data.get("session_id")
        self.lbl_session_value.setText(
            str(session_id) if session_id is not None else ""
        )

        phase_id = data.get("phase_id")
        self.cbx_current_phase.blockSignals(True)
        self.cbx_current_phase.setCurrentText(
            str(phase_id) if phase_id is not None else ""
        )
        self.cbx_current_phase.blockSignals(False)
        level_id = data.get("level_id")
        self.cbx_current_level.setCurrentText(
            str(level_id) if level_id is not None else ""
        )

        self.spn_level_time.setValue(int(data.get("level_time") or 0))
        self._set_arrival_times(data)
        for field, combo_name in self.RESOURCE_COMBOS.items():
            getattr(self, combo_name).setCurrentText(data.get(field) or "")
        self.spn_feedback_image_time.setValue(
            float(data.get("feedback_image_time") or 0.0)
        )
        # Unknown palette (e.g. an old spin box value) falls back to the
        # default
        self.cbx_palette.setCurrentIndex(
            self.cbx_palette.findData(
                KarteaPalettes.id_of(data.get("palette"))
            )
        )
        self.chk_hud.setChecked(bool(data.get("hud")))
        self.chk_sound.setChecked(bool(data.get("sound")))
        self.chk_feet_marker.setChecked(bool(data.get("feet_marker")))
        self.chk_feet_click.setChecked(bool(data.get("feet_click")))
        feet_click_time = data.get("feet_click_time")
        self.spn_feet_click_time.setValue(
            float(feet_click_time) if feet_click_time is not None else 1.2
        )
        self._update_feet_click_time_enabled()

    def _update_feet_click_time_enabled(self, *_args) -> None:
        """Enable the feet click time only with feet click on."""
        self.spn_feet_click_time.setEnabled(self.chk_feet_click.isChecked())

    def get_form_data(self) -> dict[str, Any]:
        """Return the current form values (same keys as the service).

        Returns
        -------
        dict[str, Any]
            ``player_id``, ``session_id``, ``phase_id``, ``level_id``
            and the config fields. Arrival times are returned already
            ordered by KarteaArrivalTimeFields.order.
        """
        data: dict[str, Any] = {
            "player_id": self.cbx_player.currentData(),
            "session_id": self._int_or_none(self.lbl_session_value.text()),
            "phase_id": self._int_or_none(
                self.cbx_current_phase.currentText()
            ),
            "level_id": self._int_or_none(
                self.cbx_current_level.currentText()
            ),
            "level_time": self.spn_level_time.value(),
            "feedback_image_time": self.spn_feedback_image_time.value(),
            "palette": KarteaPalettes.id_of(self.cbx_palette.currentData()),
            "hud": self.chk_hud.isChecked(),
            "sound": self.chk_sound.isChecked(),
            "feet_marker": self.chk_feet_marker.isChecked(),
            "feet_click": self.chk_feet_click.isChecked(),
            "feet_click_time": round(self.spn_feet_click_time.value(), 2),
        }
        for field, combo_name in self.RESOURCE_COMBOS.items():
            data[field] = getattr(self, combo_name).currentText()
        data.update(
            KarteaArrivalTimeFields.order(
                {
                    field.name: getattr(self, field.widget_name).value()
                    for field in KarteaArrivalTimeFields.ALL
                }
            )
        )
        return data

    # ======================
    # Arrival times
    # ======================
    def _arrival_spin_boxes(self):
        """Return (field, spin box) pairs, slowest speed first."""
        return [
            (field, getattr(self, field.widget_name))
            for field in KarteaArrivalTimeFields.ALL
        ]

    def _reset_arrival_time_ranges(self) -> None:
        """Reset each spin box to the fixed range of its field."""
        for field, spin in self._arrival_spin_boxes():
            spin.blockSignals(True)
            spin.setRange(field.minimum, field.maximum)
            spin.setSingleStep(field.step)
            spin.blockSignals(False)

    def _update_arrival_time_ranges(self, *_args) -> None:
        """Adjust the ranges so that the speeds do not overlap.

        The next (faster) speed only accepts values below the previous
        one, and the previous one only values above the next, always
        with KarteaArrivalTimeFields.GAP of difference and within the
        fixed range of each field. This way, advancing a level never
        makes the track slower.
        """
        spins = self._arrival_spin_boxes()
        for (slow_field, slow), (fast_field, fast) in zip(spins, spins[1:]):
            fast_max = min(
                fast_field.maximum,
                round(slow.value() - KarteaArrivalTimeFields.GAP, 2),
            )
            slow_min = max(
                slow_field.minimum,
                round(fast.value() + KarteaArrivalTimeFields.GAP, 2),
            )
            for spin, minimum, maximum in (
                (fast, fast_field.minimum, fast_max),
                (slow, slow_min, slow_field.maximum),
            ):
                spin.blockSignals(True)
                spin.setRange(minimum, maximum)
                spin.blockSignals(False)

    def _set_arrival_times(self, data: dict[str, Any]) -> None:
        """Fill the arrival times, already ordered and valid."""
        times = KarteaArrivalTimeFields.order(
            {
                field.name: data[field.name]
                for field in KarteaArrivalTimeFields.ALL
                if data.get(field.name) is not None
            }
        )
        # Fixed ranges before filling: the dynamic ones of the previous
        # value could clip the new value.
        self._reset_arrival_time_ranges()
        for field, spin in self._arrival_spin_boxes():
            spin.blockSignals(True)
            spin.setValue(times[field.name])
            spin.blockSignals(False)
        self._update_arrival_time_ranges()

    def eventFilter(self, watched, event):
        """Show the preview of an image combo box when it gets focus.

        Parameters
        ----------
        watched : QObject
            Object that received the event.
        event : QEvent
            The event.

        Returns
        -------
        bool
            Result of the base ``eventFilter`` (the event is not
            consumed).
        """
        if isinstance(watched, QComboBox) and event.type() == QEvent.FocusIn:
            combo_name = watched.objectName()
            if combo_name in self.PREVIEW_COMBOS:
                self._preview_combo(combo_name, watched.currentText())
        return super().eventFilter(watched, event)
