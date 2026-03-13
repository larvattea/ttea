# udescjoinvillettea/service/healthprofessionalservice.py
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal

# Local module import
from udescjoinvilletteadao import HealthProfessionalCsvDAO
from udescjoinvilletteamodel import HealthProfessional, InstitutionFacility


class HealthProfessionalService(QObject):
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
    get_all_healthprofessionals()
        Returns all registered healthprofessionals.
    create_healthprofessional(data)
        Creates a new healthprofessional from the provided data dictionary.
    update_healthprofessional(healthprofessional_id, data)
        Updates an existing healthprofessional with the given data.
    delete_healthprofessional(healthprofessional_id)
        Deletes a healthprofessional by its ID.
    find_by_id(healthprofessional_id)
        Retrieves a healthprofessional by its ID.
    search_healthprofessionals(query="")
        Searches healthprofessionals by name or ID (case-insensitive).
    """

    _instance = None
    # Sinal que avisa: "Se os dados mudaram"
    healthprofessional_change = Signal(int)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, dao: Optional[HealthProfessionalCsvDAO] = None):
        """
        Initialize the service with a data access object.

        Parameters
        ----------
        dao : InstitutionFacilityCsvDAO, optional
            Instance used for persistence. If ``None``, a default
            ``InstitutionFacilityCsvDAO`` is created.
        """
        from udescjoinvilletteaservice import InstitutionFacilityService

        if not hasattr(self, "_initialized"):
            super().__init__()
            self.institution_service = InstitutionFacilityService()
            self.dao = dao or HealthProfessionalCsvDAO(
                self.institution_service.get_dao()
            )
            self._initialized = True

    def get_all_healthprofessionals(self) -> List[HealthProfessional]:
        """Return a list of all registered healthprofessionals.

        Returns
        -------
        List[InstitutionFacility]
            Complete list of ``InstitutionFacility`` instances stored
            in the DAO.
        """
        return self.dao.list()

    def validate_data(self, data: Dict[str, Any]) -> List[str]:
        """
        Valida as regras de negócio para os dados de uma instituição.
        Retorna uma lista de mensagens de erro (vazia se estiver tudo ok).
        """
        errors = []
        if data.get("id") is None:
            errors.append(self.tr("ID é obrigatório!\n"))
        elif not isinstance(data.get("id"), int):
            errors.append(self.tr("ID deve ser do tipo inteiro!\n"))

        if not data.get("name") or not data.get("name").strip():
            errors.append(self.tr("Nome é obrigatório!\n"))

        if data.get("type") == 0:
            errors.append(self.tr("Tipo é obrigatório!\n"))

        return errors

    def create_healthprofessional(
        self, data: Dict[str, Any]
    ) -> Optional[HealthProfessional]:
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
        healthprofessional = HealthProfessional(**data)

        if not healthprofessional.is_valid():
            return None

        new_id = self.dao.insert(healthprofessional)
        if new_id:
            self.healthprofessional_change.emit(new_id)
        return self.dao.select(new_id) if new_id > 0 else None

    def update_healthprofessional(
        self, healthprofessional_id: int, data: Dict[str, Any]
    ) -> bool:
        """
        Update an existing healthprofessional with new values.

        Parameters
        ----------
        healthprofessional_id : int
            Identifier of the healthprofessional to update.
        data : dict
            Dictionary containing updated fields. Missing keys keep the
            current value.

        Returns
        -------
        bool
            ``True`` if the healthprofessional was found, validated,
            and updated successfully; ``False`` otherwise.
        """
        healthprofessional = self.dao.select(healthprofessional_id)
        if not healthprofessional:
            return False

        healthprofessional.set_data(data)

        if not healthprofessional.is_valid():
            return False

        success = self.dao.update(healthprofessional)

        if success:
            self.healthprofessional_change.emit(healthprofessional_id)

        return success

    def delete_healthprofessional(self, healthprofessional_id: int) -> bool:
        """Delete a healthprofessional by its identifier.

        Parameters
        ----------
        healthprofessional_id : int
            Identifier of the healthprofessional to be removed.

        Returns
        -------
        bool
            ``True`` if the healthprofessional was successfully deleted,
            ``False`` otherwise (e.g., healthprofessional not found).
        """
        success = self.dao.delete(healthprofessional_id)

        if success:
            self.institutionfacility_change.emit(0)

        return success

    def find_by_id(
        self, healthprofessional_id: int
    ) -> Optional[HealthProfessional]:
        """Retrieve a healthprofessional by its unique identifier.

        Parameters
        ----------
        healthprofessional_id : int
            The healthprofessional's ID.

        Returns
        -------
        HealthProfessional or None
            The matching ``HealthProfessional`` instance
            or ``None`` if not found.
        """
        return self.dao.select(healthprofessional_id)

    def search_healthprofessionals(
        self, query: str = ""
    ) -> List[HealthProfessional]:
        """
        Search healthprofessionals by name or ID (case-insensitive).

        Parameters
        ----------
        query : str, optional
            Search term. If empty or whitespace-only, returns all
            healthprofessionals.

        Returns
        -------
        List[InstitutionFacility]
            List of healthprofessionals whose ID (as string)
            or name contain the query term.
        """
        all_healthprofessionals = self.get_all_healthprofessionals()
        if not query.strip():
            return all_healthprofessionals

        q = query.lower().strip()
        return [
            p
            for p in all_healthprofessionals
            if q in str(p.id) or q in p.name.lower()
        ]

    def get_healthprofessional_types(self) -> Dict[int, str]:
        return HealthProfessional.TYPE_MAP

    def get_all_institutionfacilities(self) -> List[InstitutionFacility]:
        return sorted(
            self.institution_service.get_all_institutionfacilities(),
            key=lambda p: p.name,
        )

    def get_institutionfacility_by_id(
        self, institution_id: int
    ) -> Optional[InstitutionFacility]:
        return self.institution_service.find_by_id(institution_id)
