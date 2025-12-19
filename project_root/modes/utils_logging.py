# utils_logging.py
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime


def setup_logger(side: str) -> logging.Logger:
    logger = logging.getLogger(f"FollowMM_{side.upper()}")

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(
        log_dir, f"{side}_{datetime.now().strftime('%Y-%m-%d')}.log"
    )

    handler = TimedRotatingFileHandler(
        filename=log_file,
        when="midnight",
        interval=1,
        backupCount=0,
        encoding="utf-8",
    )

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.addHandler(console_handler)

    return logger
