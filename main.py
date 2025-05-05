import os
import sys

from PySide6.QtCore import QSettings, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton

from udescjoinvilletteaapp.tteaapp import TTeaApp
from udescjoinvilletteaview.languageselectionview import LanguageSelectionView
from udescjoinvilletteaview.splashscreen import SplashScreen
from udescjoinvilletteautil.log import Log
from udescjoinvilletteautil.pathconfig import PathConfig


class AppLauncher:
    def __init__(self):
        self.logger = Log(log_file=Log.FILE)
        self.app = QApplication(sys.argv)
        self.splash = None
        self.main_window = None
        self.language_dialog = None
        self.settings = QSettings("config.ini", QSettings.IniFormat)
        self._has_error = False

    def start(self):
        """Inicia a aplicação."""
        try:
            self.logger.log_info("Aplicação iniciada com sucesso.")
            self.splash = SplashScreen()
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
            language = self.settings.value("Geral/idioma", None)
            config_file_exists = os.path.exists(self.settings.fileName())
            if not config_file_exists or not language:
                QTimer.singleShot(3000, self.show_language_selection)
            else:
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
            self.language_dialog = LanguageSelectionView()
            self.language_dialog.accepted.connect(self.on_language_selected)
            self.language_dialog.rejected.connect(self.on_language_cancel)
            self.language_dialog.show()
            self.logger.log_info("Exibindo tela de seleção de idioma")
        except Exception as e:
            self.handle_error(e)

    def setup_main_window(self):
        """Configura a janela principal e finaliza a splash screen."""
        if self._has_error:
            return
        try:
            if not self.main_window:
                self.main_window = TTeaApp()
                if self.splash and self.splash.isVisible():
                    self.splash.finish(self.main_window)
                else:
                    self.main_window.show()
                self.logger.log_info("Janela principal configurada")
        except Exception as e:
            self.handle_error(e)

    def on_language_selected(self):
        """Salva o idioma selecionado e prossegue para a janela principal."""
        if self._has_error:
            return
        try:
            selected_language = self.language_dialog.get_selected_language()
            if selected_language:
                self.settings.setValue("Geral/idioma", selected_language)
                self.settings.sync()
                self.logger.log_info(f"Idioma selecionado: {selected_language}")
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
        if self.splash and self.splash.isVisible():
            self.splash.close()
            self.splash = None
        if self.language_dialog and self.language_dialog.isVisible():
            self.language_dialog.close()
            self.language_dialog = None
        if self.main_window and self.main_window.isVisible():
            self.main_window.close()
            self.main_window = None

    def handle_error(self, exception):
        """Trata exceções, fecha janelas e exibe mensagem de erro."""
        if self._has_error:
            return # Evita chamadas recursivas ou repetidas
        self._has_error = True
        self.logger.log_warning("Aplicação finalizada com erro.")
        self.logger.log_error_with_stack(exception)
        self.close_all_windows()
        msg = QMessageBox()
        msg.setWindowIcon(QIcon(TTeaApp.ICON_APP))
        msg.setWindowTitle(TTeaApp.TITLE)
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Ocorreu um erro inesperado e a aplicação será encerrada.\n"
                    "Por favor, contate o suporte.\n" \
                    f"Detalhes do erro: {str(exception)}")

        msg.exec()
        self.app.quit()
        sys.exit(1)


def main():
    """Função principal."""
    launcher = AppLauncher()
    launcher.start()


if __name__ == "__main__":
    main()