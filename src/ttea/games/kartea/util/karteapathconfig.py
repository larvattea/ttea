"""File paths, folders and Qt resources of the KarTEA game.

Importing this module registers the Qt resources of the .qrc
(``resourceskartea_rc``). The private ``_MODS_README_*`` texts are the
README files of the mods folder, one per game language (pt-BR, en-US,
es-ES), mapped by file name in ``_MODS_READMES``.
"""

import configparser
from pathlib import Path

from PySide6.QtCore import QDir, QDirIterator, QFile, QIODevice

# Imported for its side effect: registers the .qrc resources in Qt.
from ttea.games.kartea.resources import resourceskartea_rc  # noqa: F401
from ttea.util import PathConfig

from .inidefaults import KarteaIniDefaults
from .resourcefields import KarteaResourceFields

# README of the mods folder, one file per game language (pt-BR, en-US,
# es-ES). Each is created only if missing, so user notes are not
# overwritten.
_MODS_README_PT = """\
Recursos personalizados do KarTEA
=================================

Coloque aqui imagens e sons para aparecerem na tela de configuração do
jogador, junto com os que já vêm no jogo. Cada arquivo vai na pasta do
recurso que ele substitui:

  images/vehicle/              veículo
  images/horizon/              horizonte (fundo da pista)
  images/environment/          ambiente (esquerda e direita)
  images/target/               alvo
  images/obstacle/             obstáculo
  images/feedback/positive/    feedback visual positivo
  images/feedback/neutral/     feedback visual neutro
  images/feedback/negative/    feedback visual negativo
  sounds/feedback/positive/    som de acerto
  sounds/feedback/neutral/     som neutro
  sounds/feedback/negative/    som de erro

Formatos aceitos:
  imagens: .png (recomendado, com fundo transparente), .jpg, .jpeg, .bmp
  sons:    .wav

Recomendações
-------------

  Veículo      512x512 pixels (mínimo 384x384 em telas Full HD).
               Imagem quadrada, carro visto de trás, fundo
               transparente. Na tela, o carro ocupa um quadrado de 1/5
               da largura: imagem menor fica borrada, e imagem
               retangular sai achatada.
  Alvo e       256x256 pixels (mínimo 100x100). Imagem quadrada, fundo
  obstáculo    transparente. O jogo reduz a imagem para 100x100 antes
               da perspectiva da pista: arquivos maiores não melhoram
               a qualidade.
  Horizonte    imagem larga, como o horizonte original (768x411
               pixels). É ajustada à altura da tela e repetida na
               largura; não precisa de transparência.
  Ambiente     tamanho próximo de 500x520 pixels (como as árvores
               originais). O tamanho na tela segue o tamanho do
               arquivo: imagem muito grande vira um objeto gigante, e
               muito pequena, um objeto minúsculo. A da esquerda e a da
               direita devem estar viradas para o lado certo.
  Feedback     tamanho próximo de 800x200 pixels. É mostrada no tamanho
  visual       original, sem redimensionar: uma foto grande cobre a
               tela.
  Sons         .wav PCM de 16 bits, curtos e com volume parecido com o
               dos sons originais. WAV compactado (ADPCM) ou de 32 bits
               pode não tocar.

O feedback neutro (imagem e som) pode ser escolhido, mas não é usado
durante a partida.

Depois de copiar um arquivo, feche e abra de novo a tela de
configuração para ele aparecer na lista. Se um arquivo escolhido for
apagado, o jogo volta a usar o recurso padrão.
"""

_MODS_README_EN = """\
KarTEA custom resources
=======================

Put images and sounds here to make them available on the player
configuration screen, alongside the ones that come with the game. Each
file goes in the folder of the resource it replaces:

  images/vehicle/              vehicle
  images/horizon/              horizon (track background)
  images/environment/          scenery (left and right)
  images/target/               target
  images/obstacle/             obstacle
  images/feedback/positive/    positive visual feedback
  images/feedback/neutral/     neutral visual feedback
  images/feedback/negative/    negative visual feedback
  sounds/feedback/positive/    hit sound
  sounds/feedback/neutral/     neutral sound
  sounds/feedback/negative/    miss sound

Accepted formats:
  images: .png (recommended, with a transparent background), .jpg,
          .jpeg, .bmp
  sounds: .wav

Recommendations
---------------

  Vehicle      512x512 pixels (at least 384x384 on Full HD screens).
               Square image, car seen from behind, transparent
               background. On screen, the car fills a square 1/5 of the
               screen width: a smaller image looks blurry, and a
               rectangular image ends up squashed.
  Target and   256x256 pixels (at least 100x100). Square image,
  obstacle     transparent background. The game shrinks the image to
               100x100 before the track perspective is applied: larger
               files do not improve quality.
  Horizon      wide image, like the original horizon (768x411
               pixels). It is fitted to the screen height and repeated
               across the width; no transparency needed.
  Scenery      size close to 500x520 pixels (like the original trees).
               The size on screen follows the file size: a very large
               image becomes a giant object, and a very small one a
               tiny object. The left and right images must face the
               correct side.
  Visual       size close to 800x200 pixels. It is shown at its
  feedback     original size, without resizing: a large photo covers
               the screen.
  Sounds       16-bit PCM .wav, short and about as loud as the
               original sounds. Compressed (ADPCM) or 32-bit WAV files
               may not play.

The neutral feedback (image and sound) can be selected, but it is not
used during the game.

After copying a file, close and reopen the configuration screen for it
to appear in the list. If a selected file is deleted, the game goes
back to the default resource.
"""

_MODS_README_ES = """\
Recursos personalizados de KarTEA
=================================

Coloque aquí imágenes y sonidos para que aparezcan en la pantalla de
configuración del jugador, junto con los que ya trae el juego. Cada
archivo va en la carpeta del recurso que reemplaza:

  images/vehicle/              vehículo
  images/horizon/              horizonte (fondo de la pista)
  images/environment/          entorno (izquierda y derecha)
  images/target/               objetivo
  images/obstacle/             obstáculo
  images/feedback/positive/    retroalimentación visual positiva
  images/feedback/neutral/     retroalimentación visual neutra
  images/feedback/negative/    retroalimentación visual negativa
  sounds/feedback/positive/    sonido de acierto
  sounds/feedback/neutral/     sonido neutro
  sounds/feedback/negative/    sonido de error

Formatos aceptados:
  imágenes: .png (recomendado, con fondo transparente), .jpg, .jpeg,
            .bmp
  sonidos:  .wav

Recomendaciones
---------------

  Vehículo     512x512 píxeles (mínimo 384x384 en pantallas Full HD).
               Imagen cuadrada, coche visto desde atrás, fondo
               transparente. En pantalla, el coche ocupa un cuadrado de
               1/5 del ancho: una imagen más pequeña se ve borrosa, y
               una imagen rectangular queda achatada.
  Objetivo y   256x256 píxeles (mínimo 100x100). Imagen cuadrada, fondo
  obstáculo    transparente. El juego reduce la imagen a 100x100 antes
               de aplicar la perspectiva de la pista: los archivos más
               grandes no mejoran la calidad.
  Horizonte    imagen ancha, como el horizonte original (768x411
               píxeles). Se ajusta a la altura de la pantalla y se
               repite a lo ancho; no necesita transparencia.
  Entorno      tamaño cercano a 500x520 píxeles (como los árboles
               originales). El tamaño en pantalla sigue el tamaño del
               archivo: una imagen muy grande se convierte en un objeto
               gigante, y una muy pequeña, en un objeto diminuto. La de
               la izquierda y la de la derecha deben mirar hacia el
               lado correcto.
  Retroali-    tamaño cercano a 800x200 píxeles. Se muestra en su
  mentación    tamaño original, sin redimensionar: una foto grande
  visual       cubre la pantalla.
  Sonidos      .wav PCM de 16 bits, cortos y con un volumen parecido al
               de los sonidos originales. Los WAV comprimidos (ADPCM) o
               de 32 bits pueden no sonar.

La retroalimentación neutra (imagen y sonido) se puede seleccionar,
pero no se usa durante la partida.

Después de copiar un archivo, cierre y vuelva a abrir la pantalla de
configuración para que aparezca en la lista. Si se borra un archivo
seleccionado, el juego vuelve a usar el recurso predeterminado.
"""

_MODS_READMES: dict[str, str] = {
    "LEIA-ME.txt": _MODS_README_PT,
    "README.txt": _MODS_README_EN,
    "LEAME.txt": _MODS_README_ES,
}


class KarteaPathConfig(PathConfig):
    """Path configuration specific to the KarTEA game.

    Inherits all the logic of PathConfig. Class with only class
    attributes and class methods: it is not instantiated.

    Attributes
    ----------
    KARTEA_CONFIG_FILENAME : str, class attribute
        Name of the configuration file ("kartea.ini").
    KARTEA_LOG_FILENAME : str, class attribute
        Name of the log file ("kartea.log").
    KARTEA_DIR : Path, class attribute
        KarTEA data folder (``PathConfig.EXERGAME_DIR / "kartea"``).
    KARTEA_LOG_DIR : Path, class attribute
        Log folder.
    KARTEA_RESOURCES_DIR : Path, class attribute
        Folder of the user's resources (images, sounds, phases).
    KARTEA_IMAGES_DIR : Path, class attribute
        Folder of the user's images.
    KARTEA_SOUNDS_DIR : Path, class attribute
        Folder of the user's sounds.
    KARTEA_PHASES_DIR : Path, class attribute
        Folder of the user's phase CSV files (priority over the built-in
        ones).
    KARTEA_PLAYER_DIR : Path, class attribute
        Folder of the per-player CSV files.
    KARTEA_MODS_DIR : Path, class attribute
        Custom resources (images and sounds) placed by the user.
    KARTEA_CONFIG_FILE : Path, class attribute
        Full path of kartea.ini.
    """

    KARTEA_CONFIG_FILENAME = "kartea.ini"
    KARTEA_LOG_FILENAME = "kartea.log"

    # ==================================================================
    # KarTEA-specific folders
    # ==================================================================
    KARTEA_DIR = PathConfig.EXERGAME_DIR / "kartea"
    KARTEA_LOG_DIR = KARTEA_DIR / "log"
    KARTEA_RESOURCES_DIR = KARTEA_DIR / "resources"
    KARTEA_IMAGES_DIR = KARTEA_RESOURCES_DIR / "images"
    KARTEA_SOUNDS_DIR = KARTEA_RESOURCES_DIR / "sounds"
    KARTEA_PHASES_DIR = KARTEA_RESOURCES_DIR / "phases"
    KARTEA_PLAYER_DIR = KARTEA_DIR / "players"
    # Custom resources (images and sounds) placed by the user.
    # Installed: AppData\Local\udesc\ttea\exergames\kartea\mods.
    KARTEA_MODS_DIR = KARTEA_DIR / "mods"

    KARTEA_CONFIG_FILE = KARTEA_DIR / KARTEA_CONFIG_FILENAME

    # ==================================================================
    # Folder structure
    # ==================================================================
    @classmethod
    def ensure_kartea_dirs(cls) -> None:
        """Create all the folders KarTEA needs.

        Notes
        -----
        Also creates the PathConfig folders, the default kartea.ini (if
        missing) and the mods folders with their README files.
        """
        cls.ensure_dirs()  # PathConfig method
        for directory in [
            cls.KARTEA_DIR,
            cls.KARTEA_LOG_DIR,
            cls.KARTEA_RESOURCES_DIR,
            cls.KARTEA_IMAGES_DIR,
            cls.KARTEA_SOUNDS_DIR,
            cls.KARTEA_PHASES_DIR,
            cls.KARTEA_PLAYER_DIR,
            cls.KARTEA_MODS_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

        cls.create_default_ini()
        cls.ensure_mods_dirs()

    @classmethod
    def ensure_mods_dirs(cls) -> None:
        """Create the mods folder, its subfolders and README files.

        Notes
        -----
        One subfolder per resource field and the README in Portuguese,
        English and Spanish (each created only if it does not exist yet,
        so user notes are not overwritten). OSError is ignored: the game
        works without the folder.
        """
        try:
            for field in KarteaResourceFields.ALL:
                cls.mod_dir_for_field(field.name).mkdir(
                    parents=True, exist_ok=True
                )
            for filename, text in _MODS_READMES.items():
                readme = cls.KARTEA_MODS_DIR / filename
                if not readme.exists():
                    readme.write_text(text, encoding="utf-8")
        except OSError:
            pass

    @classmethod
    def log(cls, filename: str = KARTEA_LOG_FILENAME) -> str:
        """Return the log file path, in the KarTEA log folder.

        Overrides ``PathConfig.log``.

        Parameters
        ----------
        filename : str, optional
            Log file name. Defaults to KARTEA_LOG_FILENAME.

        Returns
        -------
        str
            Full path of the log file (folders are created if missing).
        """
        cls.ensure_kartea_dirs()
        return str(cls.KARTEA_LOG_DIR / filename)

    # ==================================================================
    # Built-in resources (Qt)
    # ==================================================================
    @staticmethod
    def kartea_resource(path: str = "") -> str:
        """Return a Qt resource path under ``:/kartea``.

        Parameters
        ----------
        path : str, optional
            Relative path inside the resource prefix.

        Returns
        -------
        str
            ``:/kartea/{path}`` without a trailing slash.

        Examples
        --------
        >>> KarteaPathConfig.kartea_resource("images")
        ':/kartea/images'
        >>> KarteaPathConfig.kartea_resource()
        ':/kartea'
        """
        return f":/kartea/{path}".rstrip("/")

    @staticmethod
    def _find_resource(base_path: str, name: str) -> str:
        """Return the first built-in resource ``name`` found.

        Searches ``base_path`` and its subfolders; returns "" if not
        found.
        """
        it = QDirIterator(
            base_path, [name], QDir.Files, QDirIterator.Subdirectories
        )
        return it.next() if it.hasNext() else ""

    @staticmethod
    def game_builtin_image(name: str) -> str:
        """Return the Qt path of a built-in image.

        Parameters
        ----------
        name : str
            Resource name (alias in the .qrc).

        Returns
        -------
        str
            The first match under ``:/images`` (subfolders included), or
            "" if not found.
        """
        return KarteaPathConfig._find_resource(":/images", name)

    @staticmethod
    def game_builtin_sound(name: str) -> str:
        """Return the Qt path of a built-in sound.

        Parameters
        ----------
        name : str
            Resource name (alias in the .qrc).

        Returns
        -------
        str
            The first match under ``:/sounds`` (subfolders included), or
            "" if not found.
        """
        return KarteaPathConfig._find_resource(":/sounds", name)

    # ==================================================================
    # Phases
    # ==================================================================
    @classmethod
    def get_phase_source(cls, phase_id: int) -> dict[str, str]:
        """Return where the CSV of a phase is read from.

        Parameters
        ----------
        phase_id : int
            Id of the phase.

        Returns
        -------
        dict[str, str]
            ``{"type": "file", "path": ...}`` when the user's phases
            folder has ``{phase_id}.csv``; otherwise ``{"type":
            "resource", "path": ":/phases/{phase_id}"}``.
        """
        user_file = cls.KARTEA_PHASES_DIR / f"{phase_id}.csv"
        if user_file.exists():
            return {"type": "file", "path": str(user_file)}
        return {"type": "resource", "path": f":/phases/{phase_id}"}

    @classmethod
    def read_phase_data(cls, phase_id: int) -> str | None:
        """Return the CSV content of a phase.

        Parameters
        ----------
        phase_id : int
            Id of the phase.

        Returns
        -------
        str | None
            The CSV text, or None if it cannot be read.

        Notes
        -----
        The user's file takes priority over the built-in resource (see
        ``get_phase_source``). The user's file is read as UTF-8 with or
        without BOM; any error reading it returns None.
        """
        source = cls.get_phase_source(phase_id)

        if source["type"] == "file":
            try:
                return Path(source["path"]).read_text(encoding="utf-8-sig")
            except Exception:
                return None

        qfile = QFile(source["path"])
        if qfile.open(QIODevice.ReadOnly | QIODevice.Text):
            content = bytes(qfile.readAll()).decode("utf-8")
            qfile.close()
            return content
        return None

    # ==================================================================
    # User data paths
    # ==================================================================
    @classmethod
    def player(cls, filename: str) -> str:
        """Return the path of a file in the players folder.

        Parameters
        ----------
        filename : str
            File name.

        Returns
        -------
        str
            Full path (folders are created if missing).
        """
        cls.ensure_kartea_dirs()
        return str(cls.KARTEA_PLAYER_DIR / filename)

    @classmethod
    def phase(cls, filename: str) -> str:
        """Return the path of a file in the user's phases folder.

        Parameters
        ----------
        filename : str
            File name.

        Returns
        -------
        str
            Full path (folders are created if missing).
        """
        cls.ensure_kartea_dirs()
        return str(cls.KARTEA_PHASES_DIR / filename)

    @classmethod
    def kartea_config(cls, filename: str = KARTEA_CONFIG_FILENAME) -> str:
        """Return the path of a configuration file in the KarTEA folder.

        Parameters
        ----------
        filename : str, optional
            File name. Defaults to KARTEA_CONFIG_FILENAME.

        Returns
        -------
        str
            Full path (folders are created if missing).
        """
        cls.ensure_kartea_dirs()
        return str(cls.KARTEA_DIR / filename)

    @classmethod
    def game_image(cls, filename: str) -> str:
        """Return the path of a file in the user's images folder.

        Parameters
        ----------
        filename : str
            File name.

        Returns
        -------
        str
            Full path (folders are created if missing).
        """
        cls.ensure_kartea_dirs()
        return str(cls.KARTEA_IMAGES_DIR / filename)

    @classmethod
    def game_sound(cls, filename: str) -> str:
        """Return the path of a file in the user's sounds folder.

        Parameters
        ----------
        filename : str
            File name.

        Returns
        -------
        str
            Full path (folders are created if missing).
        """
        cls.ensure_kartea_dirs()
        return str(cls.KARTEA_SOUNDS_DIR / filename)

    # ==================================================================
    # INI configuration
    # ==================================================================
    @classmethod
    def kartea_config_file_exists(
        cls, filename: str = KARTEA_CONFIG_FILENAME
    ) -> bool:
        """Check whether a KarTEA configuration file exists.

        Parameters
        ----------
        filename : str, optional
            File name. Defaults to KARTEA_CONFIG_FILENAME.

        Returns
        -------
        bool
            True if the file exists.

        Notes
        -----
        Ensures the folders first, which also creates the default
        kartea.ini; so for the default file name the result is normally
        True.
        """
        return Path(cls.kartea_config(filename)).exists()

    @classmethod
    def read_config(cls) -> dict[str, dict[str, str]]:
        """Read kartea.ini.

        Returns
        -------
        dict[str, dict[str, str]]
            ``{section: {key: value}}``, as read by ConfigParser (keys
            in lowercase).
        """
        cls.ensure_kartea_dirs()
        config = configparser.ConfigParser()
        config.read(cls.KARTEA_CONFIG_FILE)
        return {
            section: dict(config[section]) for section in config.sections()
        }

    @classmethod
    def create_default_ini(cls) -> None:
        """Create kartea.ini with the defaults, if missing.

        Notes
        -----
        Values come from the single table KarteaIniDefaults.TABLE
        (util/inidefaults.py). An existing file is never changed.
        """
        if cls.KARTEA_CONFIG_FILE.exists():
            return

        config = configparser.ConfigParser(allow_no_value=True)
        config.read_dict(KarteaIniDefaults.sections())

        with open(cls.KARTEA_CONFIG_FILE, "w", encoding="utf-8") as f:
            config.write(f)

    # ==================================================================
    # Listings
    # ==================================================================
    @classmethod
    def list_images(cls) -> list[str]:
        """Return the image files of the user's images folder.

        Returns
        -------
        list[str]
            Sorted file names with extension .png, .jpg, .jpeg, .gif,
            .bmp or .tiff.
        """
        cls.ensure_kartea_dirs()
        exts = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"}
        return sorted(
            f.name
            for f in cls.KARTEA_IMAGES_DIR.iterdir()
            if f.is_file() and f.suffix.lower() in exts
        )

    @classmethod
    def list_sounds(cls) -> list[str]:
        """Return the sound files of the user's sounds folder.

        Returns
        -------
        list[str]
            Sorted file names with extension .wav, .mp3, .ogg, .flac or
            .aac.
        """
        cls.ensure_kartea_dirs()
        exts = {".wav", ".mp3", ".ogg", ".flac", ".aac"}
        return sorted(
            f.name
            for f in cls.KARTEA_SOUNDS_DIR.iterdir()
            if f.is_file() and f.suffix.lower() in exts
        )

    # ==================================================================
    # Built-in resources by field
    # ==================================================================
    @staticmethod
    def list_builtin_resources(base_path: str) -> list[tuple[str, str]]:
        """Return the Qt resources under ``base_path``.

        Parameters
        ----------
        base_path : str
            Qt resource folder, e.g. ":/images/vehicle".

        Returns
        -------
        list[tuple[str, str]]
            Sorted ``[(name, path)]``, subfolders included.
        """
        result = []
        it = QDirIterator(base_path, QDir.Files, QDirIterator.Subdirectories)
        while it.hasNext():
            path = it.next()
            name = it.fileName()
            result.append((name, path))
        return sorted(result)

    @classmethod
    def list_builtin_for_field(cls, field: str) -> list[tuple[str, str]]:
        """Return the built-in resources of a configuration field.

        Parameters
        ----------
        field : str
            Field name (e.g. "vehicle_image"), as in
            KarteaResourceFields.ALL.

        Returns
        -------
        list[tuple[str, str]]
            ``[(name, path)]`` from the field's ``builtin_dir``.
        """
        return cls.list_builtin_resources(
            KarteaResourceFields.get(field).builtin_dir
        )

    @classmethod
    def find_builtin_for_field(cls, field: str, name: str) -> str:
        """Return the Qt path of a built-in resource of ``field``.

        Searches ``name`` only in the field's ``builtin_dir`` (e.g.
        ":/sounds/feedback/positive"), so that an equal name in another
        folder is not chosen.

        Parameters
        ----------
        field : str
            Field name, as in KarteaResourceFields.ALL.
        name : str
            Resource name.

        Returns
        -------
        str
            The Qt path, or "" if ``name`` is empty or does not exist
            there.
        """
        if not name:
            return ""
        return cls._find_resource(
            KarteaResourceFields.get(field).builtin_dir, name
        )

    # ==================================================================
    # Custom resources (mods folder)
    # ==================================================================
    @classmethod
    def mod_dir_for_field(cls, field: str) -> Path:
        """Return the mods folder of a field.

        Parameters
        ----------
        field : str
            Field name, as in KarteaResourceFields.ALL.

        Returns
        -------
        Path
            E.g. ``mods/sounds/feedback/positive``.
        """
        return cls.KARTEA_MODS_DIR / KarteaResourceFields.get(field).mod_subdir

    @classmethod
    def list_mod_for_field(cls, field: str) -> list[tuple[str, str]]:
        """Return the files of the field's mods folder.

        Only files directly in the folder, with the extensions accepted
        for the field. The displayed name has an extension, so it never
        matches a built-in resource (.qrc aliases have no extension).

        Parameters
        ----------
        field : str
            Field name, as in KarteaResourceFields.ALL.

        Returns
        -------
        list[tuple[str, str]]
            ``[(name, path)]`` sorted by name (case-insensitive); empty
            if the folder cannot be read.
        """
        folder = cls.mod_dir_for_field(field)
        extensions = KarteaResourceFields.get(field).mod_extensions
        try:
            files = [
                f
                for f in folder.iterdir()
                if f.is_file() and f.suffix.lower() in extensions
            ]
        except OSError:
            return []
        files.sort(key=lambda f: f.name.lower())
        return [(f.name, str(f)) for f in files]

    @classmethod
    def find_mod_for_field(cls, field: str, name: str) -> str:
        """Return the path of file ``name`` in the field's mods folder.

        Parameters
        ----------
        field : str
            Field name, as in KarteaResourceFields.ALL.
        name : str
            File name only (no folders), with an extension accepted for
            the field.

        Returns
        -------
        str
            The file path, or "" if ``name`` is invalid or the file does
            not exist.
        """
        if not name or Path(name).name != name:
            return ""
        if Path(name).suffix.lower() not in (
            KarteaResourceFields.get(field).mod_extensions
        ):
            return ""
        path = cls.mod_dir_for_field(field) / name
        return str(path) if path.is_file() else ""

    # ==================================================================
    # Built-in + mods
    # ==================================================================
    @classmethod
    def list_resources_for_field(cls, field: str) -> list[tuple[str, str]]:
        """Return the resources available for a field.

        Parameters
        ----------
        field : str
            Field name, as in KarteaResourceFields.ALL.

        Returns
        -------
        list[tuple[str, str]]
            ``[(name, path)]``: the built-in ones and, after them, those
            of the mods folder.
        """
        return cls.list_builtin_for_field(field) + cls.list_mod_for_field(
            field
        )

    @classmethod
    def resolve_for_field(cls, field: str, name: str) -> str:
        """Return the path of resource ``name`` of a field.

        Parameters
        ----------
        field : str
            Field name, as in KarteaResourceFields.ALL.
        name : str
            Resource name (built-in alias or mods file name).

        Returns
        -------
        str
            Qt path (":/...") if built-in, the mods file path, or "" if
            it does not exist.
        """
        return cls.find_builtin_for_field(
            field, name
        ) or cls.find_mod_for_field(field, name)

    @classmethod
    def resolve_for_field_or_default(cls, field: str, name: str) -> str:
        """Return the path of a field resource, or of its default.

        Like ``resolve_for_field``, but uses the field default
        (KarteaResourceFields.ALL) when ``name`` is empty or no longer
        exists (e.g. a file deleted from the mods folder).

        Parameters
        ----------
        field : str
            Field name, as in KarteaResourceFields.ALL.
        name : str
            Resource name.

        Returns
        -------
        str
            The resolved path, or "" if even the default does not exist.
        """
        return cls.resolve_for_field(field, name) or cls.resolve_for_field(
            field, KarteaResourceFields.get(field).default
        )
