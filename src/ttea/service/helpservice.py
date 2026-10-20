"""Help service: help files, languages and topics.

The help is compiled by ``resources/help/buildhelp.py`` into one .qch
file per language (``ttea_<language>.qch``). This service registers the
file of the current language in a help collection stored in the user
data folder, and translates screens and topic ids into help URLs.
"""

from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtHelp import QHelpEngine, QHelpEngineCore
from PySide6.QtWidgets import QWidget

from ttea.model import Language
from ttea.util import PathConfig


class HelpUnavailableError(RuntimeError):
    """Raised when the help files are missing or cannot be opened."""


class HelpService:
    """Locate, register and query the compiled help.

    Attributes
    ----------
    HOME_TOPIC : str, class attribute
        Topic opened when no other topic applies (``"inicio"``).
    HELP_ID_PROPERTY : str, class attribute
        Qt property that overrides the topic of a widget and its
        children, e.g. ``widget.setProperty("help_id", "calibracao")``.
    VIRTUAL_FOLDER : str, class attribute
        Virtual folder of the pages inside the help (``"doc"``).
    TOPICS : dict[str, str], class attribute
        Topic id to page path inside the help, the same in every
        language.
    VIEW_TOPICS : dict[str, str], class attribute
        Screen class name to topic id. Used by F1 to find the topic of
        the active screen without changing the screens.

    Notes
    -----
    Typical use: ``engine = service.create_engine("en_US")`` and then
    ``service.topic_url(engine, "cadastro_jogador")``.
    """

    HOME_TOPIC = "inicio"
    HELP_ID_PROPERTY = "help_id"
    VIRTUAL_FOLDER = "doc"

    TOPICS: dict[str, str] = {
        "inicio": "index.html",
        "plataforma": "introducao/plataforma.html",
        "primeiro_uso": "introducao/primeiro_uso.html",
        "cadastro_instituicao": "cadastro/instituicao.html",
        "cadastro_profissional": "cadastro/profissional.html",
        "cadastro_jogador": "cadastro/jogador.html",
        "sessao_de_jogo": "exergames/sessao_de_jogo.html",
        "calibracao": "configuracoes/calibracao.html",
        "calibracao_manual": "configuracoes/calibracao_manual.html",
        "calibracao_automatica": "configuracoes/calibracao_automatica.html",
        "configuracao_calibracao": "sistema/configuracao_calibracao.html",
        "idioma": "sistema/idioma.html",
        "kartea": "jogos/kartea/index.html",
        "kartea_configuracao": "jogos/kartea/configuracao.html",
        "problemas": "problemas/index.html",
    }

    VIEW_TOPICS: dict[str, str] = {
        "MainView": "inicio",
        "AboutView": "plataforma",
        "InstitutionFacilityListView": "cadastro_instituicao",
        "InstitutionFacilityEditView": "cadastro_instituicao",
        "ProfessionalListView": "cadastro_profissional",
        "ProfessionalEditView": "cadastro_profissional",
        "PlayerListView": "cadastro_jogador",
        "PlayerEditView": "cadastro_jogador",
        "PlayerGameLaunchView": "sessao_de_jogo",
        "CalibrationView": "calibracao",
        "ManualCalibrationView": "calibracao_manual",
        "AutomaticCalibrationView": "calibracao_automatica",
        "CalibrationSettingView": "configuracao_calibracao",
        "LanguageView": "idioma",
        # Game screens are matched by name, so the platform does not
        # import the game packages.
        "PlayerKarteaConfigListView": "kartea_configuracao",
        "PlayerKarteaConfigEditView": "kartea_configuracao",
    }

    # ------------------------------------------------------------------
    # Files and languages
    # ------------------------------------------------------------------
    def help_language(self, language: str) -> str:
        """Return the language whose help file will be used.

        Parameters
        ----------
        language : str
            Requested language code, e.g. ``"es_ES"``.

        Returns
        -------
        str
            ``language`` if its help file exists, otherwise the default
            language.

        Raises
        ------
        HelpUnavailableError
            If no help file exists at all.
        """
        for code in (language, Language.DEFAULT_LANGUAGE):
            if PathConfig.help_file(code).is_file():
                return code
        raise HelpUnavailableError(
            f"Help file not found: {PathConfig.help_file(language)}"
        )

    def create_engine(self, language: str) -> QHelpEngine:
        """Create a help engine for ``language``.

        Parameters
        ----------
        language : str
            Language code; falls back to the default language when its
            help file is missing.

        Returns
        -------
        QHelpEngine
            Engine ready to use. The caller owns it.

        Raises
        ------
        HelpUnavailableError
            If no help file exists or the collection cannot be set up.
        """
        code = self.help_language(language)
        collection = PathConfig.help_collection(code)
        self._register(collection, PathConfig.help_file(code))

        engine = QHelpEngine(collection)
        engine.setReadOnly(False)  # the search index is written here
        if not engine.setupData():
            raise HelpUnavailableError(engine.error())
        return engine

    @staticmethod
    def _register(collection: str, qch: Path) -> None:
        """Register ``qch`` in ``collection``, refreshing it if changed.

        The collection copies the table of contents and the index when a
        file is registered, so the file is registered again whenever it
        changes (new version) or moves (new install folder).

        Raises
        ------
        HelpUnavailableError
            If the collection cannot be set up, the file is not a valid
            help file or its registration fails.
        """
        core = QHelpEngineCore(collection)
        core.setReadOnly(False)
        if not core.setupData():
            raise HelpUnavailableError(core.error())

        namespace = QHelpEngineCore.namespaceName(str(qch))
        if not namespace:
            raise HelpUnavailableError(f"Invalid help file: {qch}")

        signature = f"{qch.resolve()}|{qch.stat().st_mtime_ns}"
        if core.customValue("qch_signature") != signature:
            # One collection per language, used only by this app.
            for registered in core.registeredDocumentations():
                core.unregisterDocumentation(registered)
            core.setCustomValue("qch_signature", signature)

        if namespace not in core.registeredDocumentations():
            if not core.registerDocumentation(str(qch)):
                raise HelpUnavailableError(core.error())

    # ------------------------------------------------------------------
    # Topics
    # ------------------------------------------------------------------
    def topic_for_widget(self, widget: QWidget | None) -> str:
        """Return the topic id for ``widget`` or its nearest parent.

        A ``help_id`` property wins over the screen class name. Widgets
        without a topic inherit the topic of their parent window, up to
        the main window.

        Parameters
        ----------
        widget : QWidget | None
            Widget with focus, or the active window.

        Returns
        -------
        str
            Topic id; ``HOME_TOPIC`` when nothing matches.
        """
        while widget is not None:
            help_id = widget.property(self.HELP_ID_PROPERTY)
            if help_id and help_id in self.TOPICS:
                return help_id
            topic = self.VIEW_TOPICS.get(type(widget).__name__)
            if topic:
                return topic
            widget = widget.parentWidget()
        return self.HOME_TOPIC

    def topic_url(self, engine: QHelpEngineCore, topic: str) -> QUrl:
        """Return the URL of ``topic`` in the help of ``engine``.

        Parameters
        ----------
        engine : QHelpEngineCore
            Engine returned by ``create_engine``.
        topic : str
            Topic id from ``TOPICS``. Unknown topics and missing pages
            fall back to the home page.

        Returns
        -------
        QUrl
            ``qthelp://<namespace>/doc/<page>`` URL of the first
            registered documentation.

        Raises
        ------
        HelpUnavailableError
            If the engine has no registered documentation.
        """
        namespaces = engine.registeredDocumentations()
        if not namespaces:
            raise HelpUnavailableError("No help documentation registered.")

        home = self._url(namespaces[0], self.TOPICS[self.HOME_TOPIC])
        page = self.TOPICS.get(topic)
        if page is None:
            return home
        url = self._url(namespaces[0], page)
        return home if engine.fileData(url).isEmpty() else url

    def _url(self, namespace: str, page: str) -> QUrl:
        """Build the help URL of ``page``."""
        return QUrl(f"qthelp://{namespace}/{self.VIRTUAL_FOLDER}/{page}")
