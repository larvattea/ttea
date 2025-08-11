from pathlib import Path
from typing import List


class PathConfig:
    """Configuration class for file and directory paths.

    This class provides a centralized way to manage file and directory paths
    used throughout the application, ensuring consistent path handling and
    directory creation.

    Attributes
    ----------
    root : Path
        The root directory of the project (current working directory).
    log_dir : Path
        Directory for log files.
    players_dir : Path
        Directory for player-related files.
    games_dir : Path
        Directory containing game subdirectories.
    assets_dir : Path
        Directory for asset files.
    translations_dir : Path
        Directory for translation files.
    images_dir : Path
        Directory for image files, nested under assets.
    icons_dir : Path
        Directory for icon files, nested under assets.
    helps_dir : Path
        Directory for help files.
    helps_dir_pt : Path
        Directory for Portuguese help files, nested under helps_dir.

    Methods
    -------
    create_directories() -> None
        Creates necessary directories (e.g., players_dir) if they do not exist
        to prevent file access errors.
    icon(filename: str) -> str
        Returns the full path to an icon file in the icons_dir.
    image(filename: str) -> str
        Returns the full path to an image file in the images_dir.
    log(filename: str) -> str
        Returns the full path to a log file in the log_dir.
    player(filename: str) -> str
        Returns the full path to a player file in the players_dir.
    translation(filename: str) -> str
        Returns the full path to a translation file in the translations_dir.
    inifile(filename: str) -> str
        Returns the full path to an ini file in the root directory.
    path_games() -> List[str]
        Lists all subdirectory names in the games_dir, excluding special
        directories like '__pycache__'.
    path_help_pt(filename: str) -> str
        Returns the full path to a Portuguese help file in the helps_dir_pt.
    """

    root = Path.cwd()
    log_dir = root / "log"
    players_dir = root / "players"
    games_dir = root / "udescjoinvilletteagames"
    assets_dir = root / "assets"
    translations_dir = root / "translations"
    images_dir = assets_dir / "images"
    icons_dir = assets_dir / "icons"
    helps_dir = root / "help"
    helps_dir_pt = helps_dir / "pt"

    @classmethod
    def create_directories(cls) -> None:
        """Create necessary directories if they do not exist.

        This method ensures that critical directories (e.g., players_dir) are
        created to prevent file access errors.

        Returns
        -------
        None

        Notes
        -----
        Currently, only the `players_dir` is created. Additional directories
        can be added to the list as needed.
        """
        for directory in [cls.players_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def icon(cls, filename: str) -> str:
        """Get the full path to an icon file.

        Parameters
        ----------
        filename : str
            Name of the icon file.

        Returns
        -------
        str
            Full path to the icon file.

        Examples
        --------
        >>> PathConfig.icon("example.png")
        '/path/to/project/assets/icons/example.png'
        """
        return str(cls.icons_dir / filename)

    @classmethod
    def image(cls, filename: str) -> str:
        """Get the full path to an image file.

        Parameters
        ----------
        filename : str
            Name of the image file.

        Returns
        -------
        str
            Full path to the image file.

        Examples
        --------
        >>> PathConfig.image("background.jpg")
        '/path/to/project/assets/images/background.jpg'
        """
        return str(cls.images_dir / filename)

    @classmethod
    def log(cls, filename: str) -> str:
        """Get the full path to a log file.

        Parameters
        ----------
        filename : str
            Name of the log file.

        Returns
        -------
        str
            Full path to the log file.

        Examples
        --------
        >>> PathConfig.log("app.log")
        '/path/to/project/log/app.log'
        """
        return str(cls.log_dir / filename)

    @classmethod
    def player(cls, filename: str) -> str:
        """Get the full path to a player file.

        Parameters
        ----------
        filename : str
            Name of the player file.

        Returns
        -------
        str
            Full path to the player file.

        Examples
        --------
        >>> PathConfig.player("player1.json")
        '/path/to/project/players/player1.json'
        """
        return str(cls.players_dir / filename)

    @classmethod
    def translation(cls, filename: str) -> str:
        """Get the full path to a translation file.

        Parameters
        ----------
        filename : str
            Name of the translation file.

        Returns
        -------
        str
            Full path to the translation file.

        Examples
        --------
        >>> PathConfig.translation("pt_BR.ts")
        '/path/to/project/translations/pt_BR.ts'
        """
        return str(cls.translations_dir / filename)

    @classmethod
    def inifile(cls, filename: str) -> str:
        """Get the full path to an ini file in the root directory.

        Parameters
        ----------
        filename : str
            Name of the ini file.

        Returns
        -------
        str
            Full path to the ini file.

        Examples
        --------
        >>> PathConfig.inifile("config.ini")
        '/path/to/project/config.ini'
        """
        return str(cls.root / filename)

    @classmethod
    def path_games(cls) -> List[str]:
        """Get a list of game directory names.

        This method lists all subdirectories in the games_dir, excluding
        special directories like '__pycache__'.

        Returns
        -------
        List[str]
            List of directory names within the games directory.

        Raises
        ------
        FileNotFoundError
            If the games directory does not exist.

        Examples
        --------
        >>> PathConfig.path_games()
        ['game1', 'game2', 'game3']
        """
        cls.create_directories()
        return [
            d.name
            for d in cls.games_dir.iterdir()
            if d.is_dir() and d.name != "__pycache__"
        ]

    @classmethod
    def path_help_pt(cls, filename: str) -> str:
        """Get the full path to a Portuguese help file.

        Parameters
        ----------
        filename : str
            Name of the help file.

        Returns
        -------
        str
            Full path to the help file.

        Examples
        --------
        >>> PathConfig.path_help_pt("index.html")
        '/path/to/project/help/pt/index.html'
        """
        return str(cls.helps_dir_pt / filename)
