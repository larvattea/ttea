"""Controller of the player Kartea configuration create/edit dialog."""

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QObject

from ttea.games.kartea.util import KarteaResourceFields
from ttea.util import MessageService

if TYPE_CHECKING:
    from ttea.games.kartea.model import PlayerKarteaConfig
    from ttea.games.kartea.service import (
        KarteaPhaseService,
        PlayerKarteaConfigService,
    )
    from ttea.games.kartea.view import PlayerKarteaConfigEditView


class PlayerKarteaConfigEditController(QObject):
    """Controller for the player Kartea config edit/create dialog.

    Manages the interaction between PlayerKarteaConfigEditView and the
    PlayerKarteaConfig model, including field population, input
    validation, and data extraction. The controller talks to the view
    only through its form API (set_form_data, get_form_data,
    set_*_choices) and to data only through the injected services.

    Parameters
    ----------
    view : PlayerKarteaConfigEditView
        The associated dialog view.
    config : PlayerKarteaConfig | None
        Config object to edit; None creates a new config.
    service : PlayerKarteaConfigService
        Shared service (injected by the view factory).
    phase_service : KarteaPhaseService
        Phases and levels offered in the form.
    message_service : MessageService | None, optional
        Custom message service; defaults to ``MessageService(view)``.

    Attributes
    ----------
    view : PlayerKarteaConfigEditView
        The dialog view containing the input widgets.
    config : PlayerKarteaConfig | None
        Config instance being edited, or None when creating a new
        config.
    ok_clicked : bool
        True if the dialog was accepted with valid data.
    service : PlayerKarteaConfigService
        Config service (players, resources, defaults).
    phase_service : KarteaPhaseService
        Phase service (phase and level choices).
    msg : MessageService
        Service used to display validation/error messages.

    Methods
    -------
    handle_phase_changed(phase_id)
        Reload the level choices for the selected phase.
    handle_ok()
        Validate inputs and accept dialog if valid.
    handle_cancel()
        Reject dialog without saving changes.
    is_input_valid()
        Check required fields and show errors if needed.
    get_data()
        Extract entered data as a dictionary.

    Notes
    -----
    On creation the controller fills the player, resource and phase
    choices and the form: with the config data when editing (the player
    then cannot be changed) or with the kartea.ini defaults when
    creating.

    The validation messages are translated with ``self.tr()`` in the
    "PlayerKarteaConfigEditController" context (i18n).
    """

    def __init__(
        self,
        view: "PlayerKarteaConfigEditView",
        config: "PlayerKarteaConfig | None",
        service: "PlayerKarteaConfigService",
        phase_service: "KarteaPhaseService",
        message_service: MessageService | None = None,
    ) -> None:
        super().__init__()

        self.view = view
        self.config = config
        self.ok_clicked = False
        self.service = service
        self.phase_service = phase_service
        self.msg = message_service or MessageService(view)

        # Combo box choices
        self.view.set_player_choices(
            (p.name, p.id) for p in self.service.get_all_players()
        )
        self.view.set_resource_choices(self.service.get_available_resources())
        self.view.set_phase_choices(
            p.id for p in self.phase_service.get_all_phases()
        )

        # Form data: existing config or the .ini defaults
        if self.config:
            data = self.service.config_to_data(self.config)
            self.view.set_player_editable(False)
        else:
            data = self.service.get_default_config_data()

        self.handle_phase_changed(data.get("phase_id"))
        self.view.set_form_data(data)

    def handle_phase_changed(self, phase_id: int | None) -> None:
        """Load in the view the levels of the selected phase.

        Parameters
        ----------
        phase_id : int | None
            Selected phase; None clears the level choices.
        """
        levels = (
            self.phase_service.get_levels_for_phase(phase_id)
            if phase_id is not None
            else []
        )
        self.view.set_level_choices(level.id for level in levels)

    def handle_ok(self) -> None:
        """Validate input and close the dialog with acceptance.

        If validation passes, sets ``ok_clicked`` to True and accepts
        the dialog. Otherwise ``is_input_valid`` shows a critical
        message with the errors and the dialog stays open.
        """
        if self.is_input_valid():
            self.ok_clicked = True
            self.view.accept()

    def handle_cancel(self) -> None:
        """Close the dialog without saving changes.

        Rejects the dialog, discarding any entered data.
        """
        self.view.reject()

    def is_input_valid(self) -> bool:
        """Validate required fields.

        Checks that the player, the phase and level, and the required
        resources (KarteaResourceFields) are filled. Shows a critical
        message listing all errors if validation fails.

        Returns
        -------
        bool
            True if all inputs are valid, False otherwise.

        Notes
        -----
        Resource fields that share the same message (environment
        right/left) produce a single error line. The messages are
        translated with ``self.tr()``: the resource messages are the
        ``QT_TRANSLATE_NOOP`` source texts of KarteaResourceFields
        (i18n).
        """
        data = self.view.get_form_data()
        error_message = ""

        if data["player_id"] is None:
            error_message += self.tr("Jogador é obrigatório!\n")
        if data["phase_id"] is None or data["level_id"] is None:
            error_message += self.tr("Fase e nível são obrigatórios!\n")
        # Required resources (KarteaResourceFields.ALL)
        missing = []
        for field in KarteaResourceFields.ALL:
            if (
                field.required
                and not data[field.name]
                and field.required_message not in missing
            ):
                missing.append(field.required_message)
        for message in missing:
            error_message += self.tr(message)

        if error_message:
            self.msg.critical(
                self.tr("Por favor, corrija os dados inválidos:\n")
                + error_message
            )
            return False
        return True

    def get_data(self) -> dict[str, Any]:
        """Return the current form values.

        Same format that create_config/update_config expect.

        Returns
        -------
        dict[str, Any]
            ``player_id``, ``session_id``, ``phase_id``, ``level_id``
            and the other config fields. The service resolves the ids
            into objects.
        """
        return self.view.get_form_data()
