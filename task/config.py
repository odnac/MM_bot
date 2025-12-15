# config.py
import os
from dotenv import load_dotenv

# -------------------------------------------------
#  .env 로드 및 환경 변수 관리
# -------------------------------------------------
load_dotenv()

CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH")
VICTORIA_URL = os.getenv("VICTORIA_URL")
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")


def get_env_float(key: str) -> float:
    value = os.getenv(key)
    if value is None:
        raise RuntimeError(f"[ENV ERROR] {key} is not set in .env")
    return float(value)


def get_env_int(key: str) -> int:
    value = os.getenv(key)
    if value is None:
        raise RuntimeError(f"[ENV ERROR] {key} is not set in .env")
    return int(value)


DISCOUNT_MIN = get_env_float("DISCOUNT_MIN")
DISCOUNT_MAX = get_env_float("DISCOUNT_MAX")
FOLLOW_UPDATE_SEC = get_env_int("FOLLOW_UPDATE_SEC")

ORDERBOOK_REFRESH_INTERVAL = 10  # seconds
