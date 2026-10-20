"""Player service: business rules and persistence of players."""

from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal

from ttea.dao import PlayerCsvDAO
from ttea.exception import BusinessRuleException
from ttea.model import Player


class PlayerService(QObject):
    """Business rules (service layer) of players.

    A single instance is shared by the whole application.

    Parameters
    ----------
    dao : PlayerCsvDAO | None, optional
        DAO used for persistence. Default is None, which creates a new
        ``PlayerCsvDAO``.

    Attributes
    ----------
    player_change : Signal(int)
        Emitted after a change: with the ID of the created or updated
        player, or with 0 after a deletion.
    dao : PlayerCsvDAO
        DAO used for persistence.

    Methods
    -------
    get_all_players()
        Return all registered players.
    validate_data(data)
        Return the validation errors of the form data.
    create_player(data)
        Create a player from a data dictionary.
    update_player(player_id, data)
        Update an existing player.
    delete_player(player_id)
        Delete a player by its ID.
    find_by_id(player_id)
        Return a player by its ID.
    search_players(query="")
        Search players by name or ID (case-insensitive).

    Notes
    -----
    ``__new__`` always returns the same instance, and ``__init__`` sets
    it up only once: a ``dao`` passed in later calls is ignored.
    """

    _instance = None
    player_change = Signal(int)

    def __new__(cls, *args, **kwargs):
        """Return the shared instance, creating it on the first call.

        Returns
        -------
        PlayerService
            The single instance of the service.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, dao: Optional[PlayerCsvDAO] = None):
        if not hasattr(self, "_initialized"):
            super().__init__()
            self.dao = dao or PlayerCsvDAO()
            self._initialized = True

    def get_all_players(self) -> List[Player]:
        """Return all registered players.

        Returns
        -------
        list[Player]
            The players cached by the DAO.
        """
        return self.dao.list()

    def validate_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate the form data of a player.

        Parameters
        ----------
        data : dict[str, Any]
            Form data.

        Returns
        -------
        list[str]
            Translated error messages, each ending with a newline; empty
            when the data is valid.

        Notes
        -----
        The ``id`` is required and must be an ``int``; ``name`` must not
        be blank; ``birth_date`` is required.

        The messages (pt_BR source texts) are translated at runtime with
        ``self.tr()``.
        """
        errors = []
        if data.get("id") is None:
            errors.append(self.tr("ID é obrigatório!\n"))
        elif not isinstance(data.get("id"), int):
            errors.append(self.tr("ID deve ser do tipo inteiro!\n"))

        if not data.get("name") or not data.get("name").strip():
            errors.append(self.tr("Nome é obrigatório!\n"))

        if not data.get("birth_date"):
            errors.append(self.tr("Data de nascimento é obrigatória!\n"))

        return errors

    def create_player(self, data: Dict[str, Any]) -> Optional[Player]:
        """Create a player from a dictionary.

        Parameters
        ----------
        data : dict[str, Any]
            Values for every ``Player`` field. An ``id`` of 0 or less
            gets the next free ID.

        Returns
        -------
        Player | None
            The created player, or None if it is not valid or its ID
            already exists.

        Raises
        ------
        TypeError
            If ``data`` misses a field or has an unknown key.

        Notes
        -----
        ``player_change`` is emitted with the new ID on success.
        """
        player = Player(**data)

        if not player.is_valid():
            return None

        new_id = self.dao.insert(player)
        if new_id:
            self.player_change.emit(new_id)
        return self.dao.select(new_id) if new_id > 0 else None

    def update_player(self, player_id: int, data: Dict[str, Any]) -> bool:
        """Update an existing player with new values.

        Parameters
        ----------
        player_id : int
            ID of the player to update.
        data : dict[str, Any]
            Updated fields; missing keys keep the current value.

        Returns
        -------
        bool
            True if the player was found, is valid and was saved; False
            otherwise.

        Notes
        -----
        The cached object is changed in place before validation, so an
        invalid update still changes it in memory. ``player_change`` is
        emitted with the ID on success.
        """
        player = self.dao.select(player_id)
        if not player:
            return False

        player.set_data(data)

        if not player.is_valid():
            return False

        success = self.dao.update(player)

        if success:
            self.player_change.emit(player_id)

        return success

    def delete_player(self, player_id: int) -> bool:
        """Delete a player by its ID.

        Parameters
        ----------
        player_id : int
            ID of the player to delete.

        Returns
        -------
        bool
            True if deleted, False if the player was not found.

        Raises
        ------
        BusinessRuleException
            If the player has a KarTEA configuration
            (``PlayerKarteaConfigService``); the message is translated
            with ``self.tr()``.

        Notes
        -----
        ``player_change`` is emitted with 0 on success.
        """
        from ttea.games.kartea.service import PlayerKarteaConfigService

        # Referential integrity (business rule)
        karteaconfig = PlayerKarteaConfigService()
        if karteaconfig.find_config_by_player_id(player_id):
            raise BusinessRuleException(
                self.tr(
                    "Exclusão negada: o jogador possui uma configuração do KarTEA ativa."
                )
            )

        success = self.dao.delete(player_id)

        if success:
            self.player_change.emit(0)

        return success

    def find_by_id(self, player_id: int) -> Optional[Player]:
        """Return a player by its ID.

        Parameters
        ----------
        player_id : int
            ID of the player.

        Returns
        -------
        Player | None
            The player, or None if not found.
        """
        return self.dao.select(player_id)

    def search_players(self, query: str = "") -> List[Player]:
        """Search players by name or ID, ignoring case.

        Parameters
        ----------
        query : str, optional
            Search term. If empty or blank, all players are returned.
            Default is ``""``.

        Returns
        -------
        list[Player]
            The players whose ID (as text) or name contains the term.
        """
        return self.dao.search_players(query)
