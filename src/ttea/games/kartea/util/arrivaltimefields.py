"""Single table of the object arrival times by speed.

The arrival time (seconds between the object appearing on the track
and reaching the front of the car) defines the track speed. Each speed
range (LevelRules.speed, see karteaphaseservice.SPEED_BY_LEVEL) has a
field in the player configuration. From this table are built:

- the key and default value in kartea.ini (KarteaIniDefaults);
- the range of the spin boxes of the edit screen (view);
- the GameSettings.OBJECT_ARRIVAL_TIME used in the game.

The defaults are those of the simulations (6.5 / 3.3 / 2.2 s). The
limits are round numbers close to the simulated ranges (3.3-9.8 /
1.6-4.9 / 1.1-3.3 s), chosen so that the ranges do not overlap: the
minimum of one speed is the maximum of the next (10 | 5 | 3 | 1),
marking the level transition. On the shared boundary,
KarteaArrivalTimeFields.order guarantees GAP seconds of difference, so
advancing a level never makes the track slower or equal.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ArrivalTimeField:
    """One arrival time field of the player configuration.

    Attributes
    ----------
    speed : int
        Speed range (key of GameSettings.OBJECT_ARRIVAL_TIME).
    name : str
        Field of PlayerKarteaConfig (and CSV column).
    levels : str
        Levels that use this speed (documentation only).
    minimum : float
        Lowest accepted value (s).
    default : float
        Default value (s).
    maximum : float
        Highest accepted value (s).
    step : float
        Increment (s) of the spin box. Defaults to 0.1.
    """

    speed: int
    name: str
    levels: str
    minimum: float
    default: float
    maximum: float
    step: float = 0.1

    @property
    def ini_key(self) -> str:
        """Key of the field in kartea.ini (``{name}_default``)."""
        return f"{self.name}_default"

    @property
    def widget_name(self) -> str:
        """Spin box of the field in the edit screen (``spn_{name}``)."""
        return f"spn_{self.name}"

    def clamp(self, value: object) -> float:
        """Convert a value to float and limit it to the field range.

        Parameters
        ----------
        value : object
            Number or text (dot or comma as decimal separator).

        Returns
        -------
        float
            The value limited to [minimum, maximum] and rounded to 2
            decimals, or ``default`` if it is not a number.

        Examples
        --------
        >>> field = KarteaArrivalTimeFields.ALL[0]
        >>> field.clamp("7,25")
        7.25
        >>> field.clamp(20)
        10.0
        >>> field.clamp("abc")
        6.5
        """
        try:
            number = float(str(value).strip().replace(",", "."))
        except (TypeError, ValueError):
            return self.default
        return round(max(self.minimum, min(self.maximum, number)), 2)


class KarteaArrivalTimeFields:
    """Single table of the arrival times by speed.

    Class with only class attributes and class methods, following the
    KarteaPathConfig pattern: it is not instantiated.

    Attributes
    ----------
    ALL : tuple[ArrivalTimeField, ...], class attribute
        Fields in speed order (from the slowest to the fastest).
    GAP : float, class attribute
        Minimum difference (s) between neighboring speeds: the next
        speed must be strictly faster (shorter arrival time).
    """

    ALL: tuple[ArrivalTimeField, ...] = (
        ArrivalTimeField(1, "object_arrival_time_1", "1 a 2", 5.0, 6.5, 10.0),
        ArrivalTimeField(2, "object_arrival_time_2", "3 a 4", 3.0, 3.3, 5.0),
        ArrivalTimeField(3, "object_arrival_time_3", "5 a 7", 1.0, 2.2, 3.0),
    )

    GAP = 0.1

    @classmethod
    def order(cls, values: dict[str, object]) -> dict[str, float]:
        """Return valid arrival times, in decreasing order.

        Each value is limited to its field range (default if missing or
        invalid) and then to the time of the previous speed minus GAP.
        With the table limits this is always possible: the minimum of
        each range is below the minimum of the previous one minus GAP.

        Parameters
        ----------
        values : dict[str, object]
            ``{field name: value}``; missing fields use the default.

        Returns
        -------
        dict[str, float]
            ``{field name: seconds}``, in the order of ALL.

        Examples
        --------
        >>> values = {
        ...     "object_arrival_time_1": 5.0,
        ...     "object_arrival_time_2": 5.0,
        ... }
        >>> times = KarteaArrivalTimeFields.order(values)
        >>> list(times.values())
        [5.0, 4.9, 2.2]
        """
        ordered: dict[str, float] = {}
        previous: float | None = None
        for field in cls.ALL:
            value = field.clamp(values.get(field.name, field.default))
            if previous is not None:
                value = max(
                    field.minimum,
                    min(value, round(previous - cls.GAP, 2)),
                )
            ordered[field.name] = value
            previous = value
        return ordered
