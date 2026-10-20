"""INI persistence of the ``CalibrationSetting`` record (QSettings)."""

from typing import List, Optional

from PySide6.QtCore import QSettings

from ttea.model import CalibrationSetting
from ttea.util import PathConfig

# Import DAO directly to avoid a circular import
from .dao import DAO


class CalibrationSettingIniDAO(DAO[CalibrationSetting]):
    """DAO for the single ``CalibrationSetting`` record in an INI file.

    Attributes
    ----------
    settings : QSettings
        INI file opened at ``PathConfig.calibration_setting()``.

    Notes
    -----
    There is only one record, with ID ``CalibrationSetting.ID_VALUE``.
    Each field is stored in the section given by
    ``CalibrationSetting.get_section_for_property``. ``update``,
    ``delete`` and ``list`` are not implemented and raise
    ``NotImplementedError``.
    """

    def __init__(self) -> None:
        self.settings = QSettings(
            PathConfig.calibration_setting(), QSettings.IniFormat
        )

    def insert(self, obj: CalibrationSetting) -> int:
        """Write all fields of the record to the INI file.

        Parameters
        ----------
        obj : CalibrationSetting
            The record to save.

        Returns
        -------
        int
            ``CalibrationSetting.ID_VALUE`` on success, or 0 if ``obj``
            is not valid (nothing is written).

        Notes
        -----
        Existing values are overwritten, so this also works as an
        update. The file is synced to disk at the end.
        """
        if not obj.is_valid():
            return 0

        for prop in obj.PROPERTIES:
            if prop in obj.IGNORED_PROPERTIES:
                continue

            value = getattr(obj, prop)
            group_name = obj.get_section_for_property(prop)

            self.settings.beginGroup(group_name)
            self.settings.setValue(prop, value)
            self.settings.endGroup()

        self.settings.sync()
        return CalibrationSetting.ID_VALUE

    def update(self, obj: CalibrationSetting) -> bool:
        """Not implemented.

        Raises
        ------
        NotImplementedError
            Always.
        """
        raise NotImplementedError

    def delete(self, obj_id: int) -> bool:
        """Not implemented.

        Raises
        ------
        NotImplementedError
            Always.
        """
        raise NotImplementedError

    def select(self, obj_id: int) -> Optional[CalibrationSetting]:
        """Read the record from the INI file.

        Parameters
        ----------
        obj_id : int
            Ignored: there is only one record.

        Returns
        -------
        CalibrationSetting | None
            The record read from the file. It is never None: missing or
            blank values become None fields.

        Raises
        ------
        ValueError
            If an ``int`` or ``float`` field holds text that cannot be
            converted.

        Notes
        -----
        Values are converted to ``int`` or ``float`` according to the
        ``CalibrationSetting`` type hints; other fields keep the type
        returned by ``QSettings``.
        """
        import typing

        data = {}
        type_hints = typing.get_type_hints(CalibrationSetting)

        # Instance without __init__ (every field is required), used only
        # to call the section helper.
        temp_obj = CalibrationSetting.__new__(CalibrationSetting)

        for prop in CalibrationSetting.PROPERTIES:
            if prop in CalibrationSetting.IGNORED_PROPERTIES:
                continue

            group_name = temp_obj.get_section_for_property(prop)
            val = self.settings.value(f"{group_name}/{prop}")

            if val is not None and str(val).strip() != "":
                target_type = type_hints.get(prop)
                if target_type == int:
                    data[prop] = int(val)
                elif target_type == float:
                    data[prop] = float(val)
                else:
                    data[prop] = val
            else:
                data[prop] = None

        return CalibrationSetting(**data)

    def list(self) -> List[CalibrationSetting]:
        """Not implemented.

        Raises
        ------
        NotImplementedError
            Always.
        """
        raise NotImplementedError
