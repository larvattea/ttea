import sys
import traceback

from PySide6.QtCore import QTranslator
from PySide6.QtWidgets import QApplication

from udescjoinvilletteaapp import AppConfig
from udescjoinvilletteacontroller import LanguageController, MainController
from udescjoinvilletteafactory import ViewFactory
from udescjoinvillettealog import Log
from udescjoinvilletteamodel import AppModel, Language
from udescjoinvilletteautil import MessageService, PathConfig
from udescjoinvilletteaview import MainView, SplashScreen


def show_critical_error(exception: Exception, translator=None):
    Log.get_log().log_error_with_stack(exception)

    message = (
        "Ocorreu um erro crítico e a aplicação será encerrada.\n\n"
        f"Erro: {exception}\n\n"
        "Contate o suporte com o arquivo de log."
    )

    try:
        app = QApplication.instance() or QApplication(sys.argv)
        if translator:
            app.installTranslator(translator)
        MessageService.critical_global(message)
    except Exception as e:
        Log.get_log().log_error(f"Falha ao exibir erro crítico: {e}")


def global_exception_hook(
    exctype: type, value: Exception, traceback_obj: traceback
):
    Log.get_log().log_error_with_stack(value, traceback_obj=traceback_obj)
    translator = QTranslator()
    if translator.load(PathConfig.translation("pt_BR.qm")):
        QApplication.instance().installTranslator(translator)
    show_critical_error(value, translator)
    sys.__excepthook__(exctype, value, traceback_obj)
    sys.exit(1)


def main():
    sys.excepthook = global_exception_hook

    app = QApplication(sys.argv)
    app.setApplicationName(AppConfig.get_title())
    app.setApplicationVersion(AppConfig.VERSION)

    # ======================
    # SPLASH SCREEN (só até escolher idioma)
    # ======================
    splash = SplashScreen()
    splash.show()
    app.processEvents()  # força aparecer imediatamente
    splash.raise_()

    # === ESCOLHA DE IDIOMA ===
    language_controller = LanguageController(
        model=AppModel().language_model,
        language_view_factory=ViewFactory.get_app_view_factory().create_language_view,
    )

    # FECHA O SPLASH IMEDIATAMENTE APÓS O USUÁRIO ESCOLHER (ou cancelar)
    splash.finish(language_controller.view)

    # Aqui acontece a mágica:
    result = language_controller.view.exec()

    if result == 0:  # Cancelou
        sys.exit(0)

    selected_lang = language_controller.view.get_checked_language()

    # Aplica o idioma escolhido
    translator = QTranslator()
    if not translator.load(PathConfig.translation(f"{selected_lang}.qm")):
        translator.load(
            PathConfig.translation(f"{Language.DEFAULT_LANGUAGE}.qm")
        )
    app.installTranslator(translator)

    # === JANELA PRINCIPAL ===
    model = AppModel()
    model.current_language = selected_lang

    main_view = MainView()
    main_view.show()  # ← Mostra direto, sem splash nenhum agora

    message_service = MessageService(main_view)

    _ = MainController(
        view=main_view, model=model, message_service=message_service
    )

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
