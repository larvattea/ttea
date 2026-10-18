"""Service of the players' Kartea game configuration.

The private module constants ``_PLAIN_FIELDS`` (configuration fields
that are not references) and ``_CREATE_DEFAULTS`` (value of each of
them when ``create_config`` does not receive it) support the service.
"""

from dataclasses import MISSING, fields
from typing import TYPE_CHECKING, Any

from ttea.games.kartea.dao import (
    PlayerKarteaConfigCsvDAO,
    PlayerKarteaSessionDetailCsvDAO,
)
from ttea.games.kartea.model import PlayerKarteaConfig, PlayerKarteaSession
from ttea.games.kartea.util import (
    KarteaIniDefaults,
    KarteaPathConfig,
    KarteaResourceFields,
)
from ttea.model import Player
from ttea.service import CalibrationService, PlayerService, ProfessionalService

from .karteahardwareservice import KarteaHardwareService
from .playerkarteasessiondetailservice import PlayerKarteaSessionDetailService
from .playerkarteasessionservice import PlayerKarteaSessionService

if TYPE_CHECKING:
    from ttea.model import Professional


# Plain config fields (the references are resolved by id)
_PLAIN_FIELDS = [
    prop
    for prop in PlayerKarteaConfig.PROPERTIES
    if prop not in PlayerKarteaConfig.REF_PROPERTIES
]

# Value of each plain field when create_config does not receive it:
# the model default or, without one, the "empty" value of its type.
_EMPTY_BY_TYPE = {int: 0, float: 0.0, bool: False, str: ""}
_CREATE_DEFAULTS = {
    f.name: (
        f.default
        if f.default is not MISSING
        else _EMPTY_BY_TYPE.get(f.type, "")
    )
    for f in fields(PlayerKarteaConfig)
    if f.name in _PLAIN_FIELDS
}
_CREATE_DEFAULTS["update_session_id"] = (
    PlayerKarteaConfig.UPDATE_SESSION_ID_YES
)


class PlayerKarteaConfigService:
    """Service layer (MVCS) with the business rules of the config.

    Hardware (screen, camera, calibration, MediaPipe) lives in
    KarteaHardwareService, available as ``hardware_service``. Phases,
    levels, progression and level rules live in KarteaPhaseService.

    Parameters
    ----------
    dao : PlayerKarteaConfigCsvDAO | None, optional
        Instance used for persistence. If None, a default
        ``PlayerKarteaConfigCsvDAO`` is created. Kept private: callers
        go through the service methods.
    calibration_service : CalibrationService | None, optional
        Used to build the hardware service when ``hardware_service`` is
        not given.
    player_service : PlayerService | None, optional
        Player service. Created if None.
    professional_service : ProfessionalService | None, optional
        Professional service. Created if None.
    hardware_service : KarteaHardwareService | None, optional
        Screen, camera, calibration and MediaPipe. Created if None.

    Attributes
    ----------
    INTERFACE_OPTIONS : tuple[str, ...], class attribute
        Interface options (bool) that can be toggled during the game:
        "hud", "sound", "feet_marker" and "feet_click".
    hardware_service : KarteaHardwareService
        Screen, camera, calibration and MediaPipe.
    player_service : PlayerService
        Access to the T-TEA players.
    professional_service : ProfessionalService
        Access to the T-TEA professionals.
    session_service : PlayerKarteaSessionService
        Session service that shares the configuration DAO's session DAO.
    session_detail_service : PlayerKarteaSessionDetailService
        Session detail service, created on first use (read-only
        property).

    Methods
    -------
    get_all_configs()
        Return all registered configs.
    create_config(data)
        Create a new config from the provided data dictionary.
    update_config(player_id, data)
        Update an existing config with the given data.
    update_config_session(player_id, session_id)
        Record the current game session in the config.
    update_config_level(player_id, phase_id, level_id)
        Record the current phase/level in the config.
    delete_config(player_id)
        Delete a config by player ID.
    find_config_by_player_id(player_id)
        Retrieve a config by player ID.
    search_configs(query="")
        Search configs by player name or ID (case-insensitive).
    get_or_create_config(player_id)
        Return the player's config, creating it with defaults if
        missing.
    set_interface_option(player_id, option, value)
        Save one of INTERFACE_OPTIONS.
    get_available_resources()
        Resources available for each resource field.
    get_default_config_data(player_id=None)
        Data of a new config, from kartea.ini.
    config_to_data(config)
        Convert a config to the form data dictionary.
    get_effective_config_data(config)
        Config data with the .ini defaults in the empty fields.
    build_game_settings(config)
        Everything the game needs to build GameSettings.

    Notes
    -----
    The session service uses the SAME session DAO as the configuration
    DAO, so a session created by the game is found when it is recorded
    in the configuration.
    """

    INTERFACE_OPTIONS = ("hud", "sound", "feet_marker", "feet_click")

    def __init__(
        self,
        dao: PlayerKarteaConfigCsvDAO | None = None,
        calibration_service: CalibrationService | None = None,
        player_service: PlayerService | None = None,
        professional_service: ProfessionalService | None = None,
        hardware_service: KarteaHardwareService | None = None,
    ):
        self._dao = dao or PlayerKarteaConfigCsvDAO()
        self.hardware_service = hardware_service or KarteaHardwareService(
            calibration_service
        )
        self.player_service = player_service or PlayerService()
        self.professional_service = (
            professional_service or ProfessionalService()
        )
        # Use the SAME session DAO as the config: a session created by
        # the game is then found when it is recorded in the config
        # (with separate instances the cache did not know it and the
        # "session" column of kartea_config was written empty).
        self.session_service = PlayerKarteaSessionService(
            dao=self._dao.session_dao
        )
        # Created on demand (see session_detail_service).
        self._session_detail_service: (
            PlayerKarteaSessionDetailService | None
        ) = None

    @property
    def session_detail_service(self) -> PlayerKarteaSessionDetailService:
        """Session detail service that shares the session DAO.

        Notes
        -----
        Created on first use (only the game records details; the
        register screens do not need to read the details CSV). A single
        instance per configuration service, so the detail ID counter is
        not duplicated between instances.
        """
        if self._session_detail_service is None:
            self._session_detail_service = PlayerKarteaSessionDetailService(
                dao=PlayerKarteaSessionDetailCsvDAO(
                    session_dao=self._dao.session_dao
                )
            )
        return self._session_detail_service

    def get_all_configs(self) -> list[PlayerKarteaConfig]:
        """Return a list of all registered configs.

        Returns
        -------
        list[PlayerKarteaConfig]
            Complete list of PlayerKarteaConfig instances stored in the
            DAO.
        """
        return self._dao.list()

    def create_config(self, data: dict[str, Any]) -> PlayerKarteaConfig | None:
        """Create a new config from a dictionary of attributes.

        Parameters
        ----------
        data : dict[str, Any]
            Same format as ``get_default_config_data``: ``player_id``,
            ``session_id``, ``phase_id``, ``level_id`` and the plain
            fields of PlayerKarteaConfig.

        Returns
        -------
        PlayerKarteaConfig | None
            The created config if validation and insertion succeed; None
            otherwise.

        Notes
        -----
        - The ids are resolved to objects through the DAOs; missing ids
          become None.
        - A missing plain field gets the model default or, without one,
          the empty value of its type (0, 0.0, False, "").
          ``update_session_id`` defaults to UPDATE_SESSION_ID_YES.
        - The config must have player, phase and level (``is_valid``).
        """
        kwargs = self._resolve_references(data)
        for field in _PLAIN_FIELDS:
            kwargs[field] = data.get(field, _CREATE_DEFAULTS[field])
        config = PlayerKarteaConfig(**kwargs)

        if not config.is_valid():
            return None

        player_id = self._dao.insert(config)
        return self._dao.select(player_id) if player_id else None

    def update_config(self, player_id: int, data: dict[str, Any]) -> bool:
        """Update an existing config.

        Parameters
        ----------
        player_id : int
            Player ID (key of the config).
        data : dict[str, Any]
            Same format as ``create_config``; only the given keys
            change.

        Returns
        -------
        bool
            True if saved; False if the config does not exist, becomes
            invalid (no player, phase or level) or the DAO rejects it.

        Notes
        -----
        Fields missing from ``data`` keep their current value; the
        references are resolved again from the current ids.
        """
        config = self._dao.select(player_id)
        if not config:
            return False

        for field, value in self._resolve_references(data, config).items():
            setattr(config, field, value)
        for field in _PLAIN_FIELDS:
            if field in data:
                setattr(config, field, data[field])

        if not config.is_valid():
            return False

        return self._dao.update(config)

    def _resolve_references(
        self,
        data: dict[str, Any],
        config: PlayerKarteaConfig | None = None,
    ) -> dict[str, Any]:
        """Look up the referenced objects by the ids in ``data``.

        Player, session, phase and level are looked up by the ``*_id``
        keys. Ids missing from ``data`` come from ``config`` (update) or
        stay None (creation).

        Returns
        -------
        dict[str, Any]
            ``player``, ``session``, ``phase`` and ``level`` objects (or
            None).
        """
        current = self.config_to_data(config) if config else {}

        def get(key: str) -> Any:
            return data.get(key, current.get(key))

        phase_id = get("phase_id")
        return {
            "player": self._dao.player_dao.select(get("player_id")),
            "session": self._dao.session_dao.select(get("session_id")),
            "phase": self._dao.phase_dao.select(phase_id),
            "level": self._dao.level_dao.select(phase_id, get("level_id")),
        }

    def update_config_session(self, player_id: int, session_id: int) -> bool:
        """Record the current game session in the player's config.

        Parameters
        ----------
        player_id : int
            Player ID.
        session_id : int
            Id of the current session.

        Returns
        -------
        bool
            True if the config was updated.

        Notes
        -----
        Only records it if the config has ``update_session_id`` = True;
        otherwise, the session recorded in the config is kept.
        """
        config = self._dao.select(player_id)
        if not config or not config.update_session_id:
            return False
        return self.update_config(player_id, {"session_id": session_id})

    def update_config_level(
        self, player_id: int, phase_id: int, level_id: int
    ) -> bool:
        """Record in the config the phase/level the game is on.

        Parameters
        ----------
        player_id : int
            Player ID.
        phase_id : int
            Current phase.
        level_id : int
            Current level.

        Returns
        -------
        bool
            True if the config holds the given phase/level.

        Notes
        -----
        The config follows the game (advance, regress, etc.), and the
        next session starts where the previous one stopped. The file is
        only rewritten when the phase or the level changes.
        """
        config = self._dao.select(player_id)
        if not config:
            return False
        if (
            config.phase
            and config.level
            and config.phase.id == phase_id
            and config.level.id == level_id
        ):
            return True
        return self.update_config(
            player_id, {"phase_id": phase_id, "level_id": level_id}
        )

    def delete_config(self, player_id: int) -> bool:
        """Delete a config by player ID.

        Parameters
        ----------
        player_id : int
            Player ID.

        Returns
        -------
        bool
            True if deleted.
        """
        return self._dao.delete(player_id)

    def find_config_by_player_id(
        self, player_id: int
    ) -> PlayerKarteaConfig | None:
        """Find a config by player ID.

        Parameters
        ----------
        player_id : int
            Player ID.

        Returns
        -------
        PlayerKarteaConfig | None
            The config, or None if the player has none.
        """
        return self._dao.select(player_id)

    def search_configs(self, query: str = "") -> list[PlayerKarteaConfig]:
        """Search configs by player name or ID.

        Parameters
        ----------
        query : str, optional
            Text searched (case-insensitive) in the player name and ID.
            An empty or blank query returns all configs.

        Returns
        -------
        list[PlayerKarteaConfig]
            Matching configs; configs without a player are left out.
        """
        all_configs = self.get_all_configs()
        if not query.strip():
            return all_configs

        q = query.lower().strip()
        return [
            c
            for c in all_configs
            if c.player
            and (q in str(c.player.id) or q in c.player.name.lower())
        ]

    def get_all_players(self) -> list[Player]:
        """Return all T-TEA players, sorted by name.

        Returns
        -------
        list[Player]
            Players from the PlayerService.
        """
        return sorted(
            self.player_service.get_all_players(),
            key=lambda p: p.name,
        )

    def get_session(self, session_id: int) -> PlayerKarteaSession | None:
        """Return a game session by id.

        Parameters
        ----------
        session_id : int
            Id of the session.

        Returns
        -------
        PlayerKarteaSession | None
            The session, or None if not found.
        """
        return self._dao.session_dao.select(session_id)

    def get_or_create_config(
        self, player_id: int
    ) -> PlayerKarteaConfig | None:
        """Return the player's config, creating it if missing.

        Parameters
        ----------
        player_id : int
            Player ID.

        Returns
        -------
        PlayerKarteaConfig | None
            The existing config, or a new one built with the kartea.ini
            defaults; None if creation fails (e.g. the
            kartea.ini defaults have no valid phase/level).
        """
        config = self.find_config_by_player_id(player_id)
        if config is None:
            config = self.create_config(
                self.get_default_config_data(player_id)
            )
        return config

    def find_player(self, player_id: int) -> Player | None:
        """Return a player by id.

        Parameters
        ----------
        player_id : int
            Player ID.

        Returns
        -------
        Player | None
            The player, or None if not found.
        """
        return self.player_service.find_by_id(player_id)

    def find_professional(self, professional_id: int) -> "Professional | None":
        """Return a professional by id.

        Parameters
        ----------
        professional_id : int
            Professional ID.

        Returns
        -------
        Professional | None
            The professional, or None if not found.
        """
        return self.professional_service.find_by_id(professional_id)

    def set_interface_option(
        self, player_id: int, option: str, value: bool
    ) -> bool:
        """Save an interface option of the player.

        Parameters
        ----------
        player_id : int
            Player ID.
        option : str
            One of INTERFACE_OPTIONS ("hud", "sound", "feet_marker" or
            "feet_click").
        value : bool
            New value.

        Returns
        -------
        bool
            True if saved; False if the player has no config yet (only
            existing configs are updated).

        Raises
        ------
        ValueError
            If ``option`` is not in INTERFACE_OPTIONS.
        """
        if option not in self.INTERFACE_OPTIONS:
            raise ValueError(f"Opção de interface inválida: {option}")
        if not self.find_config_by_player_id(player_id):
            return False
        return self.update_config(player_id, {option: value})

    # ======================
    # Resources and defaults
    # ======================
    def get_available_resources(self) -> dict[str, list[tuple[str, str]]]:
        """Return the resources available for each resource field.

        The built-in ones and, after them, the files the user placed in
        the field's mods folder.

        Returns
        -------
        dict[str, list[tuple[str, str]]]
            ``{field: [(name, path), ...]}``, with the image and sound
            fields of the config (vehicle_image, target_image, ...).
        """
        return {
            field.name: KarteaPathConfig.list_resources_for_field(field.name)
            for field in KarteaResourceFields.ALL
        }

    def get_default_config_data(
        self, player_id: int | None = None
    ) -> dict[str, Any]:
        """Return the data of a new config, from kartea.ini.

        Parameters
        ----------
        player_id : int | None, optional
            Player ID to put in the data.

        Returns
        -------
        dict[str, Any]
            Same format accepted by create_config/update_config, with
            ``session_id`` None and one entry per field of
            KarteaIniDefaults.TABLE.
        """
        ini = self.get_kartea_ini_config()
        data: dict[str, Any] = {"player_id": player_id, "session_id": None}
        for field in KarteaIniDefaults.TABLE:
            data[field] = KarteaIniDefaults.value(field, ini)
        return data

    @staticmethod
    def config_to_data(config: PlayerKarteaConfig) -> dict[str, Any]:
        """Convert the config to the dictionary used by forms.

        Parameters
        ----------
        config : PlayerKarteaConfig
            Config to convert.

        Returns
        -------
        dict[str, Any]
            Same format as get_default_config_data. References become
            ``*_id`` keys; fields without a value in the config are
            None.
        """
        data: dict[str, Any] = {
            "player_id": config.player.id if config.player else None,
            "session_id": config.session.id if config.session else None,
            "phase_id": config.phase.id if config.phase else None,
            "level_id": config.level.id if config.level else None,
        }
        for field in KarteaIniDefaults.TABLE:
            if field not in data:
                data[field] = getattr(config, field, None)
        return data

    def get_effective_config_data(
        self, config: PlayerKarteaConfig | None
    ) -> dict[str, Any]:
        """Return the config with the .ini defaults in the empty fields.

        Parameters
        ----------
        config : PlayerKarteaConfig | None
            Player's config; None returns only the defaults.

        Returns
        -------
        dict[str, Any]
            Same format as get_default_config_data; values of ``config``
            that are not None override the defaults.
        """
        data = self.get_default_config_data(
            config.player.id if config and config.player else None
        )
        if config is not None:
            for field, value in self.config_to_data(config).items():
                if value is not None:
                    data[field] = value
        return data

    def build_game_settings(
        self, config: PlayerKarteaConfig | None
    ) -> dict[str, Any]:
        """Return everything the game needs to build GameSettings.

        Parameters
        ----------
        config : PlayerKarteaConfig | None
            Player's config.

        Returns
        -------
        dict[str, Any]
            Screen settings, ``calibration_points``
            (KarteaHardwareService) and the player's effective config
            data.

        Notes
        -----
        GameSettings receives only this dictionary and does not access
        services.
        """
        return {
            **self.hardware_service.get_screen_settings(),
            "calibration_points": (
                self.hardware_service.get_calibration_points()
            ),
            **self.get_effective_config_data(config),
        }

    def get_kartea_ini_config(self) -> dict[str, str]:
        """Return the kartea.ini values.

        Returns
        -------
        dict[str, str]
            Values read by KarteaPathConfig.read_config.
        """
        return KarteaPathConfig.read_config()
