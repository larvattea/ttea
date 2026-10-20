"""Serve compiled help (.qch) pages to Qt WebEngine.

Qt WebEngine cannot read ``qthelp://`` URLs by itself. This module
registers the scheme and answers each request with the bytes stored in
the help collection, so pages, style sheets and images load directly
from the .qch file.

Notes
-----
This module imports QtWebEngineCore. Import it only where the help is
used, so the rest of the application does not load Qt WebEngine.
"""

from PySide6.QtCore import (
    QBuffer,
    QByteArray,
    QCoreApplication,
    QIODevice,
    QMimeDatabase,
    QObject,
    Qt,
    QUrl,
)
from PySide6.QtHelp import QHelpEngineCore
from PySide6.QtWebEngineCore import (
    QWebEngineProfile,
    QWebEngineUrlRequestJob,
    QWebEngineUrlScheme,
    QWebEngineUrlSchemeHandler,
)


class HelpSchemeHandler(QWebEngineUrlSchemeHandler):
    """Answer ``qthelp://`` requests with data from a help engine.

    Parameters
    ----------
    parent : QObject | None, optional
        Owner of the handler. It must live as long as the web
        profile. Default is None.

    Attributes
    ----------
    SCHEME : bytes, class attribute
        URL scheme served by this handler (``b"qthelp"``).
    _instance : HelpSchemeHandler | None, class attribute
        Handler shared by every ``install`` call.

    Methods
    -------
    register_scheme()
        Register the scheme. Call before creating the QApplication.
    install(engine)
        Serve the given help engine in the default web profile.
    """

    SCHEME = b"qthelp"

    _instance: "HelpSchemeHandler | None" = None

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._engine: QHelpEngineCore | None = None
        self._mime_db = QMimeDatabase()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------
    @staticmethod
    def register_scheme() -> None:
        """Register the ``qthelp`` scheme in Qt WebEngine.

        Qt requires both calls to happen before the QApplication is
        created.

        Notes
        -----
        Also sets ``Qt.AA_ShareOpenGLContexts``. The scheme uses the
        host syntax and is flagged secure, local and allowed to access
        local content.
        """
        QCoreApplication.setAttribute(
            Qt.ApplicationAttribute.AA_ShareOpenGLContexts
        )
        scheme = QWebEngineUrlScheme(HelpSchemeHandler.SCHEME)
        scheme.setSyntax(QWebEngineUrlScheme.Syntax.Host)
        scheme.setFlags(
            QWebEngineUrlScheme.Flag.SecureScheme
            | QWebEngineUrlScheme.Flag.LocalScheme
            | QWebEngineUrlScheme.Flag.LocalAccessAllowed
        )
        QWebEngineUrlScheme.registerScheme(scheme)

    @classmethod
    def install(cls, engine: QHelpEngineCore) -> "HelpSchemeHandler":
        """Serve ``engine`` through the default web profile.

        The handler is created once and reused; only the engine changes
        when the language changes.

        Parameters
        ----------
        engine : QHelpEngineCore
            Engine whose documentation will be served.

        Returns
        -------
        HelpSchemeHandler
            The shared handler.
        """
        profile = QWebEngineProfile.defaultProfile()
        if cls._instance is None:
            cls._instance = cls(QCoreApplication.instance())
            profile.installUrlSchemeHandler(cls.SCHEME, cls._instance)
        cls._instance._engine = engine
        return cls._instance

    # ------------------------------------------------------------------
    # Request handling
    # ------------------------------------------------------------------
    def requestStarted(self, job: QWebEngineUrlRequestJob) -> None:
        """Reply to a request with the file stored in the help engine.

        Parameters
        ----------
        job : QWebEngineUrlRequestJob
            Request made by the web view.

        Notes
        -----
        The request fails with ``UrlNotFound`` when the engine has no
        data for the URL (or no engine is installed yet).
        """
        data = self._file_data(job.requestUrl())
        if data.isEmpty():
            job.fail(QWebEngineUrlRequestJob.Error.UrlNotFound)
            return

        buffer = QBuffer(job)
        buffer.setData(data)
        buffer.open(QIODevice.OpenModeFlag.ReadOnly)
        job.reply(self._mime_type(job.requestUrl()), buffer)

    def _file_data(self, url: QUrl) -> QByteArray:
        """Return the file bytes for ``url``, or an empty array."""
        # The host part of the URL is the help namespace. URLs lowercase
        # the host, so the namespaces created by buildhelp.py are
        # lowercase too.
        if self._engine is None:
            return QByteArray()
        return self._engine.fileData(url)

    def _mime_type(self, url: QUrl) -> bytes:
        """Return the MIME type for ``url`` based on its extension.

        HTML, CSS and JavaScript are fixed; other types come from
        ``QMimeDatabase``.
        """
        path = url.path().lower()
        if path.endswith((".html", ".htm")):
            return b"text/html"
        if path.endswith(".css"):
            return b"text/css"
        if path.endswith(".js"):
            return b"text/javascript"
        mime = self._mime_db.mimeTypeForFile(
            url.path(), QMimeDatabase.MatchMode.MatchExtension
        )
        return mime.name().encode()
