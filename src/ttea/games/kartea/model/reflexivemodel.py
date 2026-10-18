"""Common base of the KarTEA data models.

Gathers what used to be copied in each file of ``model/``: the
``initialize_reflexive`` decorator (PROPERTIES and DATA_PROPERTIES) and
the ``set_data``/``get_data`` methods.
"""

from dataclasses import fields
from enum import Enum
from typing import ClassVar


def initialize_reflexive(cls):
    """Fill the reflection class attributes of a dataclass.

    Parameters
    ----------
    cls : type
        The dataclass to be decorated.

    Returns
    -------
    type
        The same class, with PROPERTIES and DATA_PROPERTIES filled.

    Notes
    -----
    - ``PROPERTIES`` receives the names of all dataclass fields.
    - ``DATA_PROPERTIES`` receives the default value of each init
      field (``dataclasses.MISSING`` when the field has none).
    - Must be applied above ``@dataclass``, since it reads the fields
      created by it.

    Examples
    --------
    >>> from dataclasses import dataclass
    >>> @initialize_reflexive
    ... @dataclass
    ... class Point(ReflexiveModel):
    ...     x: int
    ...     y: int = 0
    >>> Point.PROPERTIES
    ['x', 'y']
    >>> Point.DATA_PROPERTIES[1]
    0
    """
    cls.PROPERTIES = [field.name for field in fields(cls)]
    cls.DATA_PROPERTIES = [
        field.default for field in fields(cls) if field.init
    ]
    return cls


class ReflexiveModel:
    """Mixin with ``set_data``/``get_data`` based on PROPERTIES.

    Subclasses (dataclasses decorated with ``initialize_reflexive``)
    declare in ``REF_PROPERTIES`` the fields that reference another
    model: in ``get_data`` they become the ``id`` of the referenced
    object (or None). Enum values become their ``value``.

    Attributes
    ----------
    PROPERTIES : ClassVar[list[str]], class attribute
        Field names of the model, filled by ``initialize_reflexive``.
    DATA_PROPERTIES : ClassVar[list], class attribute
        Default value of each init field, filled by
        ``initialize_reflexive``.
    REF_PROPERTIES : ClassVar[tuple[str, ...]], class attribute
        Fields that reference another model. Empty by default.

    Examples
    --------
    >>> from dataclasses import dataclass
    >>> from types import SimpleNamespace
    >>> @initialize_reflexive
    ... @dataclass
    ... class Item(ReflexiveModel):
    ...     id: int
    ...     owner: object
    ...     REF_PROPERTIES = ("owner",)
    >>> item = Item(id=7, owner=SimpleNamespace(id=3))
    >>> item.get_data()
    [{'id': 7, 'owner': 3}]
    >>> item.set_data({"id": 8, "unknown": 1})
    >>> item.id
    8
    """

    PROPERTIES: ClassVar[list[str]] = []
    DATA_PROPERTIES: ClassVar[list] = []
    REF_PROPERTIES: ClassVar[tuple[str, ...]] = ()

    def set_data(self, data: dict) -> None:
        """Update attributes from a dictionary.

        Parameters
        ----------
        data : dict
            New values, keyed by field name.

        Notes
        -----
        Only keys present in PROPERTIES are applied; other keys are
        ignored. No validation or type conversion is performed on the
        input data.
        """
        for prop in self.PROPERTIES:
            if prop in data:
                setattr(self, prop, data[prop])

    def get_data(self) -> list[dict]:
        """Return the model data as a list with one dictionary.

        Returns
        -------
        list[dict]
            A single dictionary with one entry per field of PROPERTIES.
            A list is returned for consistency with potential
            multi-record returns.

        Notes
        -----
        - References (REF_PROPERTIES) are replaced by their ``id``. A
          value without ``id`` (e.g. text already read from the CSV) is
          kept as is, and a falsy value (None, 0, "") becomes None.
        - Enum values are replaced by their ``value``.

        Examples
        --------
        >>> from dataclasses import dataclass
        >>> @initialize_reflexive
        ... @dataclass
        ... class Item(ReflexiveModel):
        ...     id: int
        ...     owner: object
        ...     REF_PROPERTIES = ("owner",)
        >>> Item(id=7, owner="3").get_data()
        [{'id': 7, 'owner': '3'}]
        >>> Item(id=7, owner=None).get_data()
        [{'id': 7, 'owner': None}]
        """
        info = {}
        for prop in self.PROPERTIES:
            value = getattr(self, prop)
            if prop in self.REF_PROPERTIES:
                # Object -> id; a value already in id form (e.g. text
                # read from the CSV) is kept.
                value = getattr(value, "id", value) if value else None
            elif isinstance(value, Enum):
                value = value.value
            info[prop] = value
        return [info]
