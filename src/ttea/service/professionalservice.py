"""Professional service: business rules and persistence."""

from typing import Any, Dict, List, Optional

from PySide6.QtCore import QCoreApplication, QObject, Signal

from ttea.dao import ProfessionalCsvDAO
from ttea.model import InstitutionFacility, Professional


class ProfessionalService(QObject):
    """Business rules (service layer) of professionals.

    A single instance is shared by the whole application.

    Parameters
    ----------
    dao : ProfessionalCsvDAO | None, optional
        DAO used for persistence. Default is None, which creates a new
        ``ProfessionalCsvDAO``.

    Attributes
    ----------
    professional_change : Signal(int)
        Emitted after a change: with the ID of the created or updated
        professional, or with 0 after a deletion.
    dao : ProfessionalCsvDAO
        DAO used for persistence.
    institution_service : InstitutionFacilityService
        Facility service; its DAO is shared with the professional DAO.

    Methods
    -------
    get_all_professionals()
        Return all registered professionals.
    validate_data(data)
        Return the validation errors of the form data.
    create_professional(data)
        Create a professional from a data dictionary.
    update_professional(professional_id, data)
        Update an existing professional.
    delete_professional(professional_id)
        Delete a professional by its ID.
    find_by_id(professional_id)
        Return a professional by its ID.
    search_professionals(query="")
        Search professionals by name or ID (case-insensitive).
    get_professional_types()
        Return the translated professional types.
    get_all_institutionfacilities()
        Return all facilities sorted by name.
    get_institutionfacility_by_id(institution_id)
        Return a facility by its ID.

    Notes
    -----
    ``__new__`` always returns the same instance, and ``__init__`` sets
    it up only once: a ``dao`` passed in later calls is ignored.

    When no ``dao`` is given, the professional DAO is created with the
    DAO of ``InstitutionFacilityService``, so facilities are resolved
    from the same cache.
    """

    _instance = None
    professional_change = Signal(int)

    def __new__(cls, *args, **kwargs):
        """Return the shared instance, creating it on the first call.

        Returns
        -------
        ProfessionalService
            The single instance of the service.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, dao: Optional[ProfessionalCsvDAO] = None):
        from ttea.service import InstitutionFacilityService

        if not hasattr(self, "_initialized"):
            super().__init__()
            self.institution_service = InstitutionFacilityService()
            self.dao = dao or ProfessionalCsvDAO(
                self.institution_service.get_dao()
            )
            self._initialized = True

    def get_all_professionals(self) -> List[Professional]:
        """Return all registered professionals.

        Returns
        -------
        list[Professional]
            The professionals cached by the DAO.
        """
        return self.dao.list()

    def validate_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate the form data of a professional.

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
        be blank; ``type`` must not be 0; ``institutionfacility`` is
        required.

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

        if not data.get("institutionfacility"):
            errors.append(
                self.tr("Instituição/Estabelecimento é obrigatória!\n")
            )

        return errors

    def create_professional(
        self, data: Dict[str, Any]
    ) -> Optional[Professional]:
        """Create a professional from a dictionary.

        Parameters
        ----------
        data : dict[str, Any]
            Values for every ``Professional`` field. An ``id`` of 0 or
            less gets the next free ID.

        Returns
        -------
        Professional | None
            The created professional, or None if it is not valid or its
            ID already exists.

        Raises
        ------
        TypeError
            If ``data`` misses a field or has an unknown key.

        Notes
        -----
        ``professional_change`` is emitted with the new ID on success.
        """
        professional = Professional(**data)

        if not professional.is_valid():
            return None

        new_id = self.dao.insert(professional)
        if new_id:
            self.professional_change.emit(new_id)
        return self.dao.select(new_id) if new_id > 0 else None

    def update_professional(
        self, professional_id: int, data: Dict[str, Any]
    ) -> bool:
        """Update an existing professional with new values.

        Parameters
        ----------
        professional_id : int
            ID of the professional to update.
        data : dict[str, Any]
            Updated fields; missing keys keep the current value.

        Returns
        -------
        bool
            True if the professional was found, is valid and was saved;
            False otherwise.

        Notes
        -----
        The cached object is changed in place before validation, so an
        invalid update still changes it in memory.
        ``professional_change`` is emitted with the ID on success.
        """
        professional = self.dao.select(professional_id)
        if not professional:
            return False

        professional.set_data(data)

        if not professional.is_valid():
            return False

        success = self.dao.update(professional)

        if success:
            self.professional_change.emit(professional_id)

        return success

    def delete_professional(self, professional_id: int) -> bool:
        """Delete a professional by its ID.

        Parameters
        ----------
        professional_id : int
            ID of the professional to delete.

        Returns
        -------
        bool
            True if deleted, False if the professional was not found.

        Notes
        -----
        ``professional_change`` is emitted with 0 on success.
        """
        success = self.dao.delete(professional_id)

        if success:
            self.professional_change.emit(0)

        return success

    def find_by_id(self, professional_id: int) -> Optional[Professional]:
        """Return a professional by its ID.

        Parameters
        ----------
        professional_id : int
            ID of the professional.

        Returns
        -------
        Professional | None
            The professional, or None if not found.
        """
        return self.dao.select(professional_id)

    def search_professionals(self, query: str = "") -> List[Professional]:
        """Search professionals by name or ID, ignoring case.

        Parameters
        ----------
        query : str, optional
            Search term. If empty or blank, all professionals are
            returned. Default is ``""``.

        Returns
        -------
        list[Professional]
            The professionals whose ID (as text) or name contains the
            term.
        """
        all_professionals = self.get_all_professionals()
        if not query.strip():
            return all_professionals

        q = query.lower().strip()
        return [
            p
            for p in all_professionals
            if q in str(p.id) or q in p.name.lower()
        ]

    def get_professional_types(self) -> Dict[int, str]:
        """Return the professional types with translated names.

        Returns
        -------
        dict[int, str]
            ``Professional.TYPE_MAP`` with each name translated at
            runtime by ``QCoreApplication.translate`` in the
            ``"Professional"`` context.
        """
        return {
            key: QCoreApplication.translate("Professional", value)
            for key, value in Professional.TYPE_MAP.items()
        }

    def get_all_institutionfacilities(self) -> List[InstitutionFacility]:
        """Return all institutions/facilities sorted by name.

        Returns
        -------
        list[InstitutionFacility]
            Facilities sorted by ``name`` (case-sensitive).
        """
        return sorted(
            self.institution_service.get_all_institutionfacilities(),
            key=lambda p: p.name,
        )

    def get_institutionfacility_by_id(
        self, institution_id: int
    ) -> Optional[InstitutionFacility]:
        """Return an institution/facility by its ID.

        Parameters
        ----------
        institution_id : int
            Facility ID.

        Returns
        -------
        InstitutionFacility | None
            The facility, or None if not found.
        """
        return self.institution_service.find_by_id(institution_id)
