"""Single table of the resource fields (image/sound) of the config.

Each row describes a ``PlayerKarteaConfig`` field that points to a
built-in resource. From it are built:

- the folder of the available resources (KarteaPathConfig / service);
- the key and default value in kartea.ini (service);
- the combo box, the preview and the sound button of the edit screen
  (view);
- the matching GameSettings attribute (``name.upper()``);
- the validation of the required fields (edit screen controller).

To add a resource: create the field in the model, a row here, the
``cbx_<field>`` widget in the .ui and the folder in the .qrc.

Besides the built-in resources, each field lists the files the user
places in the KarTEA mods folder, in the subfolder that mirrors the
built-in one (``mod_subdir``), with the extensions in
``mod_extensions``.
"""

from dataclasses import dataclass

from PySide6.QtCore import QT_TRANSLATE_NOOP


@dataclass(frozen=True)
class ResourceField:
    """One resource field of the player configuration.

    Attributes
    ----------
    name : str
        Field name in PlayerKarteaConfig (e.g. "vehicle_image").
    kind : str
        KarteaResourceFields.IMAGE or KarteaResourceFields.SOUND.
    builtin_dir : str
        Folder of the built-in resources (Qt), e.g. ":/images/vehicle".
    ini_section : str
        kartea.ini section of the default value.
    ini_key : str
        kartea.ini key of the default value.
    default : str
        Default value when kartea.ini does not have the key.
    preview_label : str
        Name shown in the edit screen preview (images). Defaults to "".
    feedback : bool
        True for feedback resources (feedback tab and preview). Defaults
        to False.
    play_button : str
        Button that plays the sound on the edit screen (sounds).
        Defaults to "".
    required_message : str
        Message when the field is empty in the form (translation source
        text); empty means an optional field. Fields with the same
        message produce a single error line. Defaults to "".

    Notes
    -----
    ``preview_label`` and ``required_message`` hold pt_BR source texts
    marked with ``QT_TRANSLATE_NOOP`` for pyside6-lupdate; they are
    translated at display time with ``self.tr()`` by the edit screen and
    its controller (i18n).

    Examples
    --------
    >>> field = KarteaResourceFields.get("vehicle_image")
    >>> field.combo_name, field.setting_name
    ('cbx_vehicle_image', 'VEHICLE_IMAGE')
    >>> field.mod_subdir
    'images/vehicle'
    """

    name: str
    kind: str
    builtin_dir: str
    ini_section: str
    ini_key: str
    default: str
    preview_label: str = ""
    feedback: bool = False
    play_button: str = ""
    required_message: str = ""

    @property
    def required(self) -> bool:
        """Whether the field is required (has ``required_message``)."""
        return bool(self.required_message)

    @property
    def combo_name(self) -> str:
        """Name of the field's combo box on the edit screen."""
        return f"cbx_{self.name}"

    @property
    def setting_name(self) -> str:
        """Name of the matching GameSettings attribute."""
        return self.name.upper()

    @property
    def mod_subdir(self) -> str:
        """Subfolder of the field inside the mods folder.

        Mirrors the built-in folder: ":/images/vehicle" ->
        "images/vehicle", ":/sounds/feedback/positive" ->
        "sounds/feedback/positive".
        """
        return self.builtin_dir.removeprefix(":/")

    @property
    def mod_extensions(self) -> tuple[str, ...]:
        """Extensions accepted in the mods folder for this field."""
        return KarteaResourceFields.MOD_EXTENSIONS[self.kind]


class KarteaResourceFields:
    """Single table of the resource fields (image/sound) of the config.

    Class with only class attributes and class methods, following the
    KarteaPathConfig pattern: it is not instantiated.

    Attributes
    ----------
    IMAGE : str, class attribute
        Image resource type ("image", ResourceField.kind).
    SOUND : str, class attribute
        Sound resource type ("sound", ResourceField.kind).
    MOD_EXTENSIONS : dict[str, tuple[str, ...]], class attribute
        Extensions accepted in the mods folder, by type (lowercase).
        Sounds only in WAV.
    ALL : tuple[ResourceField, ...], class attribute
        All fields, in the edit screen order.
    BY_NAME : dict[str, ResourceField], class attribute
        Fields by name.

    Notes
    -----
    The preview names and required-field messages of ALL are marked with
    ``QT_TRANSLATE_NOOP`` in the ``_TR_VIEW_CONTEXT``
    ("PlayerKarteaConfigEditView") and ``_TR_CONTEXT``
    ("PlayerKarteaConfigEditController") contexts; they are translated
    with ``self.tr()`` where they are shown (i18n).
    """

    IMAGE = "image"
    SOUND = "sound"

    # Sounds only in WAV: the format that plays both in the game
    # (pygame) and in the listen button of the config screen
    # (QSoundEffect).
    MOD_EXTENSIONS: dict[str, tuple[str, ...]] = {
        IMAGE: (".png", ".jpg", ".jpeg", ".bmp"),
        SOUND: (".wav",),
    }

    # Translation context of the required-field messages: they are
    # shown by the edit screen controller, with self.tr(). The
    # QT_TRANSLATE_NOOP calls below repeat these contexts as literals
    # because pyside6-lupdate only extracts texts whose context is a
    # string literal.
    _TR_CONTEXT = "PlayerKarteaConfigEditController"

    # Translation context of the preview names: they are shown by the
    # edit screen, with self.tr().
    _TR_VIEW_CONTEXT = "PlayerKarteaConfigEditView"

    @staticmethod
    def _image(
        name,
        folder,
        section,
        key,
        default,
        label,
        feedback=False,
        required_message="",
        kind=IMAGE,  # default evaluated in the class body
    ) -> ResourceField:
        """Build an image field (used only to fill ALL)."""
        return ResourceField(
            name,
            kind,
            f":/images/{folder}",
            section,
            key,
            default,
            preview_label=label,
            feedback=feedback,
            required_message=required_message,
        )

    @staticmethod
    def _feedback_sound(tone, default, kind=SOUND) -> ResourceField:
        """Build a feedback sound field (used only to fill ALL)."""
        return ResourceField(
            f"{tone}_feedback_sound",
            kind,
            f":/sounds/feedback/{tone}",
            "sound_feedback",
            f"{tone}_feedback_sound_default",
            default,
            feedback=True,
            play_button=f"pb_{tone}_sound",
        )

    _ENVIRONMENT_REQUIRED = QT_TRANSLATE_NOOP(
        "PlayerKarteaConfigEditController",
        "Imagem do ambiente é obrigatória!\n",
    )

    # fmt: off
    ALL: tuple[ResourceField, ...] = (
        _image("horizon_image", "horizon", "visual_resources",
               "horizon_image_default", "horizon",
               QT_TRANSLATE_NOOP("PlayerKarteaConfigEditView", "Horizonte"),
               required_message=QT_TRANSLATE_NOOP(
                   "PlayerKarteaConfigEditController",
                   "Imagem do horizonte é obrigatória!\n")),
        _image("vehicle_image", "vehicle", "visual_resources",
               "vehicle_image_default", "defaultvehicle",
               QT_TRANSLATE_NOOP("PlayerKarteaConfigEditView", "Veículo"),
               required_message=QT_TRANSLATE_NOOP(
                   "PlayerKarteaConfigEditController",
                   "Imagem do veículo é obrigatória!\n")),
        _image("environment_image_right", "environment", "visual_resources",
               "environment_image_default_right", "right",
               QT_TRANSLATE_NOOP("PlayerKarteaConfigEditView", "Ambiente"),
               required_message=_ENVIRONMENT_REQUIRED),
        _image("environment_image_left", "environment", "visual_resources",
               "environment_image_default_left", "left",
               QT_TRANSLATE_NOOP("PlayerKarteaConfigEditView", "Ambiente"),
               required_message=_ENVIRONMENT_REQUIRED),
        _image("target_image", "target", "visual_resources",
               "target_image_default", "defaultstar",
               QT_TRANSLATE_NOOP("PlayerKarteaConfigEditView", "Alvo"),
               required_message=QT_TRANSLATE_NOOP(
                   "PlayerKarteaConfigEditController",
                   "Imagem do alvo é obrigatória!\n")),
        _image("obstacle_image", "obstacle", "visual_resources",
               "obstacle_image_default", "defaultobstacle",
               QT_TRANSLATE_NOOP("PlayerKarteaConfigEditView", "Obstáculo"),
               required_message=QT_TRANSLATE_NOOP(
                   "PlayerKarteaConfigEditController",
                   "Imagem do obstáculo é obrigatória!\n")),
        _image("positive_feedback_image", "feedback/positive",
               "visual_feedback",
               "positive_feedback_image_default", "positive",
               QT_TRANSLATE_NOOP("PlayerKarteaConfigEditView",
                                 "Positivo"), True),
        _image("neutral_feedback_image", "feedback/neutral", "visual_feedback",
               "neutral_feedback_image_default", "neutral",
               QT_TRANSLATE_NOOP("PlayerKarteaConfigEditView",
                                 "Neutro"), True),
        _image("negative_feedback_image", "feedback/negative",
               "visual_feedback",
               "negative_feedback_image_default", "negative",
               QT_TRANSLATE_NOOP("PlayerKarteaConfigEditView",
                                 "Negativo"), True),
        _feedback_sound("positive", "point"),
        _feedback_sound("neutral", "miss"),
        _feedback_sound("negative", "miss"),
    )
    # fmt: on

    BY_NAME: dict[str, ResourceField] = {field.name: field for field in ALL}

    @classmethod
    def get(cls, name: str) -> ResourceField:
        """Return the field with the given name.

        Parameters
        ----------
        name : str
            Field name, e.g. "vehicle_image".

        Returns
        -------
        ResourceField
            The field.

        Raises
        ------
        KeyError
            If there is no field with this name.
        """
        return cls.BY_NAME[name]

    @classmethod
    def images(cls) -> tuple[ResourceField, ...]:
        """Return the image fields, in table order.

        Returns
        -------
        tuple[ResourceField, ...]
            Fields whose kind is IMAGE.

        Examples
        --------
        >>> len(KarteaResourceFields.images())
        9
        """
        return tuple(field for field in cls.ALL if field.kind == cls.IMAGE)

    @classmethod
    def sounds(cls) -> tuple[ResourceField, ...]:
        """Return the sound fields, in table order.

        Returns
        -------
        tuple[ResourceField, ...]
            Fields whose kind is SOUND.

        Examples
        --------
        >>> KarteaResourceFields.sounds()[0].name
        'positive_feedback_sound'
        """
        return tuple(field for field in cls.ALL if field.kind == cls.SOUND)
