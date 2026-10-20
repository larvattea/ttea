"""Application path configuration for T-TEA.

Handles data directories in both development and frozen
(PyInstaller) environments. Also provides Qt resource path helpers
and user file path constructors.
"""

import sys
from pathlib import Path
from typing import List

from platformdirs import user_data_dir
from PySide6.QtCore import QDir, QDirIterator


class PathConfig:
    """Centralized application path settings.

    This class exposes directory constants and helper methods for
    configuration, calibration, logs, exports, and Qt resources.

    Attributes
    ----------
    APP_NAME : str, class attribute
        Application name used for platform-specific data directories.
    APP_AUTHOR : str, class attribute
        Application author name used for platform-specific data
        directories.
    CONFIG_FILENAME : str, class attribute
        Default file name for configuration files.
    CALIBRATION_HARDWARE_FILENAME : str, class attribute
        Default file name for calibration hardware settings.
    CALIBRATION_SETTING_FILENAME : str, class attribute
        Default file name for calibration settings.
    CALIBRATION_POINT_FILENAME : str, class attribute
        Default file name for calibration point CSV data.
    HELP_BASENAME : str, class attribute
        Base name of the compiled help files
        (``ttea_<language>.qch``).
    PROJECT_DIR : Path, class attribute
        Repository root. Defined only in development mode.
    BASE_DIR : Path, class attribute
        Base application data directory: ``<project>/data`` in
        development, the platform user data folder when frozen.
    EXERGAME_DIR : Path, class attribute
        Base directory for exergame save data:
        ``<project>/src/ttea/games`` in development,
        ``BASE_DIR / "exergames"`` when frozen.
    RESOURCES_ROOT : Path, class attribute
        Installed resources: ``<project>/resources`` in development,
        ``resources`` inside the PyInstaller bundle when frozen.
    CONFIG_DIR : Path, class attribute
        Directory for configuration files.
    CALIBRATION_DIR : Path, class attribute
        Directory for calibration files.
    EXPORTS_DIR : Path, class attribute
        Directory for exported files.
    INSTITUTIONFACILITY_DIR : Path, class attribute
        Directory for institution facility data.
    LOG_DIR : Path, class attribute
        Directory for log files.
    MODELS_DIR : Path, class attribute
        Directory containing the bundled MediaPipe models.
    HELP_ROOT : Path, class attribute
        Directory containing the compiled help files (.qch), one per
        language. Read-only in installed builds.
    HELP_CACHE_DIR : Path, class attribute
        Writable directory for the help collections and search
        index.
    PLAYERS_DIR : Path, class attribute
        Directory for player files.
    PROFESSIONAL_DIR : Path, class attribute
        Directory for professional files.

    Methods
    -------
    resource(path='')
        Build a Qt resource path.
    icon_system(name)
        Return a Qt system icon resource path.
    icon_ui_button(name)
        Return a Qt UI button icon resource path.
    icon_ui_menu(name)
        Return a Qt UI menu icon resource path.
    flag(name)
        Return a Qt flag resource path.
    image(name)
        Return a Qt image resource path.
    ui(name)
        Return a Qt UI resource path.
    translation(name)
        Return a Qt translation resource path.
    sounds(name)
        Return a Qt sound resource path.
    ensure_dirs()
        Create all user directories.
    config(filename=CONFIG_FILENAME)
        Return application config file path.
    calibration_hardware(filename=CALIBRATION_HARDWARE_FILENAME)
        Return calibration hardware file path.
    calibration_setting(filename=CALIBRATION_SETTING_FILENAME)
        Return calibration setting file path.
    calibration_point(filename=CALIBRATION_POINT_FILENAME)
        Return calibration point CSV file path.
    professional(filename)
        Return professional data file path.
    institutionfacility(filename)
        Return institution facility data file path.
    player(filename)
        Return player data file path.
    model(filename)
        Return Mediapipe model file path.
    export(filename)
        Return export file path.
    log(filename)
        Return log file path.
    help_file(language)
        Return the compiled help file of a language.
    help_collection(language)
        Return the help collection file of a language.
    game_save(game_name, filename)
        Return game save file path.
    set_base_dir(path)
        Set a different base directory for tests.
    config_file_exists(filename=CONFIG_FILENAME)
        Check if configuration file exists.
    calibration_file_exists(filename=CALIBRATION_HARDWARE_FILENAME)
        Check if calibration file exists.
    find_resource_built_in(base_path, name)
        Find an embedded Qt resource from a base path.

    Notes
    -----
    Every class attribute whose name ends in ``_DIR`` is treated as a
    user directory: ``ensure_dirs`` creates it and ``set_base_dir``
    moves it. That includes ``MODELS_DIR`` and, in development,
    ``PROJECT_DIR``; ``HELP_ROOT`` and ``RESOURCES_ROOT`` are
    deliberately named otherwise.

    Examples
    --------
    >>> PathConfig.resource('images/logo.png')
    ':/images/logo.png'
    >>> PathConfig.help_file('en_US').name
    'ttea_en_US.qch'
    """

    APP_NAME = "ttea"
    APP_AUTHOR = "udesc"

    CONFIG_FILENAME = "config.ini"
    CALIBRATION_HARDWARE_FILENAME = "calibration_hardware.ini"
    CALIBRATION_SETTING_FILENAME = "calibration_setting.ini"
    CALIBRATION_POINT_FILENAME = "calibration_point.csv"
    HELP_BASENAME = "ttea"

    # ==================================================================
    # Base directory
    # ==================================================================
    if getattr(sys, "frozen", False):
        BASE_DIR: Path = Path(user_data_dir(APP_NAME, APP_AUTHOR))
        EXERGAME_DIR: Path = BASE_DIR / "exergames"
        RESOURCES_ROOT: Path = (
            Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
            / "resources"
        )
    else:
        PROJECT_DIR: Path = Path(__file__).resolve().parents[3]
        EXERGAME_DIR: Path = PROJECT_DIR / "src" / "ttea" / "games"
        BASE_DIR: Path = PROJECT_DIR / "data"
        RESOURCES_ROOT: Path = PROJECT_DIR / "resources"

    MODELS_DIR: Path = RESOURCES_ROOT / "mediapipemodels"
    # Not named *_DIR: it is part of the installed resources, not a
    # user folder created by ensure_dirs().
    HELP_ROOT: Path = RESOURCES_ROOT / "help"

    # Subdirectories — add new folders here
    CONFIG_DIR: Path = BASE_DIR / "config"
    CALIBRATION_DIR: Path = BASE_DIR / "calibration"
    EXPORTS_DIR: Path = BASE_DIR / "exports"
    HELP_CACHE_DIR: Path = BASE_DIR / "helpcache"
    INSTITUTIONFACILITY_DIR: Path = BASE_DIR / "institutionfacilities"
    LOG_DIR: Path = BASE_DIR / "log"
    PLAYERS_DIR: Path = BASE_DIR / "players"
    PROFESSIONAL_DIR: Path = BASE_DIR / "professionals"

    # ==================================================================
    # Built-in Resources (Qt)
    # ==================================================================
    @staticmethod
    def resource(path: str = "") -> str:
        """Return a Qt resource path.

        Parameters
        ----------
        path : str, optional
            Resource path segment. Default is empty string.

        Returns
        -------
        str
            Qt resource path starting with ``:/``.

        Notes
        -----
        Trailing slashes are removed from the generated resource path,
        so an empty ``path`` gives ``":"``.

        Examples
        --------
        >>> PathConfig.resource('images/logo.png')
        ':/images/logo.png'
        >>> PathConfig.resource()
        ':'
        """
        return f":/{path}".rstrip("/")

    @staticmethod
    def icon_system(name: str) -> str:
        """Return a Qt resource path for a system icon.

        Parameters
        ----------
        name : str
            Icon file name.

        Returns
        -------
        str
            Qt path for the system icon.
        """
        return f":/icons/system/{name}"

    @staticmethod
    def icon_ui_button(name: str) -> str:
        """Return a Qt resource path for a UI button icon.

        Parameters
        ----------
        name : str
            Button icon file name.

        Returns
        -------
        str
            Qt path for the UI button icon.
        """
        return f":/icons/ui/buttons/{name}"

    @staticmethod
    def icon_ui_menu(name: str) -> str:
        """Return a Qt resource path for a UI menu icon.

        Parameters
        ----------
        name : str
            Menu icon file name.

        Returns
        -------
        str
            Qt path for the UI menu icon.
        """
        return f":/icons/ui/menu/{name}"

    @staticmethod
    def flag(name: str) -> str:
        """Return a Qt resource path for a flag image.

        Parameters
        ----------
        name : str
            Flag file name.

        Returns
        -------
        str
            Qt path for the flag resource.
        """
        return f":/flags/{name}"

    @staticmethod
    def image(name: str) -> str:
        """Return a Qt resource path for an image.

        Parameters
        ----------
        name : str
            Image file name.

        Returns
        -------
        str
            Qt path for the image resource.
        """
        return f":/images/{name}"

    @staticmethod
    def ui(name: str) -> str:
        """Return a Qt resource path for a UI file.

        Parameters
        ----------
        name : str
            UI file name.

        Returns
        -------
        str
            Qt path for the UI resource.
        """
        return f":/ui/{name}"

    @staticmethod
    def translation(name: str) -> str:
        """Return a Qt resource path for a translation file.

        Parameters
        ----------
        name : str
            Translation file name.

        Returns
        -------
        str
            Qt path for the translation resource.
        """
        return f":/translations/{name}"

    @staticmethod
    def sounds(name: str) -> str:
        """Return a Qt resource path for a sound file.

        Parameters
        ----------
        name : str
            Sound file name.

        Returns
        -------
        str
            Qt path for the sound resource.
        """
        return f":/sounds/{name}"

    # ==================================================================
    # Automatic Introspection
    # ==================================================================
    @classmethod
    def _get_dir_names(cls) -> List[str]:
        """Return class attribute names that end with ``_DIR``.

        Returns
        -------
        list[str]
            Names of the public ``*_DIR`` class attributes, in
            definition order.
        """
        return [
            name
            for name in vars(cls)
            if name.endswith("_DIR") and not name.startswith("_")
        ]

    @classmethod
    def _get_user_dirs(cls) -> List[Path]:
        """Return Path objects for all user directories.

        Returns
        -------
        list[Path]
            Path objects for each ``_DIR`` class attribute.
        """
        return [
            value
            for name, value in vars(cls).items()
            if name.endswith("_DIR") and not name.startswith("_")
        ]

    # ==================================================================
    # User data methods
    # ==================================================================
    @classmethod
    def ensure_dirs(cls) -> None:
        """Create all configured directories if they do not exist.

        Notes
        -----
        Creates every directory of ``_get_user_dirs`` with its parents.
        """
        for directory in cls._get_user_dirs():
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def _user_file(cls, directory: Path, filename: str) -> str:
        """Return the full file path for a given user directory.

        Calls ``ensure_dirs`` first, so all user directories exist.

        Parameters
        ----------
        directory : Path
            Target directory.
        filename : str
            File name to append to the directory.

        Returns
        -------
        str
            Full path to the user file.
        """
        cls.ensure_dirs()
        return str(directory / filename)

    @classmethod
    def config(cls, filename: str = CONFIG_FILENAME) -> str:
        """Return the configuration file path.

        Parameters
        ----------
        filename : str, optional
            Name of the configuration file. Default is
            ``CONFIG_FILENAME``.

        Returns
        -------
        str
            Full path to the configuration file.

        Notes
        -----
        Creates the user directories if needed (see ``_user_file``).
        """
        return cls._user_file(cls.CONFIG_DIR, filename)

    @classmethod
    def calibration_hardware(
        cls, filename: str = CALIBRATION_HARDWARE_FILENAME
    ) -> str:
        """Return the calibration hardware file path.

        Parameters
        ----------
        filename : str, optional
            Name of the calibration hardware file. Default is
            ``CALIBRATION_HARDWARE_FILENAME``.

        Returns
        -------
        str
            Full path to the calibration hardware file.
        """
        return cls._user_file(cls.CALIBRATION_DIR, filename)

    @classmethod
    def calibration_setting(
        cls, filename: str = CALIBRATION_SETTING_FILENAME
    ) -> str:
        """Return the calibration setting file path.

        Parameters
        ----------
        filename : str, optional
            Name of the calibration setting file. Default is
            ``CALIBRATION_SETTING_FILENAME``.

        Returns
        -------
        str
            Full path to the calibration setting file.
        """
        return cls._user_file(cls.CALIBRATION_DIR, filename)

    @classmethod
    def calibration_point(
        cls, filename: str = CALIBRATION_POINT_FILENAME
    ) -> str:
        """Return the calibration point CSV file path.

        Parameters
        ----------
        filename : str, optional
            Name of the calibration point CSV file. Default is
            ``CALIBRATION_POINT_FILENAME``.

        Returns
        -------
        str
            Full path to the calibration point CSV file.
        """
        return cls._user_file(cls.CALIBRATION_DIR, filename)

    @classmethod
    def professional(cls, filename: str) -> str:
        """Return the professional data file path.

        Parameters
        ----------
        filename : str
            Name of the professional file.

        Returns
        -------
        str
            Full path to the professional file.
        """
        return cls._user_file(cls.PROFESSIONAL_DIR, filename)

    @classmethod
    def institutionfacility(cls, filename: str) -> str:
        """Return the institution facility data file path.

        Parameters
        ----------
        filename : str
            Name of the institution facility file.

        Returns
        -------
        str
            Full path to the institution facility file.
        """
        return cls._user_file(cls.INSTITUTIONFACILITY_DIR, filename)

    @classmethod
    def player(cls, filename: str) -> str:
        """Return the player data file path.

        Parameters
        ----------
        filename : str
            Name of the player file.

        Returns
        -------
        str
            Full path to the player file.
        """
        return cls._user_file(cls.PLAYERS_DIR, filename)

    @classmethod
    def model(cls, filename: str) -> str:
        """Return the MediaPipe model file path.

        Parameters
        ----------
        filename : str
            Name of the model file.

        Returns
        -------
        str
            Full path to the model file.
        """
        return str(cls.MODELS_DIR / filename)

    @classmethod
    def export(cls, filename: str) -> str:
        """Return the export file path.

        Parameters
        ----------
        filename : str
            Name of the export file.

        Returns
        -------
        str
            Full path to the export file.
        """
        return cls._user_file(cls.EXPORTS_DIR, filename)

    @classmethod
    def log(cls, filename: str) -> str:
        """Return the log file path.

        Parameters
        ----------
        filename : str
            Name of the log file.

        Returns
        -------
        str
            Full path to the log file.
        """
        return cls._user_file(cls.LOG_DIR, filename)

    @classmethod
    def help_file(cls, language: str) -> Path:
        """Return the compiled help file of a language.

        Parameters
        ----------
        language : str
            Language code, e.g. ``"pt_BR"``.

        Returns
        -------
        Path
            Path of ``ttea_<language>.qch``. The file may not exist.

        Examples
        --------
        >>> PathConfig.help_file('en_US').name
        'ttea_en_US.qch'
        """
        return cls.HELP_ROOT / f"{cls.HELP_BASENAME}_{language}.qch"

    @classmethod
    def help_collection(cls, language: str) -> str:
        """Return the help collection file of a language.

        The collection and the search index are created on first use,
        in a writable user folder.

        Parameters
        ----------
        language : str
            Language code, e.g. ``"pt_BR"``.

        Returns
        -------
        str
            Full path of ``ttea_<language>.qhc``.
        """
        return cls._user_file(
            cls.HELP_CACHE_DIR, f"{cls.HELP_BASENAME}_{language}.qhc"
        )

    @classmethod
    def game_save(cls, game_name: str, filename: str) -> str:
        """Return the game save file path.

        Parameters
        ----------
        game_name : str
            Identifier for the game save directory.
        filename : str
            Name of the save file.

        Returns
        -------
        str
            Full path to the game save file.

        Notes
        -----
        Creates the user directories and ``EXERGAME_DIR / game_name``
        if needed.
        """
        cls.ensure_dirs()
        game_dir = cls.EXERGAME_DIR / game_name
        game_dir.mkdir(exist_ok=True)
        return str(game_dir / filename)

    # ==================================================================
    # Test support
    # ==================================================================
    @classmethod
    def set_base_dir(cls, path: str | Path) -> None:
        """Set a different base directory, primarily for tests.

        Parameters
        ----------
        path : str | Path
            New base directory path; it is resolved to an absolute path.

        Notes
        -----
        ``BASE_DIR`` becomes the new base and ``EXERGAME_DIR`` its
        ``exergames`` subfolder. Every other ``*_DIR`` attribute becomes
        ``<base>/<name>``, where ``name`` is the attribute name without
        ``_DIR`` in lower case. These names do not always match the
        defaults (``help_cache``, ``institutionfacility``,
        ``professional``), and ``MODELS_DIR`` and ``PROJECT_DIR`` are
        moved too. Directories are not created here.

        Examples
        --------
        >>> PathConfig.set_base_dir('tests_data')
        >>> PathConfig.HELP_CACHE_DIR.name
        'help_cache'
        """
        new_base = Path(path).resolve()

        cls.BASE_DIR = new_base
        cls.EXERGAME_DIR = new_base / "exergames"

        for dir_name in cls._get_dir_names():
            if dir_name in ("BASE_DIR", "EXERGAME_DIR"):
                continue
            subdir = dir_name.replace("_DIR", "").lower()
            setattr(cls, dir_name, new_base / subdir)

    # ==================================================================
    # Checks
    # ==================================================================
    @classmethod
    def config_file_exists(cls, filename: str = CONFIG_FILENAME) -> bool:
        """Return whether the configuration file exists.

        Parameters
        ----------
        filename : str, optional
            Name of the configuration file. Default is
            ``CONFIG_FILENAME``.

        Returns
        -------
        bool
            True if the configuration file exists, otherwise False.

        Notes
        -----
        Creates the user directories if needed (see ``config``).
        """
        return Path(cls.config(filename)).exists()

    @classmethod
    def calibration_file_exists(
        cls, filename: str = CALIBRATION_HARDWARE_FILENAME
    ) -> bool:
        """Return whether the calibration file exists.

        Parameters
        ----------
        filename : str, optional
            Name of the calibration file. Default is
            ``CALIBRATION_HARDWARE_FILENAME``.

        Returns
        -------
        bool
            True if the calibration file exists, otherwise False.

        Notes
        -----
        Looks in ``CALIBRATION_DIR`` and creates the user directories if
        needed.
        """
        return Path(cls.calibration_hardware(filename)).exists()

    # ==================================================================
    # Utilities
    # ==================================================================
    @classmethod
    def find_resource_built_in(cls, base_path: str, name: str) -> str:
        """Find an embedded Qt resource from a base path.

        Parameters
        ----------
        base_path : str
            Base resource path to search in.
        name : str
            File name to locate.

        Returns
        -------
        str
            Full resource path of the first match, otherwise an empty
            string.

        Notes
        -----
        Searches ``base_path`` and its subdirectories for a file whose
        name matches ``name`` (a ``QDir`` name filter, so wildcards
        work).
        """
        it = QDirIterator(
            base_path, [name], QDir.Files, QDirIterator.Subdirectories
        )
        return it.next() if it.hasNext() else ""
