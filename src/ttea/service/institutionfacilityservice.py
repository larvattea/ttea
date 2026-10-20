"""Institution/facility service: business rules and persistence."""

from typing import Any, Dict, List, Optional

from PySide6.QtCore import QCoreApplication, QObject, Signal

from ttea.dao import InstitutionFacilityCsvDAO
from ttea.exception import BusinessRuleException
from ttea.model import InstitutionFacility


class InstitutionFacilityService(QObject):
    """Business rules (service layer) of institution facilities.

    A single instance is shared by the whole application.

    Parameters
    ----------
    dao : InstitutionFacilityCsvDAO | None, optional
        DAO used for persistence. Default is None, which creates a new
        ``InstitutionFacilityCsvDAO``.

    Attributes
    ----------
    institutionfacility_change : Signal(int)
        Emitted after a change: with the ID of the created or updated
        institution facility, or with 0 after a deletion.
    dao : InstitutionFacilityCsvDAO
        DAO used for persistence.

    Methods
    -------
    get_all_institutionfacilities()
        Return all registered institution facilities.
    validate_data(data)
        Return the validation errors of the form data.
    create_institutionfacility(data)
        Create an institution facility from a data dictionary.
    update_institutionfacility(institutionfacility_id, data)
        Update an existing institution facility.
    delete_institutionfacility(institutionfacility_id)
        Delete an institution facility by its ID.
    find_by_id(institutionfacility_id)
        Return an institution facility by its ID.
    search_institutionfacilities(query="")
        Search institution facilities by name or ID (case-insensitive).
    get_institutionfacility_types()
        Return the translated facility types.
    get_dao()
        Return the DAO of the service.

    Notes
    -----
    ``__new__`` always returns the same instance, and ``__init__`` sets
    it up only once: a ``dao`` passed in later calls is ignored.
    """

    _instance = None
    institutionfacility_change = Signal(int)

    def __new__(cls, *args, **kwargs):
        """Return the shared instance, creating it on the first call.

        Returns
        -------
        InstitutionFacilityService
            The single instance of the service.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, dao: Optional[InstitutionFacilityCsvDAO] = None):
        if not hasattr(self, "_initialized"):
            super().__init__()
            self.dao = dao or InstitutionFacilityCsvDAO()
            self._initialized = True

    def get_all_institutionfacilities(self) -> List[InstitutionFacility]:
        """Return all registered institution facilities.

        Returns
        -------
        list[InstitutionFacility]
            The institution facilities cached by the DAO.
        """
        return self.dao.list()

    def validate_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate the form data of an institution facility.

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
        be blank; ``type`` must not be 0.

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

        if data.get("type") == 0:
            errors.append(self.tr("Tipo é obrigatório!\n"))

        return errors

    def create_institutionfacility(
        self, data: Dict[str, Any]
    ) -> Optional[InstitutionFacility]:
        """Create an institution facility from a dictionary.

        Parameters
        ----------
        data : dict[str, Any]
            Values for every ``InstitutionFacility`` field. An ``id`` of
            0 or less gets the next free ID.

        Returns
        -------
        InstitutionFacility | None
            The created institution facility, or None if it is not valid
            or its ID already exists.

        Raises
        ------
        TypeError
            If ``data`` misses a field or has an unknown key.

        Notes
        -----
        ``institutionfacility_change`` is emitted with the new ID on
        success.
        """
        institutionfacility = InstitutionFacility(**data)

        if not institutionfacility.is_valid():
            return None

        new_id = self.dao.insert(institutionfacility)
        if new_id:
            self.institutionfacility_change.emit(new_id)
        return self.dao.select(new_id) if new_id > 0 else None

    def update_institutionfacility(
        self, institutionfacility_id: int, data: Dict[str, Any]
    ) -> bool:
        """Update an existing institution facility with new values.

        Parameters
        ----------
        institutionfacility_id : int
            ID of the institution facility to update.
        data : dict[str, Any]
            Updated fields; missing keys keep the current value.

        Returns
        -------
        bool
            True if the institution facility was found, is valid and was
            saved; False otherwise.

        Notes
        -----
        The cached object is changed in place before validation, so an
        invalid update still changes it in memory.
        ``institutionfacility_change`` is emitted with the ID on
        success.
        """
        institutionfacility = self.dao.select(institutionfacility_id)
        if not institutionfacility:
            return False

        institutionfacility.set_data(data)

        if not institutionfacility.is_valid():
            return False

        success = self.dao.update(institutionfacility)

        if success:
            self.institutionfacility_change.emit(institutionfacility_id)

        return success

    def delete_institutionfacility(self, institutionfacility_id: int) -> bool:
        """Delete an institution facility by its ID.

        Parameters
        ----------
        institutionfacility_id : int
            ID of the institution facility to delete.

        Returns
        -------
        bool
            True if deleted, False if the institution facility was not
            found.

        Raises
        ------
        BusinessRuleException
            If a professional is linked to the facility; the message is
            translated with ``self.tr()``.

        Notes
        -----
        ``institutionfacility_change`` is emitted with 0 on success. A
        professional without a facility (None) makes the check raise
        ``AttributeError``.
        """
        from ttea.service import ProfessionalService

        # Referential integrity (business rule)
        professional_service = ProfessionalService()
        professionals = professional_service.get_all_professionals()
        if any(
            professional.institutionfacility.id == institutionfacility_id
            for professional in professionals
        ):
            raise BusinessRuleException(
                self.tr(
                    "Exclusão negada: a instituição possui profissional vinculado."
                )
            )

        success = self.dao.delete(institutionfacility_id)

        if success:
            self.institutionfacility_change.emit(0)

        return success

    def find_by_id(
        self, institutionfacility_id: int
    ) -> Optional[InstitutionFacility]:
        """Return an institution facility by its ID.

        Parameters
        ----------
        institutionfacility_id : int
            ID of the institution facility.

        Returns
        -------
        InstitutionFacility | None
            The institution facility, or None if not found.
        """
        return self.dao.select(institutionfacility_id)

    def search_institutionfacilities(
        self, query: str = ""
    ) -> List[InstitutionFacility]:
        """Search institution facilities by name or ID, ignoring case.

        Parameters
        ----------
        query : str, optional
            Search term. If empty or blank, all institution facilities
            are returned. Default is ``""``.

        Returns
        -------
        list[InstitutionFacility]
            The institution facilities whose ID (as text) or name
            contains the term.
        """
        return self.dao.search_institutionfacilities(query)

    def get_institutionfacility_types(self) -> Dict[int, str]:
        """Return the facility types with translated names.

        Returns
        -------
        dict[int, str]
            ``InstitutionFacility.TYPE_MAP`` with each name translated
            at runtime by ``QCoreApplication.translate`` in the
            ``"InstitutionFacility"`` context.
        """
        # return InstitutionFacility.TYPE_MAP
        return {
            key: QCoreApplication.translate("InstitutionFacility", value)
            for key, value in InstitutionFacility.TYPE_MAP.items()
        }

    def get_dao(self) -> InstitutionFacilityCsvDAO:
        """Return the DAO instance used by this service.

        Returns
        -------
        InstitutionFacilityCsvDAO
            The DAO, shared with ``ProfessionalService`` so both use the
            same facility cache.
        """
        return self.dao
