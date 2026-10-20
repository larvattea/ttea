"""Help window: contents, index and search beside a web view.

The pages come from the compiled help (.qch) through the ``qthelp://``
scheme served by HelpSchemeHandler.

Notes
-----
This module imports Qt WebEngine. It is not exported by ``ttea.view``
and is imported only when the help is opened, so the rest of the
application starts without loading Qt WebEngine.
"""

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QAction, QCloseEvent, QDesktopServices, QKeySequence
from PySide6.QtHelp import QHelpEngine
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QLineEdit,
    QMainWindow,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ttea.util.helpschemehandler import HelpSchemeHandler


class _HelpPage(QWebEnginePage):
    """Web page that opens external links in the system browser.

    Attributes
    ----------
    EXTERNAL_SCHEMES : tuple[str, ...], class attribute
        URL schemes opened outside the help (http, https, mailto).
    """

    EXTERNAL_SCHEMES = ("http", "https", "mailto")

    def acceptNavigationRequest(
        self,
        url: QUrl,
        navigation_type: QWebEnginePage.NavigationType,
        is_main_frame: bool,
    ) -> bool:
        """Send external links to the browser, keep help links here."""
        if url.scheme() in self.EXTERNAL_SCHEMES:
            QDesktopServices.openUrl(url)
            return False
        return super().acceptNavigationRequest(
            url, navigation_type, is_main_frame
        )


class HelpView(QMainWindow):
    """Window that shows the help of one language.

    Parameters
    ----------
    engine : QHelpEngine
        Help engine of ``language``. The window takes ownership.
    language : str
        Language code of the help shown.
    home_url : QUrl
        URL of the home page.
    parent : QWidget | None, optional
        Owner window. While a modal dialog is open, the help must be a
        child of it, otherwise Qt blocks the help window.

    Attributes
    ----------
    language : str
        Language code of the help shown. A new window is needed when the
        application language changes.
    closed : Signal()
        Emitted when the user closes the window.
    engine : QHelpEngine
        Help engine; its parent is set to this window.
    web : QWebEngineView
        View of the help pages.
    tabs : QTabWidget
        Contents, index and search tabs.
    DEFAULT_SIZE : tuple[int, int], class attribute
        Initial window size in pixels.
    SIDEBAR_WIDTH : int, class attribute
        Initial width of the sidebar in pixels.

    Notes
    -----
    The window title and tab names are translated with ``self.tr()``.
    """

    closed = Signal()

    DEFAULT_SIZE = (1100, 720)
    SIDEBAR_WIDTH = 300

    def __init__(
        self,
        engine: QHelpEngine,
        language: str,
        home_url: QUrl,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent, Qt.WindowType.Window)
        self.engine = engine
        self.engine.setParent(self)
        self.language = language
        self._home_url = home_url

        HelpSchemeHandler.install(engine)

        self.setWindowTitle(self.tr("Ajuda - Plataforma T-TEA"))
        self.resize(*self.DEFAULT_SIZE)

        self.web = QWebEngineView(self)
        self.web.setPage(_HelpPage(self.web))

        self.tabs = QTabWidget(self)
        self.tabs.addTab(self._create_contents_tab(), self.tr("Sumário"))
        self.tabs.addTab(self._create_index_tab(), self.tr("Índice"))
        self.tabs.addTab(self._create_search_tab(), self.tr("Pesquisar"))

        splitter = QSplitter(self)
        splitter.addWidget(self.tabs)
        splitter.addWidget(self.web)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes(
            [self.SIDEBAR_WIDTH, self.DEFAULT_SIZE[0] - self.SIDEBAR_WIDTH]
        )
        self.setCentralWidget(splitter)

        self._create_toolbar()
        self.web.urlChanged.connect(self._on_url_changed)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def show_url(self, url: QUrl) -> None:
        """Show the page at ``url``."""
        self.web.setUrl(url)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Hide the window and notify the controller."""
        self.closed.emit()
        super().closeEvent(event)

    # ------------------------------------------------------------------
    # Sidebar tabs
    # ------------------------------------------------------------------
    def _create_contents_tab(self) -> QWidget:
        """Create the table of contents tab."""
        self.contents = self.engine.contentWidget()
        self.contents.setHeaderHidden(True)
        self.contents.linkActivated.connect(self.show_url)

        # The engine fills the model right after setup; expand the first
        # level when it is ready.
        model = self.engine.contentModel()
        model.contentsCreated.connect(lambda: self.contents.expandToDepth(0))
        if model.rowCount() > 0:
            self.contents.expandToDepth(0)
        return self.contents

    def _create_index_tab(self) -> QWidget:
        """Create the keyword index tab with a filter field."""
        index = self.engine.indexWidget()
        keyword = QLineEdit(self)
        keyword.setPlaceholderText(self.tr("Digite a palavra-chave"))
        keyword.setClearButtonEnabled(True)
        keyword.textChanged.connect(index.filterIndices)
        keyword.returnPressed.connect(index.activateCurrentItem)

        index.documentActivated.connect(
            lambda link, _keyword: self.show_url(link.url)
        )
        # A keyword with several pages opens the first one.
        index.documentsActivated.connect(
            lambda links, _keyword: links and self.show_url(links[0].url)
        )

        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.addWidget(keyword)
        layout.addWidget(index)
        return page

    def _create_search_tab(self) -> QWidget:
        """Create the full-text search tab."""
        search = self.engine.searchEngine()
        query = search.queryWidget()
        results = search.resultWidget()

        query.search.connect(lambda: search.search(query.searchInput()))
        results.requestShowLink.connect(self.show_url)
        search.indexingStarted.connect(
            lambda: self.statusBar().showMessage(
                self.tr("Preparando a pesquisa...")
            )
        )
        search.indexingFinished.connect(self.statusBar().clearMessage)
        # Incremental: only rebuilt when the help file changes.
        search.reindexDocumentation()

        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.addWidget(query)
        layout.addWidget(results, 1)
        return page

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def _create_toolbar(self) -> None:
        """Create the back, forward and home buttons."""
        toolbar = self.addToolBar(self.tr("Navegação"))
        toolbar.setMovable(False)

        self.act_back = QAction(self.tr("Voltar"), self)
        self.act_back.setShortcut(QKeySequence.StandardKey.Back)
        self.act_back.triggered.connect(self.web.back)

        self.act_forward = QAction(self.tr("Avançar"), self)
        self.act_forward.setShortcut(QKeySequence.StandardKey.Forward)
        self.act_forward.triggered.connect(self.web.forward)

        act_home = QAction(self.tr("Início"), self)
        act_home.triggered.connect(lambda: self.show_url(self._home_url))

        toolbar.addActions([self.act_back, self.act_forward, act_home])
        self._update_navigation()

    def _on_url_changed(self, url: QUrl) -> None:
        """Select the page in the contents and update the buttons."""
        index = self.contents.indexOf(url)
        if index.isValid():
            self.contents.setCurrentIndex(index)
        self._update_navigation()

    def _update_navigation(self) -> None:
        """Enable back and forward only when there is history."""
        history = self.web.history()
        self.act_back.setEnabled(history.canGoBack())
        self.act_forward.setEnabled(history.canGoForward())
