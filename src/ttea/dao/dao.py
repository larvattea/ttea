"""Generic DAO interface for the persistence classes."""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")


class DAO(ABC, Generic[T]):
    """Generic interface for CRUD operations on persistent entities.

    This abstract base class defines the data access object (DAO)
    pattern with type-safe operations for any entity type ``T``.

    Methods
    -------
    insert(obj)
        Insert a new object and return its identifier.
    update(obj)
        Update an existing object in the persistent storage.
    delete(obj_id)
        Delete the object with the given identifier.
    select(obj_id)
        Retrieve an object by its identifier.
    list()
        Retrieve all objects of type ``T``.
    """

    @abstractmethod
    def insert(self, obj: T) -> int:
        """Insert a new object and return its identifier.

        Parameters
        ----------
        obj : T
            The object instance to be persisted.

        Returns
        -------
        int
            The identifier assigned to the new object. Most
            implementations return 0 on failure.
        """

    @abstractmethod
    def update(self, obj: T) -> bool:
        """Update an existing object in the persistent storage.

        Parameters
        ----------
        obj : T
            The object with updated values. Its identifier must match an
            existing record.

        Returns
        -------
        bool
            True if the object was updated, False otherwise (e.g. if the
            object does not exist).
        """

    @abstractmethod
    def delete(self, obj_id: int) -> bool:
        """Remove the object with the given identifier.

        Parameters
        ----------
        obj_id : int
            Identifier of the object to be deleted.

        Returns
        -------
        bool
            True if the object was deleted, False otherwise (e.g. if no
            object has the given ID).
        """
        pass

    @abstractmethod
    def select(self, obj_id: int) -> Optional[T]:
        """Retrieve an object by its identifier.

        Parameters
        ----------
        obj_id : int
            Identifier of the object to retrieve.

        Returns
        -------
        T | None
            The object if found, or None if no object matches the ID.
        """

    @abstractmethod
    def list(self) -> List[T]:
        """Return all persisted objects of type ``T``.

        Returns
        -------
        list[T]
            All objects currently stored.
        """
