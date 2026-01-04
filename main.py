import sys
import traceback

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QDialog

from udescjoinvilletteaapp import AppConfig
from udescjoinvilletteafactory import ViewFactory
from udescjoinvillettealog import Log
from udescjoinvilletteamodel import AppModel
from udescjoinvilletteaservice import LanguageService
from udescjoinvilletteautil import MessageService
from udescjoinvilletteaview import SplashScreen


def show_critical_error(exception: Exception):
    message = QCoreApplication.translate(
        "Main",
        "Ocorreu um erro inesperado e o aplicativo será encerrado.\n"
        "Por favor, entre em contato com o suporte e envie o arquivo de log.\n"
        "Detalhes do erro: {0}",
    ).format(str(exception))

    MessageService.critical_global(message, None)


def global_exception_hook(
    exctype: type, value: Exception, traceback_obj: traceback
):
    Log.get_log().log_error("Untreated global exception")
    Log.get_log().log_error_with_stack(value, traceback_obj=traceback_obj)
    show_critical_error(value)
    sys.__excepthook__(exctype, value, traceback_obj)
    sys.exit(1)


def main():
    sys.excepthook = global_exception_hook
    Log.get_log().log_info("Application started successfully.")

    app = QApplication(sys.argv)
    app.setApplicationName(AppConfig.get_title())
    app.setApplicationVersion(AppConfig.VERSION)
    app.setWindowIcon(QIcon(AppConfig.ICON_APP))

    # === Detecta idioma inicial e aplica ===
    language_service = LanguageService()
    initial_lang = language_service.get_initial_language()
    language_service.preview_language(initial_lang)
    # selected_lang = initial_lang

    # ======================
    # SPLASH SCREEN
    # ======================
    splash = SplashScreen()
    splash.show()
    app.processEvents()
    splash.raise_()

    # if not AppConfig.config_file_exists():
    # === Tela de escolha de idioma ===
    language_view = ViewFactory.get_app_view_factory().create_language_view()

    # === Aplica o idioma inicial como preview ===
    language_view.controller.service.preview_language(initial_lang)
    language_view.retranslateUi(language_view)  # força tradução imediata

    splash.finish(language_view)

    result = language_view.exec()

    if result == QDialog.DialogCode.Rejected:
        sys.exit(0)

    selected_lang = language_view.get_selected_language() or initial_lang

    if selected_lang != initial_lang:
        language_service.apply_language(selected_lang)
    # else:
    #    splash.finish(None)

    # === Inicializa o app model e menu da aplicação ===
    model = AppModel.get_instance()
    model.current_language = selected_lang

    main_view = ViewFactory.get_app_view_factory().create_main_view()
    main_view.show()

    Log.get_log().log_info("Application finished successfully.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
