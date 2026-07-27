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
    APP_NAME : str
        Application name used for platform-specific data directories.
    APP_AUTHOR : str
        Application author name used for platform-specific data
        directories.
    CONFIG_FILENAME : str
        Default file name for configuration files.
    CALIBRATION_FILENAME : str
        Default file name for calibration settings.
    CALIBRATION_POINT_FILENAME : str
        Default file name for calibration point CSV data.
    BASE_DIR : Path
        Base application data directory in development or frozen mode.
    EXERGAME_DIR : Path
        Base directory for exergame save data.
    CONFIG_DIR : Path
        Directory for configuration files.
    CALIBRATION_DIR : Path
        Directory for calibration files.
    EXPORTS_DIR : Path
        Directory for exported files.
    INSTITUTIONFACILITY_DIR : Path
        Directory for institution facility data.
    LOG_DIR : Path
        Directory for log files.
    MODELS_DIR : Path
        Directory for Mediapipe models.
    PLAYERS_DIR : Path
        Directory for player files.
    PROFESSIONAL_DIR : Path
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
    help(path='')
        Return a Qt help resource path.
    ensure_dirs()
        Create all user directories.
    config(filename=CONFIG_FILENAME)
        Return application config file path.

    Examples
    --------
    >>> PathConfig.ensure_dirs()
    >>> PathConfig.config()
    '.../data/config/config.ini'
    >>> PathConfig.resource('images/logo.png')
    ': /images/logo.png'
    """

    APP_NAME = "ttea"
    APP_AUTHOR = "udesc"

    CONFIG_FILENAME = "config.ini"
    CALIBRATION_FILENAME = "calibration.ini"
    CALIBRATION_POINT_FILENAME = "calibration_point.csv"

    # ===================================================================
    # Base directory
    # ===================================================================
    if getattr(sys, "frozen", False):
        BASE_DIR: Path = Path(user_data_dir(APP_NAME, APP_AUTHOR))
        EXERGAME_DIR: Path = BASE_DIR / "exergames"
    else:
        PROJECT_DIR: Path = Path(__file__).resolve().parents[2]
        EXERGAME_DIR: Path = PROJECT_DIR / "src" / "games"
        BASE_DIR: Path = PROJECT_DIR / "data"

    # Subdirectories — add new folders here
    CONFIG_DIR: Path = BASE_DIR / "config"
    CALIBRATION_DIR: Path = BASE_DIR / "calibration"
    EXPORTS_DIR: Path = BASE_DIR / "exports"
    INSTITUTIONFACILITY_DIR: Path = BASE_DIR / "institutionfacilities"
    LOG_DIR: Path = BASE_DIR / "log"
    MODELS_DIR: Path = BASE_DIR / "mediapipemodels"
    PLAYERS_DIR: Path = BASE_DIR / "players"
    PROFESSIONAL_DIR: Path = BASE_DIR / "professionals"

    # ===================================================================
    # Built-in Resources (Qt)
    # ===================================================================
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
        Trailing slashes are removed from the generated resource path.

        Examples
        --------
        >>> PathConfig.resource('images/logo.png')
        ':/images/logo.png'
        >>> PathConfig.resource()
        ':/'
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

    @staticmethod
    def help(path: str = "") -> str:
        """Return a Qt resource path for help content.

        Parameters
        ----------
        path : str, optional
            Help content file or folder name. Default is empty string.

        Returns
        -------
        str
            Qt path for the help resource.
        """
        return f":/help/{path}".rstrip("/")

    # ===================================================================
    # Automatic Introspection
    # ===================================================================
    @classmethod
    def _get_dir_names(cls) -> List[str]:
        """Return class attribute names that end with ``_DIR``.

        Returns
        -------
        list[str]
            Sorted or unsorted names of directory attributes.
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

    # ===================================================================
    # User data methods
    # ===================================================================
    @classmethod
    def ensure_dirs(cls) -> None:
        """Create all configured directories if they do not exist.

        Returns
        -------
        None
            Ensures all directories defined by the class are present on disk.
        """
        for directory in cls._get_user_dirs():
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def _user_file(cls, directory: Path, filename: str) -> str:
        """Return the full file path for a given user directory.

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
            Name of the configuration file. Defaults to the class constant.

        Returns
        -------
        str
            Full path to the configuration file.

        Examples
        --------
        >>> PathConfig.config()
        '.../data/config/config.ini'
        """
        return cls._user_file(cls.CONFIG_DIR, filename)

    @classmethod
    def calibration(cls, filename: str = CALIBRATION_FILENAME) -> str:
        """Return the calibration file path.

        Parameters
        ----------
        filename : str, optional
            Name of the calibration file. Defaults to the class constant.

        Returns
        -------
        str
            Full path to the calibration file.
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
            Name of the calibration point CSV file. Defaults to the class
            constant.

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
        """Return the Mediapipe model file path.

        Parameters
        ----------
        filename : str
            Name of the model file.

        Returns
        -------
        str
            Full path to the model file.
        """
        return cls._user_file(cls.MODELS_DIR, filename)

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
        """
        cls.ensure_dirs()
        game_dir = cls.EXERGAME_DIR / game_name
        game_dir.mkdir(exist_ok=True)
        return str(game_dir / filename)

    # ===================================================================
    # Test support
    # ===================================================================
    @classmethod
    def set_base_dir(cls, path: str | Path) -> None:
        """Set a different base directory, primarily for tests.

        Parameters
        ----------
        path : str or Path
            New base directory path.

        Returns
        -------
        None
            Updates class directory attributes to point at the new base.

        Examples
        --------
        >>> PathConfig.set_base_dir('/tmp/ttestate')
        >>> PathConfig.CONFIG_DIR
        PosixPath('/tmp/ttestate/config')
        """
        new_base = Path(path).resolve()

        cls.BASE_DIR = new_base
        cls.EXERGAME_DIR = new_base / "exergames"

        for dir_name in cls._get_dir_names():
            if dir_name in ("BASE_DIR", "EXERGAME_DIR"):
                continue
            subdir = dir_name.replace("_DIR", "").lower()
            setattr(cls, dir_name, new_base / subdir)

    # ===================================================================
    # Checks
    # ===================================================================
    @classmethod
    def config_file_exists(cls, filename: str = CONFIG_FILENAME) -> bool:
        """Return whether the configuration file exists.

        Parameters
        ----------
        filename : str, optional
            Name of the configuration file. Defaults to the class constant.

        Returns
        -------
        bool
            True if the configuration file exists, otherwise False.
        """
        return Path(cls.config(filename)).exists()

    @classmethod
    def calibration_file_exists(
        cls, filename: str = CALIBRATION_FILENAME
    ) -> bool:
        """Return whether the calibration file exists.

        Parameters
        ----------
        filename : str, optional
            Name of the calibration file. Defaults to the class constant.

        Returns
        -------
        bool
            True if the calibration file exists, otherwise False.
        """
        return Path(cls.calibration(filename)).exists()

    # ===================================================================
    # Utilities
    # ===================================================================
    @classmethod
    def path_help_pt(cls, filename: str) -> str:
        """Return the Portuguese help resource path.

        Parameters
        ----------
        filename : str
            Help file name relative to the Portuguese help folder.

        Returns
        -------
        str
            Qt resource path for the Portuguese help file.
        """
        return cls.help(f"pt/{filename}")

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
            Full resource path if found, otherwise an empty string.

        Examples
        --------
        >>> PathConfig.find_resource_built_in(':/help', 'index.html')
        ':/help/pt/index.html'
        """
        it = QDirIterator(
            base_path, [name], QDir.Files, QDirIterator.Subdirectories
        )
        return it.next() if it.hasNext() else ""
