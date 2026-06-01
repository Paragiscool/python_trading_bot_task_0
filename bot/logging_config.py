import logging
import os
from logging.handlers import RotatingFileHandler

# Path to the logs directory in the project directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Ensure logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FILE_PATH = os.path.join(LOGS_DIR, "trading_bot.log")

def setup_logging():
    """Sets up standard logging for the application.
    Logs to a rotating file and optional console handler.
    """
    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.DEBUG)

    # Prevent duplicating handlers
    if logger.hasHandlers():
        return logger

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # File handler (10MB max size, keeping up to 5 backups)
    file_handler = RotatingFileHandler(
        LOG_FILE_PATH, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler for CLI warnings/errors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

logger = setup_logging()
