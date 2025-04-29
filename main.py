import sys
import os
from udescjoinvilletteautil.log import Log
from PySide6.QtWidgets import QApplication, QMessageBox
from udescjoinvilletteaapp.tteaapp import IPApp
from udescjoinvilletteaview.languageselectionview import LanguageSelectionView
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSettings, QTimer
from udescjoinvilletteautil.pathconfig import PathConfig  
from udescjoinvilletteaview.splashscreen import SplashScreen

class AppLauncher:
    def __init__(self):
        self.logger = Log(log_file=Log.FILE)
        self.app = QApplication(sys.argv)
        self.splash = None
        self.main_window = None
        self.language_dialog = None
        # Configurar QSettings para arquivo .ini portátil
        self.settings = QSettings("config.ini", QSettings.Format.IniFormat)

    def start(self):
        """Inicia a aplicação"""
        try:
            self.logger.log_info("Aplicação iniciada com sucesso.")
            
            # Cria e exibe a splash screen
            self.splash = SplashScreen()
            self.splash.show()

            # Configura a aplicação após a splash aparecer
            QTimer.singleShot(0, self.check_language)
            
            # Executa o loop principal
            exit_code = self.app.exec()
            
            self.logger.log_info("Aplicação finalizada com sucesso.")
            sys.exit(exit_code)
            
        except Exception as e:
            self.handle_error(e)

    def check_language(self):
        """Verifica se é necessário exibir a tela de idioma"""
        try:
            # Verificar se o arquivo .ini existe e contém a configuração de idioma
            language = self.settings.value("Geral/idioma", None)
            config_file_exists = os.path.exists(self.settings.fileName())

            if not config_file_exists or not language:
                # Aguardar a conclusão da splash screen antes de mostrar a tela de idioma
                QTimer.singleShot(3000, self.show_language_selection)  # 3000 ms (animação)
            else:
                # Configurar janela principal diretamente
                self.setup_main_window()
            
        except Exception as e:
            self.handle_error(e)

    def show_language_selection(self):
        """Exibe a tela de seleção de idioma após a splash screen"""
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
        """Configura a janela principal e finaliza a splash screen"""
        try:
            if not self.main_window:
                # Cria a janela principal
                self.main_window = IPApp()
                # Passa a janela principal para a splash, que cuidará da exibição
                if self.splash and self.splash.isVisible():
                    self.splash.finish(self.main_window)
                else:
                    # Se a splash já foi fechada, mostra a janela principal diretamente
                    self.main_window.show()
                self.logger.log_info("Janela principal configurada")
            
        except Exception as e:
            self.handle_error(e)

    def on_language_selected(self):
        """Salva o idioma selecionado e prossegue para a janela principal"""
        try:
            selected_language = self.language_dialog.get_selected_language()
            if selected_language:
                self.settings.setValue("Geral/idioma", selected_language)
                self.settings.sync()  # Garantir que a configuração seja salva
                self.logger.log_info(f"Idioma selecionado: {selected_language}")
                
                # Configurar a janela principal
                self.setup_main_window()
            else:
                self.logger.log_warning("Nenhum idioma selecionado")
                self.on_language_cancel()
            
        except Exception as e:
            self.handle_error(e)

    def on_language_cancel(self):
        """Fecha a aplicação se a seleção de idioma for cancelada"""
        self.logger.log_info("Seleção de idioma cancelada, encerrando aplicação")
        if self.splash and self.splash.isVisible():
            self.splash.close()
        self.app.quit()
        sys.exit(0)

    def handle_error(self, exception):
        """Trata exceções e registra logs de erro"""
        self.logger.log_warning("Aplicação finalizada com erro.")
        self.logger.log_error_with_stack(exception)
        
        # Fecha a splash screen se ela estiver aberta
        if self.splash and self.splash.isVisible():
            self.splash.close()
            self.splash = None

        # Fecha a tela de idioma se estiver aberta
        if self.language_dialog and self.language_dialog.isVisible():
            self.language_dialog.close()
            self.language_dialog = None

        # Exibe mensagem de erro
        msg = QMessageBox()
        msg.setWindowIcon(QIcon(IPApp.ICON_PATH))
        msg.setWindowTitle("Erro")
        msg.setIcon(QMessageBox.Critical)
        msg.setText(f"A aplicação encontrou um erro fatal e será encerrada.\nErro: {str(exception)}")
        msg.setParent(self.main_window)
        msg.exec()

        self.app.quit()
        sys.exit(1)

def main():
    """Função principal"""
    launcher = AppLauncher()
    launcher.start()

if __name__ == "__main__":
    main()