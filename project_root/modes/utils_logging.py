# utils_logging.py
import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


def setup_logger(side: str):
    logger_name = f"mm_{side}"
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    log_file = os.path.join(LOG_DIR, f"mm_engine_{side}.log")
    file = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file)

    return logger
