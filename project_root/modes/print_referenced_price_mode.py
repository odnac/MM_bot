# referenced_mm_mode.py
import time
import random
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modes.driver_utils import init_driver
from modes.utils import clear_console
from modes.utils import wait_for_manual_login
from config import DISCOUNT_MIN, DISCOUNT_MAX, FOLLOW_UPDATE_SEC


def get_binance_price(symbol: str) -> float:
    url = "https://api.binance.com/api/v3/ticker/price"
    r = requests.get(url, params={"symbol": symbol}, timeout=10)
    r.raise_for_status()
    return float(r.json()["price"])


def get_current_binance_symbol_from_victoria(driver) -> str:
    unit_text = driver.find_element(By.CSS_SELECTOR, "span.unit").text.strip()
    return unit_text.replace("/", "").upper()


def print_binance_referenced_price_mode(VICTORIA_URL: str):

    driver = init_driver()

    try:
        driver.get(f"{VICTORIA_URL}/account/login")

        wait_for_manual_login(2)

        driver.get(f"{VICTORIA_URL}/trade")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "b.pair-title"))
        )

        while True:
            try:
                symbol = get_current_binance_symbol_from_victoria(driver)

                try:
                    binance_price = get_binance_price(symbol)

                except Exception as e:
                    print(f"[WARN] Binance API error: {type(e).__name__} - {e}")
                    time.sleep(1)
                    continue

                discount = random.uniform(DISCOUNT_MIN, DISCOUNT_MAX)
                target_price = binance_price * (1 - discount)

                clear_console()
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
