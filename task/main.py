from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from orderbook_mode import run_victoria_orderbook_mode
from driver_utils import init_driver


import time
import os
import random
import requests

# -------------------------------------------------
#  환경 설정
# -------------------------------------------------
load_dotenv()  # .env 파일 로드
CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH")
VICTORIA_URL = os.getenv("VICTORIA_URL")
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

ORDERBOOK_REFRESH_INTERVAL = 10  # seconds


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


# -------------------------------------------------
#  드라이버 초기화
# -------------------------------------------------
def init_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    return driver


# -------------------------------------------------
#   Binance 가격 가져오기
# -------------------------------------------------
def get_binance_price(symbol: str) -> float:
    url = "https://api.binance.com/api/v3/ticker/price"
    r = requests.get(url, params={"symbol": symbol}, timeout=10)
    r.raise_for_status()
    return float(r.json()["price"])


# -------------------------------------------------
#   VictoriaEX 현재 심볼을 Binance 심볼로 변환
# -------------------------------------------------
def get_current_binance_symbol_from_victoria(driver) -> str:
    unit_text = driver.find_element(By.CSS_SELECTOR, "span.unit").text.strip()
    return unit_text.replace("/", "").upper()


# -------------------------------------------------
#  바이낸스 가격 추종 모드 (모드 2)
# -------------------------------------------------
def run_binance_referenced_mm_mode():
    driver = init_driver()

    try:
        driver.get(f"{VICTORIA_URL}/account/login")
        input("Login and press Enter to continue...")

        driver.get(f"{VICTORIA_URL}/trade")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "b.pair-title"))
        )

        print("\n[Mode 2] Binance-Referenced MM start..\n")

        while True:
            try:
                symbol = get_current_binance_symbol_from_victoria(driver)
                binance_price = get_binance_price(symbol)

                discount = random.uniform(DISCOUNT_MIN, DISCOUNT_MAX)
                target_price = binance_price * (1 - discount)

                print(
                    f"[{time.strftime('%H:%M:%S')}] Binance {symbol}={binance_price:.2f} | "
                    f"target(-{discount*100:.3f}%)={target_price:.2f}"
                )

                time.sleep(FOLLOW_UPDATE_SEC)

            except KeyboardInterrupt:
                print("\nStopped by user. Returning to menu...")
                return

    finally:
        driver.quit()
        print("Driver shutdown complete.")


# -------------------------------------------------
#  main() — 실행 시작점
# -------------------------------------------------
def main():

    print("\n" + "=" * 45)
    print("         💎 Connected to VictoriaEX 💎")
    print("  Press Enter after logging in to continue.")
    print("=" * 45 + "\n")
    input()

    while True:
        try:
            print("\n⚙️  Mode:")
            print("1) Show Order Book (VictoriaEX)")
            print("2) Binance-Referenced MM Mode")
            print("q) Quit")

            mode = input("\n👉  Select (1/2/q): ").strip().lower()

            if mode == "1":
                run_victoria_orderbook_mode(VICTORIA_URL, ORDERBOOK_REFRESH_INTERVAL)

            elif mode == "2":
                run_binance_referenced_mm_mode()

            elif mode == "q":
                print("Exiting...")
                break

            else:
                print("Invalid input. Please enter 1, 2, or q.")

        except KeyboardInterrupt:
            print("\nInterrupted. Returning to menu...")
            continue

    print("Driver shutdown complete.")


# -------------------------------------------------
# 프로그램 실행
# -------------------------------------------------
if __name__ == "__main__":
    main()
