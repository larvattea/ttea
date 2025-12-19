import configparser

from udescjoinvilletteautil import PathConfig


class KarteaPathConfig(PathConfig):
    """Config class for KarTEA file and dir paths.

    Extends `PathConfig` to define paths for KarTEA dirs like assets,
    images, sounds, phases, and player data. Provides methods to create
    dirs, get file paths, and list image and sound files.

    Attributes
    ----------
    kartea_dir : Path
        Base dir for KarTEA game data.
    kartea_assets_dir : Path
        Dir for KarTEA assets (images, sounds, etc.).
    kartea_images_dir : Path
        Dir for KarTEA image files.
    kartea_sounds_dir : Path
        Dir for KarTEA sound files.
    kartea_phases_dir : Path
        Dir for KarTEA phase config files.
    kartea_players_dir : Path
        Dir for KarTEA player data files.

    Methods
    -------
    create_directories()
        Creates necessary KarTEA dirs.
    kartea_image(filename)
        Gets full path to an image file.
    kartea_sound(filename)
        Gets full path to a sound file.
    kartea_player(filename)
        Gets full path to a player file.
    list_images()
        Lists image file names in kartea_images_dir.
    list_sounds()
        Lists sound file names in kartea_sounds_dir.
    read_config()
        Reads config values from kartea.ini.
    """

    kartea_dir = PathConfig.GAMES_DIR / "kartea"
    kartea_assets_dir = kartea_dir / "assets"
    kartea_images_dir = kartea_assets_dir / "images"
    kartea_sounds_dir = kartea_assets_dir / "sounds"
    kartea_phases_dir = kartea_dir / "phases"
    kartea_players_dir = kartea_dir / "players"

    @classmethod
    def create_directories(cls) -> None:
        """Create necessary KarTEA dirs if they don't exist.

        Ensures dirs for players, images, sounds, and phases are created
        with parents as needed. Existing dirs are not modified.
        """
        for directory in [
            cls.kartea_players_dir,
            cls.kartea_images_dir,
            cls.kartea_sounds_dir,
            cls.kartea_phases_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def kartea_image(cls, filename: str) -> str:
        """Return full path to a KarTEA image file.

        Parameters
        ----------
        filename : str
            Name of the image file (e.g., 'background.png').

        Returns
        -------
        str
            Full path to the image file in kartea_images_dir.
        """
        cls.create_directories()
        return str(cls.kartea_images_dir / filename)

    @classmethod
    def kartea_sound(cls, filename: str) -> str:
        """Return full path to a KarTEA sound file.

        Parameters
        ----------
        filename : str
            Name of the sound file (e.g., 'music.mp3').

        Returns
        -------
        str
            Full path to the sound file in kartea_sounds_dir.
        """
        cls.create_directories()
        return str(cls.kartea_sounds_dir / filename)

    @classmethod
    def kartea_player(cls, filename: str) -> str:
        """Return full path to a KarTEA player file.

        Parameters
        ----------
        filename : str
            Name of the player file (e.g., 'player.csv').

        Returns
        -------
        str
            Full path to the player file in kartea_players_dir.
        """
        cls.create_directories()
        return str(cls.kartea_players_dir / filename)

    @classmethod
    def list_images(cls) -> list[str]:
        """List image file names in kartea_images_dir.

        Includes files with extensions like .png, .jpg, .jpeg, .gif,
        .bmp, .tiff. Sorted alphabetically.

        Returns
        -------
        list[str]
            List of image file names (no paths) in kartea_images_dir.
            Empty list if no image files are found.
        """
        cls.create_directories()
        image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"}
        images = [
            file.name
            for file in cls.kartea_images_dir.glob("*")
            if file.is_file() and file.suffix.lower() in image_extensions
        ]
        return sorted(images)

    @classmethod
    def list_sounds(cls) -> list[str]:
        """List sound file names in kartea_sounds_dir.

        Includes files with extensions like .wav, .mp3, .ogg, .flac,
        .aac. Sorted alphabetically.

        Returns
        -------
        list[str]
            List of sound file names (no paths) in kartea_sounds_dir.
            Empty list if no sound files are found.
        """
        cls.create_directories()
        sound_extensions = {".wav", ".mp3", ".ogg", ".flac", ".aac"}
        sounds = [
            file.name
            for file in cls.kartea_sounds_dir.glob("*")
            if file.is_file() and file.suffix.lower() in sound_extensions
        ]
        return sorted(sounds)

    @classmethod
    def read_config(cls) -> dict[str, dict[str, str]]:
        """Read config values from kartea.ini in kartea_dir.

        Loads kartea.ini and returns its values as a dict where keys are
        section names and values are dicts of key-value pairs. Raises
        FileNotFoundError if kartea.ini is missing or configparser.Error
        if the file is malformed.

        Returns
        -------
        dict[str, dict[str, str]]
            Dict with section names as keys and key-value pairs as dicts.
        """
        config = configparser.ConfigParser()
        config_path = cls.kartea_dir / "kartea.ini"
        config.read(config_path)
        return {
            section: dict(config[section]) for section in config.sections()
        }
