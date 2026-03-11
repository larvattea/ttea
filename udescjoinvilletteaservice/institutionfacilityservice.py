# udescjoinvillettea/service/institutionfacility_service.py
from typing import Any, Dict, List, Optional

from udescjoinvilletteadao import InstitutionFacilityCsvDAO
from udescjoinvilletteamodel import InstitutionFacility


class InstitutionFacilityService:
    """
    Service layer (MVCS) handling all business rules related to insti.

    Attributes
    ----------
    dao : InstitutionFacilityCsvDAO
        Data access object responsible for persistence operations.
        Defaults to a new ``InstitutionFacilityCsvDAO``
        instance if not provided.

    Methods
    -------
    __init__(dao=None)
        Initializes the service with a DAO instance.
    get_all_institutionfacilities()
        Returns all registered institutionfacilities.
    create_institutionfacility(data)
        Creates a new institutionfacility from the provided data dictionary.
    update_institutionfacility(institutionfacility_id, data)
        Updates an existing institutionfacility with the given data.
    delete_institutionfacility(institutionfacility_id)
        Deletes a institutionfacility by its ID.
    find_by_id(institutionfacility_id)
        Retrieves a institutionfacility by its ID.
    search_institutionfacilities(query="")
        Searches institutionfacilities by name or ID (case-insensitive).
    """

    def __init__(self, dao: Optional[InstitutionFacilityCsvDAO] = None):
        """
        Initialize the service with a data access object.

        Parameters
        ----------
        dao : InstitutionFacilityCsvDAO, optional
            Instance used for persistence. If ``None``, a default
            ``InstitutionFacilityCsvDAO`` is created.
        """
        self.dao = dao or InstitutionFacilityCsvDAO()

    def get_all_institutionfacilities(self) -> List[InstitutionFacility]:
        """Return a list of all registered institutionfacilities.

        Returns
        -------
        List[InstitutionFacility]
            Complete list of ``InstitutionFacility`` instances stored
            in the DAO.
        """
        return self.dao.list()

    def create_institutionfacility(
        self, data: Dict[str, Any]
    ) -> Optional[InstitutionFacility]:
        """
        Create a new InstitutionFacility from a dictionary of attributes.

        Parameters
        ----------
        data : dict
            Must contain the keys the attributes.

        Returns
        -------
        InstitutionFacility or None
            The created ``InstitutionFacility`` instance if validation
            and insertion succeed; ``None`` otherwise.
        """
        institutionfacility = InstitutionFacility(**data)

        if not institutionfacility.is_valid():
            return None

        new_id = self.dao.insert(institutionfacility)
        return self.dao.select(new_id) if new_id > 0 else None

    def update_institutionfacility(
        self, institutionfacility_id: int, data: Dict[str, Any]
    ) -> bool:
        """
        Update an existing institutionfacility with new values.

        Parameters
        ----------
        institutionfacility_id : int
            Identifier of the institutionfacility to update.
        data : dict
            Dictionary containing updated fields. Missing keys keep the
            current value.

        Returns
        -------
        bool
            ``True`` if the institutionfacility was found, validated,
            and updated successfully; ``False`` otherwise.
        """
        institutionfacility = self.dao.select(institutionfacility_id)
        if not institutionfacility:
            return False

        institutionfacility.set_data(data)

        if not institutionfacility.is_valid():
            return False

        return self.dao.update(institutionfacility)

    def delete_institutionfacility(self, institutionfacility_id: int) -> bool:
        """Delete a institutionfacility by its identifier.

        Parameters
        ----------
        institutionfacility_id : int
            Identifier of the institutionfacility to be removed.

        Returns
        -------
        bool
            ``True`` if the institutionfacility was successfully deleted,
            ``False`` otherwise (e.g., institutionfacility not found).
        """
        return self.dao.delete(institutionfacility_id)

    def find_by_id(
        self, institutionfacility_id: int
    ) -> Optional[InstitutionFacility]:
        """Retrieve a institutionfacility by its unique identifier.

        Parameters
        ----------
        institutionfacility_id : int
            The institutionfacility's ID.

        Returns
        -------
        InstitutionFacility or None
            The matching ``InstitutionFacility`` instance
            or ``None`` if not found.
        """
        return self.dao.select(institutionfacility_id)

    def search_institutionfacilities(
        self, query: str = ""
    ) -> List[InstitutionFacility]:
        """
        Search institutionfacilities by name or ID (case-insensitive).

        Parameters
        ----------
        query : str, optional
            Search term. If empty or whitespace-only, returns all
            institutionfacilities.

        Returns
        -------
        List[InstitutionFacility]
            List of institutionfacilities whose ID (as string)
            or name contain the query term.
        """
        all_institutionfacilities = self.get_all_institutionfacilities()
        if not query.strip():
            return all_institutionfacilities

        q = query.lower().strip()
        return [
            p
            for p in all_institutionfacilities
            if q in str(p.id) or q in p.name.lower()
        ]

    def get_institutionfacility_types(self) -> Dict[int, str]:
        return InstitutionFacility.TYPE_MAP
