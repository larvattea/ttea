import sys
from udescjoinvilleisurfaceutil.log import Log
from PySide6.QtWidgets import QMessageBox, QApplication 
from udescjoinvilleisurfaceapp.isurfaceapp import ISurfaceApp

# Função principal
def main():
    try:
        logger = Log(log_file=Log.FILE)
        logger.log_info("Aplicação iniciada com sucesso.")
        app = QApplication(sys.argv)
        isapp = ISurfaceApp()
        isapp.show()
        #resultado = 10/0
        app.exec()   
        logger.log_info("Aplicação finalizada com sucesso.")
    except Exception as e:
        logger.log_warning("Aplicação finalizada com erro.")
        logger.log_error_with_stack(e)
        QMessageBox().critical(None, "Erro", "A aplicação encontrou um erro fatal e será encerrada.")

if __name__ == "__main__":
    main()