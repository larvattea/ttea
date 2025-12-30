import sys
import traceback

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

from udescjoinvilletteaapp import AppConfig
from udescjoinvilletteacontroller import LanguageController, MainController
from udescjoinvilletteafactory import ViewFactory
from udescjoinvillettealog import Log
from udescjoinvilletteamodel import AppModel
from udescjoinvilletteaservice import LanguageService  # novo import
from udescjoinvilletteautil import MessageService
from udescjoinvilletteaview import MainView, SplashScreen


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

    # === CARREGA O IDIOMA O MAIS CEDO POSSÍVEL ===
    language_service = LanguageService()
    initial_lang = language_service.get_initial_language()
    # language_service.apply_language(initial_lang)

    # ======================
    # SPLASH SCREEN
    # ======================
    splash = SplashScreen()
    splash.show()
    app.processEvents()
    splash.raise_()

    # === Tela de escolha de idioma ===
    language_controller = LanguageController(
        model=AppModel().language_model,
        language_view_factory=ViewFactory.get_app_view_factory().create_language_view,
    )

    splash.finish(language_controller.view)

    result = language_controller.view.exec()

    if result == 0:
        sys.exit(0)

    selected_lang = language_controller.view.get_checked_language()

    # Se mudou o idioma, aplica o novo tradutor
    if selected_lang != initial_lang:
        language_service.apply_language(selected_lang)
        # O apply_language provavelmente já reinstala o tradutor correto

    # === Resto do app ===
    model = AppModel()
    model.current_language = selected_lang

    main_view = MainView()
    main_view.show()

    message_service = MessageService(main_view)

    _ = MainController(
        view=main_view, model=model, message_service=message_service
    )

    Log.get_log().log_info("Application finished successfully.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
