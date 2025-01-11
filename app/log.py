import logging
from logging.handlers import RotatingFileHandler


def setup_logger(name: str, log_file: str = "app.log", console_level=logging.INFO):
    """
    Sets up a logger with both file and console handlers.

    :param name: Name of the logger (usually __name__).
    :param log_file: Name of the log file.
    :param console_level: Logging level for the console handler.
    :return: Configured logger.
    """
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Capture all levels for the logger

    # File handler (captures all log levels)
    file_handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(levelname)s %(asctime)s %(name)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)

    # Console handler (streams only INFO and higher levels)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_formatter)

    # Add handlers to the logger
    if not logger.hasHandlers():  # Avoid adding handlers multiple times
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
