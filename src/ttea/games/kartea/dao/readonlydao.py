"""Base of the read-only DAOs of KarTEA."""

from typing import Any

from ttea.dao import DAO


class ReadOnlyDAO(DAO):
    """Read-only DAO: insert, update and delete are not supported.

    Used by the phase and level DAOs, read from the phase CSV files
    (resources/phases), which the game does not change.
    """

    def insert(self, obj: object) -> Any | None:
        """Not supported: the data are read-only.

        Parameters
        ----------
        obj : object
            Object that would be inserted (ignored).

        Raises
        ------
        NotImplementedError
            Always.
        """
        raise NotImplementedError

    def update(self, obj: object) -> Any | None:
        """Not supported: the data are read-only.

        Parameters
        ----------
        obj : object
            Object that would be updated (ignored).

        Raises
        ------
        NotImplementedError
            Always.
        """
        raise NotImplementedError

    def delete(self, obj_id: int) -> Any | None:
        """Not supported: the data are read-only.

        Parameters
        ----------
        obj_id : int
            Id of the object that would be deleted (ignored).

        Raises
        ------
        NotImplementedError
            Always.
        """
        raise NotImplementedError
