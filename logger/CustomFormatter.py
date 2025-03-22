import logging
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv
import os
import datetime

load_dotenv()

LOG_LEVEL = os.getenv('LOG_LEVEL','INFO')
LOG_FOLDER = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_FOLDER, exist_ok=True)

class CustomFormatter(logging.Formatter):
    cyan = "\x1b[36;20m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: cyan + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def get_logger(name: str, level=logging.INFO):
    logger = logging.getLogger(name)
    if not logger.handlers:  # Avoid duplicate handlers

        # Console handler (with colors)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(CustomFormatter())
        logger.addHandler(console_handler)

        # Get today's date in ISO 8601 format (YYYY-MM-DD)
        date_str = datetime.date.today().isoformat()
        log_file_path = os.path.join(LOG_FOLDER, f"{date_str}.log")

        # File handler with daily rotation (even if we don't auto-rotate here, keeps it flexible)
        file_handler = TimedRotatingFileHandler(
            log_file_path,
            when="midnight",   # Rotate at midnight
            interval=1,
            backupCount=7,     # Keep last 7 logs (optional)
            encoding='utf-8'
        )
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        logger.setLevel(level)

    return logger