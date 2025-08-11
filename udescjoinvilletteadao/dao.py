from abc import ABC, abstractmethod
from typing import Any, List, Optional, Union


class DAO(ABC):
    """Abstract base class for Data Access Object (DAO) pattern.

    This class defines the interface for basic CRUD
    (Create, Read, Update, Delete) operations and listing functionality
    for data persistence. Concrete subclasses must implement all
    abstract methods to provide specific database operations.

    Methods
    -------
    insert(self) -> Optional[Union[int, str, bool]]
        Insert a new record into the data storage.
    update(self) -> Optional[Union[int, bool]]
        Update an existing record in the data storage.
    delete(self) -> Optional[Union[int, bool]]
        Delete a record from the data storage.
    select(self) -> Optional[Any]:
        Retrieve a single record from the data storage.
    list(self) -> List[Any]
        Retrieve a list of records from the data storage.

    Notes
    -----
    - This is an abstract base class and cannot be instantiated directly.
    - Subclasses should implement database-specific logic for each method.
    - Methods are designed to be overridden with specific implementations for
      different data storage systems (e.g., SQL, NoSQL, file-based).
    """

    @abstractmethod
    def insert(self, obj: object) -> Optional[Union[int, str, bool]]:
        """Insert a new record into the data storage.

        Parameters
        ----------
        None
            Subclasses should define specific parameters (e.g., data object,
            dictionary, or specific fields).

        Returns
        -------
        Optional[Union[int, str, bool]]
            Subclasses may return an identifier (e.g., ID of the inserted
            record) or a success indicator.

        Notes
        -----
        - Subclasses must handle the insertion logic specific to the
        data storage.
        - Should include validation and error handling for the data
        being inserted.

        Raises
        ------
        NotImplementedError
            If the method is not implemented in a subclass.
        """

    @abstractmethod
    def update(self, obj: object) -> Optional[Union[int, bool]]:
        """Update an existing record in the data storage.

        Parameters
        ----------
        None
            Subclasses should define specific parameters (e.g., record ID,
            updated data fields).

        Returns
        -------
        Optional[Union[int, bool]]
            Subclasses may return a success indicator or number of affected
            records.

        Notes
        -----
        - Subclasses must handle the update logic specific to the data storage.
        - Should include validation to ensure the record exists before
        updating.

        Raises
        ------
        NotImplementedError
            If the method is not implemented in a subclass.
        """

    @abstractmethod
    def delete(self, obj_id: int) -> Optional[Union[int, bool]]:
        """Delete a record from the data storage.

        Parameters
        ----------
        None
            Subclasses should define specific parameters (e.g., record ID).

        Returns
        -------
        Optional[Union[int, bool]]
            Subclasses may return a success indicator or number of deleted
            records.

        Notes
        -----
        - Subclasses must handle the deletion logic specific to the data
        storage.
        - Should include validation to ensure the record exists before
        deletion.

        Raises
        ------
        NotImplementedError
            If the method is not implemented in a subclass.
        """

    @abstractmethod
    def select(self, obj_id: int) -> Optional[Any]:
        """Retrieve a single record from the data storage.

        Parameters
        ----------
        None
            Subclasses should define specific parameters (e.g., record ID
            or query criteria).

        Returns
        -------
        Optional[Any]
            Subclasses should return the retrieved record or None if not found.

        Notes
        -----
        - Subclasses must implement logic to fetch a specific record based on
          provided criteria.
        - Should handle cases where the record is not found.

        Raises
        ------
        NotImplementedError
            If the method is not implemented in a subclass.
        """

    @abstractmethod
    def list(self) -> List[Any]:
        """Retrieve a list of records from the data storage.

        Parameters
        ----------
        None
            Subclasses may define optional parameters (e.g., filters,
            pagination).

        Returns
        -------
        List[Any]
            Subclasses should return a list of records or an empty list if no
            records are found.

        Notes
        -----
        - Subclasses must implement logic to fetch multiple records,
          potentially with filtering or pagination.
        - Should handle cases where no records match the criteria.

        Raises
        ------
        NotImplementedError
            If the method is not implemented in a subclass.
        """
