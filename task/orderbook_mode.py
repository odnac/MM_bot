# orderbook_mode.py
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from driver_utils import init_driver
from utils import clear_console


# -------------------------------------------------
#  호가 행(Row) 데이터 파싱
# -------------------------------------------------
def parse_rows(rows):
    prices, amounts = [], []
    for row in rows:
        try:
            price = (
                row.find_element(By.CSS_SELECTOR, ".col-price")
                .text.strip()
                .replace(",", "")
            )
            amount = (
                row.find_element(By.CSS_SELECTOR, ".col-amount")
                .text.strip()
                .replace(",", "")
            )
            if price and amount and price != "-" and amount != "-":
                prices.append(float(price))
                amounts.append(float(amount))
        except Exception:
            continue
    return prices, amounts


# -------------------------------------------------
#  VictoriaEX 현재가(Last Price) 가져오기
# -------------------------------------------------
def get_victoria_last_price(driver) -> float:
    price_text = (
        driver.find_element(
            By.CSS_SELECTOR, "div.overturn-cell.col-price span.contrast"
        )
        .text.strip()
        .replace(",", "")
    )
    return float(price_text)


# -------------------------------------------------
#  VictoriaEX 호가창 스냅샷 가져오기
# -------------------------------------------------
def fetch_victoria_orderbook_snapshot(driver):
    ask_rows = driver.find_elements(
        By.CSS_SELECTOR, "#mCSB_2_container > a.bidding-table-rows"
    )
    bid_rows = driver.find_elements(
        By.CSS_SELECTOR, "#mCSB_3_container > a.bidding-table-rows"
    )

    ask_prices, ask_amounts = parse_rows(ask_rows)
    bid_prices, bid_amounts = parse_rows(bid_rows)

    coin_name = driver.find_element(By.CSS_SELECTOR, "b.pair-title").text.strip()
    ticker_text = driver.find_element(By.CSS_SELECTOR, "span.unit").text.strip()
    coin_ticker = ticker_text.replace("/USDT", "")

    # 데이터 부족하면 None 반환(호출부에서 continue)
    if len(ask_prices) < 10 or len(bid_prices) < 10:
        return None

    asks_sorted = sorted(zip(ask_prices, ask_amounts), reverse=True)
    bids_sorted = sorted(zip(bid_prices, bid_amounts), reverse=True)

    asks = asks_sorted[-10:]  # 낮은 매도 10개
    bids = bids_sorted[:10]  # 높은 매수 10개

    last_price = get_victoria_last_price(driver)

    return coin_name, coin_ticker, last_price, asks, bids


# -------------------------------------------------
#  콘솔 출력 함수
# -------------------------------------------------
def print_orderbook(coin_name, coin_ticker, last_price, asks, bids):

    print(f"┌───────────── {time.strftime('%H:%M:%S')}  {coin_ticker} ─────────────┐")

    print("")
    for i, (price, amount) in enumerate(asks[:10], 1):
        print(f" {11 - i:2d}호가 │ {price:>14,.8f} │ {amount:>14,.8f}")
    print("                 🟦 Asks")

    print(f"\n        💎 Last Price │ {last_price:>14,.8f}")

    print("\n                 🔴 Bids")
    for i, (price, amount) in enumerate(bids, 1):
        print(f" {i:2d}호가 │ {price:>14,.8f} │ {amount:>14,.8f}")

    print("\n└" + "─" * 41 + "┘\n")


# -------------------------------------------------
#  실시간 호가창 루프 (Mode 1)
# -------------------------------------------------
def run_victoria_orderbook_mode(victoria_url: str, refresh_interval: float = 10):

    driver = init_driver()

    try:
        driver.get(f"{victoria_url}/account/login")

        print("\n" + "=" * 45)
        print("         💎 Connected to VictoriaEX 💎")
        print("  Press Enter after logging in to continue.")
        print("=" * 45 + "\n")
        input()

        driver.get(f"{victoria_url}/trade")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.bidding-table-rows"))
        )

        print("\n[Mode 1] Show VictoriaEX Order Book\n\n")

        while True:
            try:
                snapshot = fetch_victoria_orderbook_snapshot(driver)
                if snapshot is None:
                    time.sleep(0.5)
                    continue

                coin_name, coin_ticker, last_price, asks, bids = snapshot
                clear_console()
                print_orderbook(coin_name, coin_ticker, last_price, asks, bids)

                time.sleep(refresh_interval)

            except KeyboardInterrupt:
                print("\nStopped by user. Returning to menu...")
                return

            except Exception as e:
                print(f"[WARN] Order book error: {type(e).__name__} - {e}")
                time.sleep(1)

    finally:
        driver.quit()
        print("Driver shutdown complete.")
