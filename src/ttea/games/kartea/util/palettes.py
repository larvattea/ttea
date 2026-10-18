"""Single table of the KarTEA track color palettes.

Each palette defines the colors of the grass, the side strip
(rumble), the road and the finish line, always in two tones
(``"dark"`` and ``"light"``) that alternate every 3 segments to give
the feeling of movement.

From it are built:

- the game theme (``KarTEATheme``), which converts the colors to
  ``pygame.Color``;
- the ``cbx_palette`` combo box of the edit screen (translated name
  and description in the tooltip).

Only the palette number (key of KarteaPalettes.ALL) is saved in the
player configuration (CSV), never the name: this way the
configuration does not depend on the screen language. A number that
does not exist here falls back to ``KarteaPalettes.DEFAULT``.

To add a palette: create a new entry in ``_PALETTES`` with the next
free number. Do not reuse or renumber numbers already used, since
they are saved in the players' configurations.

This module does not import pygame, so it can be used by the Qt
screen.

Attributes
----------
RGB : type
    Type of a color: ``tuple[int, int, int]``.
"""

from dataclasses import dataclass
from types import MappingProxyType

from PySide6.QtCore import QT_TRANSLATE_NOOP

RGB = tuple[int, int, int]


@dataclass(frozen=True)
class Palette:
    """One color palette of the track.

    Attributes
    ----------
    name : str
        Name shown on the edit screen (translation source text).
    description : str
        What the palette is for (tooltip on the edit screen).
    finish : dict[str, RGB]
        ``{"dark": (r, g, b), "light": (r, g, b)}`` colors of the finish
        line.
    grass : dict[str, RGB]
        Dark and light colors of the grass.
    rumble : dict[str, RGB]
        Dark and light colors of the side strip.
    road : dict[str, RGB]
        Dark and light colors of the road.

    Notes
    -----
    ``name`` and ``description`` hold the pt_BR source text marked with
    ``QT_TRANSLATE_NOOP`` (context "PlayerKarteaConfigEditView") for
    pyside6-lupdate; the edit screen translates them at display time
    with ``self.tr()`` (i18n).
    """

    name: str
    description: str
    finish: dict[str, RGB]
    grass: dict[str, RGB]
    rumble: dict[str, RGB]
    road: dict[str, RGB]


class KarteaPalettes:
    """Single table of the track color palettes.

    Class with only class attributes and class methods, following the
    KarteaPathConfig pattern: it is not instantiated.

    Attributes
    ----------
    DEFAULT : int, class attribute
        Number of the palette used when the value is empty or invalid
        (0, "Padrão").
    ALL : Mapping[int, Palette], class attribute
        Read-only ``{number: Palette}``, in increasing number order.
    _PALETTES : dict[int, Palette], class attribute
        Source table of ALL; where new palettes are added.

    Notes
    -----
    The palette names and descriptions are marked for translation with
    ``QT_TRANSLATE_NOOP`` in the ``_TR_VIEW_CONTEXT`` context
    ("PlayerKarteaConfigEditView"); the edit screen translates them with
    ``self.tr()`` (i18n).
    """

    # Translation context of the names and descriptions: they are shown
    # by the edit screen, with self.tr(). The QT_TRANSLATE_NOOP calls
    # below repeat it as a literal because pyside6-lupdate only extracts
    # texts whose context is a string literal.
    _TR_VIEW_CONTEXT = "PlayerKarteaConfigEditView"

    DEFAULT = 0

    _PALETTES: dict[int, Palette] = {
        0: Palette(
            name=QT_TRANSLATE_NOOP("PlayerKarteaConfigEditView", "Padrão"),
            description=QT_TRANSLATE_NOOP(
                "PlayerKarteaConfigEditView", "Cores originais do jogo"
            ),
            finish={"dark": (0, 0, 0), "light": (255, 255, 255)},
            grass={"dark": (0, 154, 0), "light": (16, 200, 16)},
            rumble={"dark": (255, 0, 0), "light": (255, 255, 255)},
            road={"dark": (75, 75, 75), "light": (107, 107, 107)},
        ),
        1: Palette(
            name=QT_TRANSLATE_NOOP("PlayerKarteaConfigEditView", "Suave"),
            description=QT_TRANSLATE_NOOP(
                "PlayerKarteaConfigEditView",
                "Baixo estímulo sensorial: cores dessaturadas e pouca "
                "diferença entre as faixas",
            ),
            finish={"dark": (90, 90, 90), "light": (190, 190, 185)},
            grass={"dark": (118, 150, 118), "light": (128, 160, 128)},
            rumble={"dark": (190, 175, 160), "light": (205, 195, 180)},
            road={"dark": (100, 100, 105), "light": (110, 110, 115)},
        ),
        2: Palette(
            name=QT_TRANSLATE_NOOP(
                "PlayerKarteaConfigEditView", "Alto contraste"
            ),
            description=QT_TRANSLATE_NOOP(
                "PlayerKarteaConfigEditView",
                "Baixa visão: pista escura com borda amarela e preta",
            ),
            finish={"dark": (0, 0, 0), "light": (255, 255, 255)},
            grass={"dark": (0, 80, 0), "light": (0, 100, 0)},
            rumble={"dark": (20, 20, 20), "light": (255, 215, 0)},
            road={"dark": (35, 35, 35), "light": (50, 50, 50)},
        ),
        3: Palette(
            name=QT_TRANSLATE_NOOP("PlayerKarteaConfigEditView", "Daltonismo"),
            description=QT_TRANSLATE_NOOP(
                "PlayerKarteaConfigEditView",
                "Protanopia e deuteranopia: azul e laranja no lugar de "
                "vermelho e verde",
            ),
            finish={"dark": (0, 0, 0), "light": (255, 255, 255)},
            grass={"dark": (0, 130, 95), "light": (0, 158, 115)},
            rumble={"dark": (0, 114, 178), "light": (230, 159, 0)},
            road={"dark": (80, 80, 80), "light": (110, 110, 110)},
        ),
        4: Palette(
            name=QT_TRANSLATE_NOOP("PlayerKarteaConfigEditView", "Noturno"),
            description=QT_TRANSLATE_NOOP(
                "PlayerKarteaConfigEditView",
                "Pouco brilho, para ambientes escuros ou sensibilidade à luz",
            ),
            finish={"dark": (20, 20, 25), "light": (200, 200, 210)},
            grass={"dark": (12, 45, 30), "light": (18, 60, 40)},
            rumble={"dark": (40, 40, 55), "light": (170, 170, 90)},
            road={"dark": (30, 30, 40), "light": (42, 42, 55)},
        ),
        5: Palette(
            name=QT_TRANSLATE_NOOP("PlayerKarteaConfigEditView", "Deserto"),
            description=QT_TRANSLATE_NOOP(
                "PlayerKarteaConfigEditView", "Temática: areia e tons terrosos"
            ),
            finish={"dark": (60, 40, 25), "light": (245, 235, 215)},
            grass={"dark": (205, 170, 110), "light": (222, 190, 130)},
            rumble={"dark": (180, 75, 40), "light": (240, 228, 205)},
            road={"dark": (110, 95, 80), "light": (128, 112, 96)},
        ),
        6: Palette(
            name=QT_TRANSLATE_NOOP("PlayerKarteaConfigEditView", "Neve"),
            description=QT_TRANSLATE_NOOP(
                "PlayerKarteaConfigEditView", "Temática: neve e tons frios"
            ),
            finish={"dark": (0, 0, 0), "light": (255, 255, 255)},
            grass={"dark": (215, 228, 235), "light": (238, 245, 250)},
            rumble={"dark": (30, 90, 170), "light": (190, 210, 230)},
            road={"dark": (85, 90, 100), "light": (100, 106, 118)},
        ),
        7: Palette(
            name=QT_TRANSLATE_NOOP("PlayerKarteaConfigEditView", "Outono"),
            description=QT_TRANSLATE_NOOP(
                "PlayerKarteaConfigEditView",
                "Temática: tons quentes de outono",
            ),
            finish={"dark": (50, 30, 20), "light": (245, 230, 200)},
            grass={"dark": (150, 85, 30), "light": (175, 105, 40)},
            rumble={"dark": (120, 40, 30), "light": (235, 200, 120)},
            road={"dark": (85, 75, 70), "light": (102, 92, 86)},
        ),
        8: Palette(
            name=QT_TRANSLATE_NOOP("PlayerKarteaConfigEditView", "Tritanopia"),
            description=QT_TRANSLATE_NOOP(
                "PlayerKarteaConfigEditView",
                "Tritanopia (confusão entre azul e amarelo): vermelho e "
                "ciano",
            ),
            finish={"dark": (0, 0, 0), "light": (255, 255, 255)},
            grass={"dark": (40, 120, 90), "light": (55, 140, 105)},
            rumble={"dark": (210, 40, 60), "light": (120, 220, 230)},
            road={"dark": (80, 80, 80), "light": (105, 105, 105)},
        ),
        9: Palette(
            name=QT_TRANSLATE_NOOP(
                "PlayerKarteaConfigEditView", "Monocromático"
            ),
            description=QT_TRANSLATE_NOOP(
                "PlayerKarteaConfigEditView",
                "Somente tons de cinza, sem estímulo de cor",
            ),
            finish={"dark": (0, 0, 0), "light": (255, 255, 255)},
            grass={"dark": (150, 150, 150), "light": (165, 165, 165)},
            rumble={"dark": (70, 70, 70), "light": (210, 210, 210)},
            road={"dark": (90, 90, 90), "light": (102, 102, 102)},
        ),
        10: Palette(
            name=QT_TRANSLATE_NOOP("PlayerKarteaConfigEditView", "Pastel"),
            description=QT_TRANSLATE_NOOP(
                "PlayerKarteaConfigEditView",
                "Cores claras e suaves, entre a Suave e a Padrão",
            ),
            finish={"dark": (110, 110, 120), "light": (250, 250, 250)},
            grass={"dark": (170, 220, 170), "light": (185, 232, 185)},
            rumble={"dark": (240, 170, 180), "light": (250, 245, 240)},
            road={"dark": (150, 150, 160), "light": (165, 165, 175)},
        ),
    }

    ALL = MappingProxyType(dict(sorted(_PALETTES.items())))

    @classmethod
    def id_of(cls, value) -> int:
        """Return a valid palette number from any value.

        Parameters
        ----------
        value : Any
            Int or text (as it comes from the CSV or kartea.ini).

        Returns
        -------
        int
            The palette number; empty, invalid or unknown values become
            ``DEFAULT``.

        Examples
        --------
        >>> KarteaPalettes.id_of("3")
        3
        >>> KarteaPalettes.id_of("99"), KarteaPalettes.id_of(None)
        (0, 0)
        """
        try:
            number = int(value)
        except (TypeError, ValueError):
            return cls.DEFAULT
        return number if number in cls.ALL else cls.DEFAULT

    @classmethod
    def get(cls, value) -> Palette:
        """Return the palette matching ``value`` (see ``id_of``).

        Parameters
        ----------
        value : Any
            Int or text palette number.

        Returns
        -------
        Palette
            The palette, or the DEFAULT one for invalid values.

        Examples
        --------
        >>> KarteaPalettes.get("1").name
        'Suave'
        """
        return cls.ALL[cls.id_of(value)]
