"""Logging utilities for the T-TEA Qt application.

This module provides the singleton ``Log`` class for application
diagnostics: rotating file logging, system and Python environment
information, and exception stack trace reporting.
"""

import importlib.metadata
import json
import logging
import os
import platform
import sys
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, Optional

import psutil

from ttea.util import PathConfig


class Log:
    """Logging manager for application diagnostics and exceptions.

    This singleton class configures a rotating log file handler and
    provides methods to record informational events, warnings and
    errors. It also collects system and Python environment data for
    richer diagnostics.

    Parameters
    ----------
    log_file : str | None, optional
        Path to the log file. Default is None, which uses
        ``LOG_FILE_PATH``.
    log_level : int, optional
        Logging level of the logger and of the file handler, such as
        ``logging.DEBUG`` or ``logging.INFO``. Default is
        ``logging.DEBUG``.

    Attributes
    ----------
    LOG_FILE_NAME : str, class attribute
        Default log file name (``"tteaapp.log"``).
    LOG_FILE_PATH : str, class attribute
        Default log file path, resolved by ``PathConfig.log`` when the
        module is imported.
    _instance : Log | None, class attribute
        Cached singleton instance.
    log_file : str
        Path of the log file in use.
    logger : logging.Logger
        The ``"Log"`` logger that receives all messages.

    Methods
    -------
    get_log()
        Retrieve the singleton Log instance.
    ensure_log_directory_exists()
        Create the log directory if necessary.
    get_system_info()
        Return system and hardware diagnostics.
    get_python_info()
        Return Python environment diagnostics.
    log_system_info()
        Write system and Python environment information to the log.
    log_error_with_stack(exception, variables=None, traceback_obj=None)
        Log exceptions with stack traces and optional context.
    log_info(message)
        Write an informational message to the log.
    log_warning(message)
        Write a warning message to the log.
    log_error(message)
        Write an error message to the log.

    Notes
    -----
    ``__new__`` always returns the same instance, but Python still runs
    ``__init__`` on every ``Log(...)`` call: each call reconfigures the
    shared instance (file, level and handler). Use ``get_log()`` to
    reuse the instance without reconfiguring it.

    On initialization the log directory is created if missing, existing
    handlers of the ``"Log"`` logger are removed to avoid duplicate
    output, and a ``RotatingFileHandler`` is added (10 MiB per file,
    5 backups, format ``"%(asctime)s - %(levelname)s - %(message)s"``
    with dates as ``%Y-%m-%d %H:%M:%S``). The message
    ``"Log instance initialized."`` is then written at INFO level.
    """

    LOG_FILE_NAME = "tteaapp.log"
    LOG_FILE_PATH = PathConfig.log(LOG_FILE_NAME)
    _instance = None

    def __new__(cls, *args: tuple, **kwargs: dict) -> "Log":
        """Return the singleton instance, creating it on the first call.

        Parameters
        ----------
        *args : tuple
            Positional arguments; ignored here (Python passes them to
            ``__init__``).
        **kwargs : dict
            Keyword arguments; ignored here (Python passes them to
            ``__init__``).

        Returns
        -------
        Log
            The singleton instance of the Log class.
        """
        if cls._instance is None:
            cls._instance = super(Log, cls).__new__(cls)
        return cls._instance

    def __init__(
        self, log_file: Optional[str] = None, log_level: int = logging.DEBUG
    ) -> None:
        # Use default file if none specified
        self.log_file = log_file if log_file else self.LOG_FILE_PATH
        # Ensure log directory exists
        self.ensure_log_directory_exists()
        # Configure logger
        self.logger = logging.getLogger("Log")
        self.logger.setLevel(log_level)
        # Clear existing handlers to avoid duplicates
        if self.logger.handlers:
            self.logger.handlers.clear()
        # Configure rotating file handler (10MB per file, keep 5 backups)
        file_handler = RotatingFileHandler(
            self.log_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        file_handler.setLevel(log_level)
        # Define log format
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        # Add handler to logger
        self.logger.addHandler(file_handler)
        self.logger.info("Log instance initialized.")

    @classmethod
    def get_log(cls) -> "Log":
        """Retrieve the singleton instance of the Log class.

        Returns
        -------
        Log
            The singleton instance of the Log class.

        Notes
        -----
        If no instance exists, a new one is created with default
        parameters. An existing instance is returned as is, without
        reconfiguration.
        """
        if cls._instance is None:
            cls._instance = Log()
        return cls._instance

    def ensure_log_directory_exists(self) -> None:
        """Create the log file directory if it does not exist.

        Notes
        -----
        Uses ``os.makedirs`` on the directory of the absolute path of
        ``log_file``, creating intermediate directories as needed.
        """
        log_dir = os.path.dirname(os.path.abspath(self.log_file))
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def get_system_info(self) -> Dict[str, str]:
        """Retrieve system, hardware and memory information.

        Returns
        -------
        dict[str, str]
            Information keyed by ``"OS"``, ``"OS Version"``,
            ``"Machine"``, ``"Processor"``, ``"CPU Cores"``,
            ``"Memory Total (GB)"``, ``"Memory Used by App (MB)"`` and
            ``"Timestamp"``.

        Notes
        -----
        Despite the annotation, not every value is a string:
        ``"CPU Cores"`` is the logical core count from ``psutil``
        (an int, or None if undetermined) and the memory values are
        floats rounded to 2 decimals. ``"Memory Total (GB)"`` is the
        total physical memory divided by 1024**3; ``"Memory Used by App
        (MB)"`` is the resident set size (RSS) of the current process
        divided by 1024**2. ``"Timestamp"`` uses ``%Y-%m-%d %H:%M:%S``.
        """
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        info = {
            "OS": platform.system(),
            "OS Version": platform.version(),
            "Machine": platform.machine(),
            "Processor": platform.processor(),
            "CPU Cores": psutil.cpu_count(logical=True),
            "Memory Total (GB)": round(
                psutil.virtual_memory().total / (1024**3), 2
            ),
            "Memory Used by App (MB)": round(memory_info.rss / (1024**2), 2),
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        return info

    def get_python_info(self) -> Dict[str, str]:
        """Retrieve Python and installed package information.

        Returns
        -------
        dict[str, str]
            Information keyed by ``"Python Version"`` (``sys.version``),
            ``"Python Executable"`` (``sys.executable``) and
            ``"Installed Packages"``.

        Notes
        -----
        Installed packages come from ``importlib.metadata``,
        formatted as ``"name==version"``, sorted alphabetically and
        joined with ``", "``. If none is found the value is
        ``"No packages found"``.
        """
        # Get installed packages
        packages = sorted(
            [
                f"{dist.metadata['Name']}=={dist.version}"
                for dist in importlib.metadata.distributions()
            ]
        )
        packages_str = ", ".join(packages) if packages else "No packages found"
        info = {
            "Python Version": sys.version,
            "Python Executable": sys.executable,
            "Installed Packages": packages_str,
        }
        return info

    def log_system_info(self) -> None:
        """Write system and Python environment information to the log.

        Notes
        -----
        Writes a header line followed by each key-value pair of
        ``get_system_info()`` and of ``get_python_info()``, all at INFO
        level.
        """
        # Log system information
        self.logger.info("System Information:")
        system_info = self.get_system_info()
        for key, value in system_info.items():
            self.logger.info("%s: %s", key, value)
        # Log Python environment information
        self.logger.info("Python Environment Information:")
        python_info = self.get_python_info()
        for key, value in python_info.items():
            self.logger.info("%s: %s", key, value)

    def log_error_with_stack(
        self,
        exception: Exception,
        variables: Optional[Dict[str, Any]] = None,
        traceback_obj: Optional[Any] = None,
    ) -> None:
        """Log an error with stack trace and diagnostic context.

        Parameters
        ----------
        exception : Exception
            The exception to log.
        variables : dict[str, Any] | None, optional
            Variables to include in the log output. Default is None.
        traceback_obj : Any | None, optional
            Traceback object to format. If None, the traceback of the
            exception currently being handled is used. Default is None.

        Notes
        -----
        Everything is written at ERROR level, in this order:

        1. ``variables``, if given, each value serialized with
           ``json.dumps(indent=2, default=str)``;
        2. the local variables of the caller's frame
           (``sys._getframe(1)``), skipping names that start with
           ``__``, serialized the same way;
        3. ``get_system_info()`` and ``get_python_info()``;
        4. ``str(exception)`` and the execution stack.

        With ``traceback_obj`` the stack comes from
        ``traceback.format_tb``; otherwise from
        ``traceback.format_exc``, so call it inside the ``except``
        block. Outside it, ``format_exc`` returns ``"NoneType: None"``
        and that is what gets logged.
        """
        # Log provided variables if any
        if variables:
            self.logger.error("Provided variables at the time of error:")
            for key, value in variables.items():
                formatted_value = json.dumps(value, indent=2, default=str)
                self.logger.error("%s: %s", key, formatted_value)
        # Capture local variables from the caller's frame
        caller_frame = sys._getframe(1)
        local_vars = caller_frame.f_locals
        if local_vars:
            self.logger.error("Local variables at the time of error:")
            for key, value in local_vars.items():
                # Filters Python built-in variables (starting with '__')
                if not key.startswith("__"):
                    formatted_value = json.dumps(value, indent=2, default=str)
                    self.logger.error("%s: %s", key, formatted_value)
        # System Information
        self.logger.error("Error detected. System information:")
        system_info = self.get_system_info()
        for key, value in system_info.items():
            self.logger.error("%s: %s", key, value)
        # Python information
        self.logger.error("Python Environment Information:")
        python_info = self.get_python_info()
        for key, value in python_info.items():
            self.logger.error("%s: %s", key, value)
        # Error message and stack trace
        self.logger.error("Exception: %s", str(exception))
        if traceback_obj:
            stack_trace = "".join(traceback.format_tb(traceback_obj))
            self.logger.error("Execution stack:\n%s", stack_trace)
        else:
            stack_trace = traceback.format_exc()
            self.logger.error(
                "Execution stack:\n%s",
                stack_trace if stack_trace else "No stack trace available",
            )

    def log_info(self, message: str) -> None:
        """Log an informational message.

        Parameters
        ----------
        message : str
            The message to log at the INFO level.
        """
        self.logger.info(message)

    def log_warning(self, message: str) -> None:
        """Log a warning message.

        Parameters
        ----------
        message : str
            The message to log at the WARNING level.
        """
        self.logger.warning(message)

    def log_error(self, message: str) -> None:
        """Log an error message.

        Parameters
        ----------
        message : str
            The message to log at the ERROR level.
        """
        self.logger.error(message)
