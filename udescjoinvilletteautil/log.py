import logging
import platform
import psutil
import traceback
from datetime import datetime
from udescjoinvilletteautil.pathconfig import PathConfig
import os

# Classe para criar e gerenciar logs detalhados da aplicação.
class Log:

    FILE = PathConfig.log("ipapp.log")

    def __init__(self, log_file=None, log_level=logging.DEBUG):
        """Inicializa o logger com um arquivo e nível de log.

        Args:
            log_file (str): Nome do arquivo de log.
            log_level (int): Nível de log (ex.: logging.DEBUG, logging.INFO).
        """
         # Usa o arquivo padrão se nenhum for especificado
        self.log_file = log_file if log_file else self.FILE

        # Verifica e cria o diretório de log se não existir
        self._ensure_log_directory_exists()    

        # Configura o logger
        self.logger = logging.getLogger("Log")
        self.logger.setLevel(log_level)

        # Remove handlers existentes para evitar duplicatas
        if self.logger.handlers:
            self.logger.handlers.clear()

        # Configura o handler para arquivo
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)

        # Define o formato do log
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)

        # Adiciona o handler ao logger
        self.logger.addHandler(file_handler)

        # Registra informações iniciais do sistema ao criar o logger
        #self.log_system_info()

    def _ensure_log_directory_exists(self):
        """Verifica se o diretório do log existe e o cria se necessário."""
        log_dir = os.path.dirname(os.path.abspath(self.log_file))
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def get_system_info(self):
        """Retorna informações do sistema, hardware e memória."""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()

        info = {
            "OS": platform.system(),
            "OS Version": platform.version(),
            "Machine": platform.machine(),
            "Processor": platform.processor(),
            "CPU Cores": psutil.cpu_count(logical=True),
            "Memory Total (GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2),
            "Memory Used by App (MB)": round(memory_info.rss / (1024 ** 2), 2),
            "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return info

    def log_system_info(self):
        # Registra informações do sistema no log.
        system_info = self.get_system_info()
        self.logger.info("Informações do Sistema:")
        for key, value in system_info.items():
            self.logger.info(f"{key}: {value}")

    def log_error_with_stack(self, exception):
        """Registra um erro com a pilha de execução completa.

        Args:
            exception (Exception): Exceção capturada.
        """
        # Informações do sistema
        self.logger.error("Erro detectado. Informações do sistema:")
        system_info = self.get_system_info()
        for key, value in system_info.items():
            self.logger.error(f"{key}: {value}")

        # Mensagem de erro e stack trace
        self.logger.error(f"Exceção: {str(exception)}")
        stack_trace = traceback.format_exc()
        self.logger.error(f"Pilha de execução:\n{stack_trace}")

    def log_info(self, message):
        """Registra uma mensagem informativa.

        Args:
            message (str): Mensagem a ser registrada.
        """
        self.logger.info(message)

    def log_warning(self, message):
        """Registra um aviso.

        Args:
            message (str): Mensagem de aviso.
        """
        self.logger.warning(message)