import sys
from udescjoinvilleiputil.log import Log
from PySide6.QtWidgets import QApplication, QMessageBox
from udescjoinvilleipapp.ipapp import IPApp
from udescjoinvilleipview.splashscreen import SplashScreen

# Função principal
def main():
    try:
        logger = Log(log_file=Log.FILE)
        logger.log_info("Aplicação iniciada com sucesso.")
        app = QApplication(sys.argv)
        splash = SplashScreen()
        splash.show()
        sys.exit(app.exec())
        #ipapp = IPApp()
        #ipapp.show()
        #app.exec()   
        #logger.log_info("Aplicação finalizada com sucesso.")
    except Exception as e:
        logger.log_warning("Aplicação finalizada com erro.")
        logger.log_error_with_stack(e)
        QMessageBox().critical(None, "Erro", "A aplicação encontrou um erro fatal e será encerrada.")

if __name__ == "__main__":
    main()