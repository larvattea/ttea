"""Generic create, update and lookup service over a DAO."""

from typing import Any, Generic, TypeVar

T = TypeVar("T")


class CsvCrudService(Generic[T]):
    """Common rules of the session and session detail services.

    Subclasses define ``model`` (dataclass) and ``dao_class`` (DAO used
    when none is given).

    Parameters
    ----------
    dao : Any | None, optional
        DAO to use (e.g. the one shared by the configuration service).
        If None, ``dao_class()`` is created. Kept private: callers use
        only the service methods.

    Attributes
    ----------
    model : type, class attribute
        Model dataclass built by ``create``. Defined by the subclass.
    dao_class : type, class attribute
        DAO class instantiated when no ``dao`` is given. Defined by the
        subclass.
    """

    model: type
    dao_class: type

    def __init__(self, dao: Any | None = None):
        self._dao = dao or self.dao_class()

    def create(self, data: dict[str, Any]) -> T | None:
        """Create and save a record.

        Parameters
        ----------
        data : dict[str, Any]
            Constructor arguments of ``model``.

        Returns
        -------
        T | None
            The saved record, or None if the DAO rejected it as invalid.
        """
        new_id = self._dao.insert(self.model(**data))
        return self._dao.select(new_id) if new_id > 0 else None

    def update(self, obj_id: int, data: dict[str, Any]) -> bool:
        """Update the fields in ``data`` on the record and save it.

        Parameters
        ----------
        obj_id : int
            Id of the record.
        data : dict[str, Any]
            New values; keys that are not model fields are ignored
            (``set_data``).

        Returns
        -------
        bool
            True if saved; False if the record does not exist or the DAO
            rejected it.
        """
        obj = self._dao.select(obj_id)
        if not obj:
            return False
        obj.set_data(data)
        return self._dao.update(obj)

    def find_by_id(self, obj_id: int) -> T | None:
        """Return the record with the given id.

        Parameters
        ----------
        obj_id : int
            Id of the record.

        Returns
        -------
        T | None
            The record, or None if not found.
        """
        return self._dao.select(obj_id)
