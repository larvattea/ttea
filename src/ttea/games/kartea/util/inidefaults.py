"""Single table of the kartea.ini default values.

Used to create the file (KarteaPathConfig.create_default_ini) and to
build a new configuration from it
(PlayerKarteaConfigService.get_default_config_data). The resource
fields (image/sound) come from KarteaResourceFields and the arrival
times by speed, from KarteaArrivalTimeFields.

Attributes
----------
IniDefault : type
    Type of a table row: (kartea.ini section, key, converter, default
    value as .ini text).
"""

from collections.abc import Callable
from typing import Any

from .arrivaltimefields import KarteaArrivalTimeFields
from .resourcefields import KarteaResourceFields

IniDefault = tuple[str, str, Callable[[Any], Any], str]


class KarteaIniDefaults:
    """Default values of kartea.ini and conversion of the values read.

    Class with only class attributes and class methods, following the
    KarteaPathConfig pattern: it is not instantiated.

    Attributes
    ----------
    TABLE : dict[str, IniDefault], class attribute
        Configuration field -> (section, key, converter, default as
        text). The order defines the order of the sections and keys in
        the generated file.
    """

    @staticmethod
    def to_float(value: Any) -> float:
        """Convert a decimal read from the .ini ("0.5" or "0,5").

        Parameters
        ----------
        value : Any
            Text or number read from the .ini.

        Returns
        -------
        float
            The number, or 0.0 if it is not a number.

        Examples
        --------
        >>> KarteaIniDefaults.to_float("0,5")
        0.5
        """
        try:
            return float(str(value).strip().replace(",", "."))
        except ValueError:
            return 0.0

    @staticmethod
    def to_bool(value: Any) -> bool:
        """Convert a boolean read from the .ini ("true"/"false").

        Parameters
        ----------
        value : Any
            Text or bool read from the .ini.

        Returns
        -------
        bool
            True for "true", "1", "yes" or "sim" (case-insensitive);
            False for any other text. A bool is returned as is.

        Examples
        --------
        >>> KarteaIniDefaults.to_bool(" Sim ")
        True
        """
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in ("true", "1", "yes", "sim")

    # Built with loops (not comprehensions): in the class body, a
    # comprehension cannot see to_float/to_bool.
    TABLE: dict[str, IniDefault] = {
        "phase_id": ("game_settings", "phase_default", int, "1"),
        "level_id": ("game_settings", "level_default", int, "1"),
        "level_time": ("game_settings", "level_time_default", int, "120"),
    }
    for _field in KarteaArrivalTimeFields.ALL:
        TABLE[_field.name] = (
            "game_settings",
            _field.ini_key,
            to_float,
            str(_field.default),
        )
    for _field in KarteaResourceFields.ALL:
        TABLE[_field.name] = (
            _field.ini_section,
            _field.ini_key,
            str,
            _field.default,
        )
    del _field
    TABLE.update(
        {
            "feedback_image_time": (
                "visual_feedback",
                "feedback_image_time_default",
                to_float,
                "0",
            ),
            "palette": ("interface_settings", "palette_default", int, "0"),
            "hud": ("interface_settings", "hud_default", to_bool, "true"),
            "sound": ("interface_settings", "sound_default", to_bool, "true"),
            "feet_marker": (
                "interface_settings",
                "feet_marker_default",
                to_bool,
                "false",
            ),
            "feet_click": (
                "interface_settings",
                "feet_click_default",
                to_bool,
                "false",
            ),
            "feet_click_time": (
                "interface_settings",
                "feet_click_time_default",
                to_float,
                "1.2",
            ),
        }
    )

    @classmethod
    def sections(cls) -> dict[str, dict[str, str]]:
        """Return the content of the default kartea.ini.

        Returns
        -------
        dict[str, dict[str, str]]
            ``{section: {key: default value as text}}``.

        Examples
        --------
        >>> ini = KarteaIniDefaults.sections()
        >>> ini["game_settings"]["level_time_default"]
        '120'
        """
        sections: dict[str, dict[str, str]] = {}
        for section, key, _convert, default in cls.TABLE.values():
            sections.setdefault(section, {})[key] = default
        return sections

    @classmethod
    def value(cls, field: str, ini: dict[str, dict[str, str]]) -> Any:
        """Return the default value of a configuration field.

        Parameters
        ----------
        field : str
            Configuration field (key of TABLE).
        ini : dict[str, dict[str, str]]
            kartea.ini already read (KarteaPathConfig.read_config).

        Returns
        -------
        Any
            The kartea.ini value or, if the key does not exist, the
            table default; converted to the field type.

        Raises
        ------
        KeyError
            If ``field`` is not in TABLE.

        Examples
        --------
        >>> KarteaIniDefaults.value("level_time", {})
        120
        >>> KarteaIniDefaults.value(
        ...     "hud", {"interface_settings": {"hud_default": "false"}}
        ... )
        False
        """
        section, key, convert, default = cls.TABLE[field]
        return convert(ini.get(section, {}).get(key, default))
