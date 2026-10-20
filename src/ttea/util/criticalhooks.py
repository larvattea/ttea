"""Global exception hook utilities for the T-TEA application.

This module installs hooks for uncaught exceptions in the main thread
and worker threads. It also shows an error dialog using translated
messages when Qt is available.
"""

import sys
import threading
from types import TracebackType

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication


class CriticalHooks:
    """Encapsulate global exception hooks for the application.

    This class registers handlers for uncaught exceptions in the main
    thread and worker threads, and displays a translated error dialog
    when Qt is available.

    Methods
    -------
    show_critical_error(exception)
        Display a translated critical error dialog for an exception.
    global_exception_hook(exctype, value, traceback_obj)
        Handle uncaught exceptions on the main thread.
    threading_exception_hook(args)
        Handle uncaught exceptions in worker threads.
    setup_exception_hooks()
        Register global exception hooks for the application.

    Notes
    -----
    The dialog text is translated at runtime with
    ``QCoreApplication.translate`` in the ``"CriticalHooks"`` context.
    """

    @staticmethod
    def show_critical_error(exception: BaseException) -> None:
        """Show a translated critical error dialog.

        Parameters
        ----------
        exception : BaseException
            The exception that caused the failure; its text is appended
            to the message.

        Notes
        -----
        The message (pt_BR source text) is translated at runtime with
        ``QCoreApplication.translate`` in the ``"CriticalHooks"``
        context and shown with ``MessageService.critical_global``. If
        the dialog cannot be displayed (e.g. Qt is not ready yet), the
        error is printed to standard output instead.
        """
        from ttea.util import MessageService

        message = QCoreApplication.translate(
            "CriticalHooks",
            "Ocorreu um erro inesperado e o aplicativo será encerrado.\n"
            "Por favor, entre em contato com o suporte e envie o arquivo de log.\n"
            "Detalhes do erro: {0}",
        ).format(str(exception))

        try:
            MessageService.critical_global(message, None)
        except Exception:
            # Fallback in case the dialog fails or Qt is not yet ready
            print("Critical error (failed to display dialogue): ", exception)

    @staticmethod
    def global_exception_hook(
        exctype: type[BaseException],
        value: BaseException,
        traceback_obj: TracebackType | None,
    ) -> None:
        """Handle uncaught exceptions on the main thread.

        Installed as ``sys.excepthook``.

        Parameters
        ----------
        exctype : type[BaseException]
            The exception class.
        value : BaseException
            The exception instance.
        traceback_obj : TracebackType | None
            The traceback object, if available.

        Notes
        -----
        The exception is written to the application log with its stack
        trace. The dialog is shown only if a QApplication instance
        exists; otherwise a message is printed. The default
        ``sys.__excepthook__`` then prints the traceback and the
        application exits with status 1.
        """
        from ttea.log import Log

        Log.get_log().log_error("Untreated global exception")
        Log.get_log().log_error_with_stack(value, traceback_obj=traceback_obj)

        # Qt widgets can only be created once a QApplication exists.
        if QApplication.instance() is not None:
            try:
                CriticalHooks.show_critical_error(value)
            except Exception:
                print("Critical error (failed to display dialogue).")
        else:
            print("Critical error before QApplication initialization:", value)

        sys.__excepthook__(exctype, value, traceback_obj)
        sys.exit(1)

    @staticmethod
    def threading_exception_hook(args: threading.ExceptHookArgs) -> None:
        """Handle uncaught exceptions in worker threads.

        Installed as ``threading.excepthook``.

        Parameters
        ----------
        args : threading.ExceptHookArgs
            Thread exception hook arguments.

        Notes
        -----
        This hook only logs the exception with its stack trace. It shows
        no dialog, to avoid thread safety issues with Qt widgets, and
        does not end the application.
        """
        from ttea.log import Log

        Log.get_log().log_error("Untreated exception in thread")
        Log.get_log().log_error_with_stack(
            args.exc_value, traceback_obj=args.exc_traceback
        )

    @staticmethod
    def setup_exception_hooks() -> None:
        """Register the global exception hooks for the application.

        Sets ``sys.excepthook`` to ``global_exception_hook`` and
        ``threading.excepthook`` to ``threading_exception_hook``.
        """
        sys.excepthook = CriticalHooks.global_exception_hook
        threading.excepthook = CriticalHooks.threading_exception_hook
