import sys
from udescjoinvilleiputil.log import Log
from PySide6.QtWidgets import QApplication, QMessageBox
from udescjoinvilleipapp.ipapp import IPApp
from udescjoinvilleipview.splashscreen import SplashScreen
from PySide6.QtCore import QTimer

class AppLauncher:
    def __init__(self):
        self.logger = Log(log_file=Log.FILE)
        self.app = QApplication(sys.argv)
        self.splash = None
        self.main_window = None

    def start(self):
        """Inicia a aplicação"""
        try:
            self.logger.log_info("Aplicação iniciada com sucesso.")
            
            # Cria e exibe a splash screen
            self.splash = SplashScreen()
            self.splash.show()
            
            # Configura a aplicação após a splash aparecer
            QTimer.singleShot(0, self.setup_application)
            
            # Executa o loop principal
            exit_code = self.app.exec()
            
            self.logger.log_info("Aplicação finalizada com sucesso.")
            sys.exit(exit_code)
            
        except Exception as e:
            self.handle_error(e)

    def setup_application(self):
        """Configura a janela principal, mas não a exibe ainda"""
        try:
            if not self.main_window:
                # Cria a janela principal sem exibi-la
                self.main_window = IPApp()
                # Passa a janela principal para a splash, que cuidará da exibição
                self.splash.finish(self.main_window)
                self.logger.log_info("Janela principal configurada, aguardando o término da splash")
            
        except Exception as e:
            self.handle_error(e)

    def handle_error(self, exception):
        """Trata exceções e registra logs de erro"""
        self.logger.log_warning("Aplicação finalizada com erro.")
        self.logger.log_error_with_stack(exception)
        
        # Exibe mensagem de erro
        QMessageBox.critical(None, "Erro", 
                           f"A aplicação encontrou um erro fatal e será encerrada.\nErro: {str(exception)}")
        self.app.quit()
        sys.exit(1)

def main():
    """Função principal"""
    launcher = AppLauncher()
    launcher.start()

if __name__ == "__main__":
    main()