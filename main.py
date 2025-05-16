
import os
import sys
from PySide6.QtCore import QSettings, QTimer, QTranslator
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox
from udescjoinvilletteaapp.tteaapp import TTeaApp
from udescjoinvilletteautil.log import Log
from udescjoinvilletteautil.pathconfig import PathConfig
from udescjoinvilletteamodel.language import Language
from udescjoinvilletteaview.languageview import LanguageView
from udescjoinvilletteacontroller.languagecontroller import LanguageController
from udescjoinvilletteaview.splashscreen import SplashScreen

class AppLauncher:
    """Classe responsável por iniciar e gerenciar a aplicação."""
    
    GENERAL_LANGUAGE = "Geral/idioma"
    GENERAL_DATE_MASK = "Geral/data"

    def __init__(self):
        self.logger = Log(log_file=Log.FILE)
        self.app = QApplication(sys.argv)
        self.translator = QTranslator()
        self.language_model = Language()
        self.splash = None
        self.main_window = None
        self.language_view = None
        self.language_controller = None
        self.settings = QSettings(PathConfig.inifile("config.ini"), QSettings.IniFormat)
        self._has_error = False
        # Carrega o tradutor no início para garantir disponibilidade
        self._load_translator(self._get_initial_language())

    def _get_initial_language(self):
        """Determina o idioma inicial com base nas configurações ou sistema."""
        system_language = self.language_model.get_system_language().replace("-", "_")
        supported_languages = {lang["code"] for lang in self.language_model.get_languages()}
        default_language = system_language if system_language in supported_languages else Language.DEFAULT_LANGUAGE
        
        if os.path.exists(self.settings.fileName()):
            language = self.settings.value(self.GENERAL_LANGUAGE, None)
            if language in supported_languages:
                return language
        return default_language

    def _load_translator(self, language):
        """Carrega o tradutor para o idioma especificado com fallback robusto."""
        try:
            translation_file = PathConfig.translation(language + ".qm")
            self.logger.log_info(f"Tentando carregar tradução: {translation_file}")
            if os.path.exists(translation_file) and self.translator.load(translation_file):
                self.app.installTranslator(self.translator)
                self.logger.log_info(f"Tradução carregada: {language}")
            else:
                self.logger.log_warning(f"Arquivo de tradução não encontrado: {translation_file}")
                # Tenta carregar o idioma padrão como fallback
                if language != Language.DEFAULT_LANGUAGE:
                    translation_file = PathConfig.translation(Language.DEFAULT_LANGUAGE + ".qm")
                    if os.path.exists(translation_file) and self.translator.load(translation_file):
                        self.app.installTranslator(self.translator)
                        self.logger.log_info(f"Tradução padrão carregada: {Language.DEFAULT_LANGUAGE}")
                    else:
                        self.logger.log_warning(f"Arquivo de tradução padrão não encontrado: {translation_file}")
        except Exception as e:
            self.logger.log_error(f"Erro ao carregar tradução {language}: {str(e)}")

    def start(self):
        """Inicia a aplicação."""
        try:
            self.logger.log_info("Aplicação iniciada com sucesso.")
            self.splash = SplashScreen(self.translator)
            self.splash.show()
            QTimer.singleShot(0, self.check_language)
            exit_code = self.app.exec()
            self.logger.log_info("Aplicação finalizada com sucesso.")
            sys.exit(exit_code)
        except Exception as e:
            self.handle_error(e)

    def check_language(self):
        """Verifica se é necessário exibir a tela de idioma."""
        if self._has_error:
            return
        try:
            config_file_exists = os.path.exists(self.settings.fileName())
            language = self.settings.value(self.GENERAL_LANGUAGE, None)
            if not config_file_exists or not language:
                QTimer.singleShot(3000, self.show_language_selection)
            else:
                self._load_translator(language)
                self.setup_main_window()
        except Exception as e:
            self.handle_error(e)

    def show_language_selection(self):
        """Exibe a tela de seleção de idioma após a splash screen."""
        if self._has_error:
            return
        try:
            if self.splash and self.splash.isVisible():
                self.splash.close()
                self.splash = None
            view = LanguageView(self.translator)
            self.language_controller = LanguageController(self.language_model, view)
            self.language_view = view
            self.language_view.accepted.connect(self.on_language_selected)
            self.language_view.rejected.connect(self.on_language_cancel)
            self.language_view.show()
            self.logger.log_info("Exibindo tela de seleção de idioma")
        except Exception as e:
            self.handle_error(e)

    def setup_main_window(self):
        """Configura a janela principal e finaliza a splash screen."""
        if self._has_error:
            return
        try:
            if not self.main_window:
                self.main_window = TTeaApp(self.translator, self)
                if self.splash and self.splash.isVisible():
                    self.splash.finish(self.main_window)
                else:
                    self.main_window.show()
                self.logger.log_info("Janela principal configurada")
        except Exception as e:
            self.handle_error(e)

    def on_language_selected(self):
        """Salva o idioma selecionado, carrega tradução e prossegue para a janela principal."""
        if self._has_error:
            return
        try:
            selected_language = self.language_controller.get_selected_language()
            if selected_language:
                self.settings.setValue(self.GENERAL_LANGUAGE, selected_language)
                if selected_language == Language.DEFAULT_LANGUAGE: 
                    self.settings.setValue(self.GENERAL_DATE_MASK, "%d/%m/%Y") 
                else:
                   self.settings.setValue(self.GENERAL_DATE_MASK, "%m/%d/%Y")     
                
                self.settings.sync()
                self.logger.log_info(f"Idioma selecionado: {selected_language}")
                self._load_translator(selected_language)
                self.setup_main_window()
            else:
                self.logger.log_warning("Nenhum idioma selecionado")
                self.on_language_cancel()
        except Exception as e:
            self.handle_error(e)

    def on_language_cancel(self):
        """Fecha a aplicação se a seleção de idioma for cancelada."""
        if self._has_error:
            return
        self.logger.log_info("Seleção de idioma cancelada, encerrando aplicação")
        self.close_all_windows()
        self.app.quit()
        sys.exit(0)

    def close_all_windows(self):
        """Fecha todas as janelas abertas."""
        for window in (self.splash, self.language_view, self.main_window):
            if window and hasattr(window, "isVisible") and window.isVisible():
                window.close()
        self.splash = self.language_view = self.main_window = None

    def handle_error(self, exception):
        """Trata exceções, fecha janelas e exibe mensagem de erro."""
        if self._has_error:
            return
        self._has_error = True
        self.logger.log_warning("Aplicação finalizada com erro.")
        self.logger.log_error_with_stack(exception)
        self.close_all_windows()
        msg = QMessageBox()
        msg.setWindowIcon(QIcon(TTeaApp.ICON_APP))
        #msg.setWindowTitle(TTeaApp.TITLE)
        msg.setWindowTitle(TTeaApp.get_title())
        msg.setIcon(QMessageBox.Critical)
        # Tenta traduzir a mensagem de erro
        error_message = self.translator.translate(
            "AppLauncher",
            "Ocorreu um erro inesperado e a aplicação será encerrada.\n"
            "Por favor, contate o suporte.\n"
            "Detalhes do erro: {0}"
        ).format(str(exception))
        # Fallback para mensagem em texto puro se a tradução falhar
        if not error_message or error_message.isspace():
            error_message = (
                "Ocorreu um erro inesperado e a aplicação será encerrada.\n"
                "Por favor, contate o suporte.\n"
                f"Detalhes do erro: {str(exception)}"
            )
        msg.setText(error_message)
        msg.exec()
        self.app.quit()
        sys.exit(1)

def main():
    """Função principal para iniciar a aplicação."""
    launcher = AppLauncher()
    launcher.start()

if __name__ == "__main__":
    main()