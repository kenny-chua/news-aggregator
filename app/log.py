import logging
from logging.handlers import RotatingFileHandler


class LoggerSingleton:
    _instances = {}  # Dictionary to store singleton logger instances

    @staticmethod
    def get_logger(name: str, log_file: str = "app.log", console_level=logging.INFO):
        """
        Retrieves or creates a singleton logger instance.

        :param name: Name of the logger (e.g., __name__).
        :param log_file: Name of the log file.
        :param console_level: Logging level for the console handler.
        :return: Singleton logger instance.
        """
        if name not in LoggerSingleton._instances:
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)  # Capture all log levels

            # File handler
            file_handler = RotatingFileHandler(
                log_file, maxBytes=5_000_000, backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                "%(levelname)s %(asctime)s %(name)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(file_formatter)

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(console_level)
            console_formatter = logging.Formatter("%(levelname)s: %(message)s")
            console_handler.setFormatter(console_formatter)

            if not logger.hasHandlers():  # Prevent duplicate handlers
                logger.addHandler(file_handler)
                logger.addHandler(console_handler)

            LoggerSingleton._instances[name] = logger

        return LoggerSingleton._instances[name]

    @staticmethod
    def set_log_level(name: str, level: int):
        """
        Dynamically update the log level for a specific logger.

        :param name: Name of the logger.
        :param level: New log level (e.g., logging.DEBUG, logging.INFO).
        """
        logger = LoggerSingleton.get_logger(name)
        logger.setLevel(level)
        for handler in logger.handlers:
            handler.setLevel(level)

    @staticmethod
    def reset_logger(name: str):
        """
        Removes a logger and its handlers from the singleton registry.

        :param name: Name of the logger to reset.
        """
        if name in LoggerSingleton._instances:
            logger = LoggerSingleton._instances.pop(name)
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
                handler.close()
