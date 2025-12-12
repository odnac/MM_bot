import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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
#  콘솔 출력 함수
# -------------------------------------------------
def print_orderbook(coin_name, coin_ticker, asks, bids):
    print(f"┌───────────── {time.strftime('%H:%M:%S')}  {coin_ticker} ─────────────┐")

    print("\n            🟦 매도 호가 (Ask)\n")
    for i, (price, amount) in enumerate(asks[:10], 1):
        print(f" {11 - i:2d}호가 │ {price:>14,.8f} │ {amount:>14,.8f}")

    print("\n            🔴 매수 호가 (Bid)\n")
    for i, (price, amount) in enumerate(bids, 1):
        print(f" {i:2d}호가 │ {price:>14,.8f} │ {amount:>14,.8f}")

    print("\n└" + "─" * 41 + "┘\n")


# -------------------------------------------------
#  실시간 호가창 루프 (모드 1)
# -------------------------------------------------
def run_orderbook(driver, victoria_url: str, refresh_interval: float = 2.5):
    driver.get(f"{victoria_url}/trade")

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a.bidding-table-rows"))
    )

    while True:
        try:
            if not driver.window_handles:
                print("\n브라우저가 닫혔습니다. 프로그램을 종료합니다.")
                break

            ask_rows = driver.find_elements(
                By.CSS_SELECTOR, "#mCSB_2_container > a.bidding-table-rows"
            )
            bid_rows = driver.find_elements(
                By.CSS_SELECTOR, "#mCSB_3_container > a.bidding-table-rows"
            )

            ask_prices, ask_amounts = parse_rows(ask_rows)
            bid_prices, bid_amounts = parse_rows(bid_rows)

            coin_name = driver.find_element(
                By.CSS_SELECTOR, "b.pair-title"
            ).text.strip()
            ticker_text = driver.find_element(By.CSS_SELECTOR, "span.unit").text.strip()
            coin_ticker = ticker_text.replace("/USDT", "")

            if len(ask_prices) < 10 or len(bid_prices) < 10:
                time.sleep(0.5)
                continue

            asks_sorted = sorted(zip(ask_prices, ask_amounts), reverse=True)
            bids_sorted = sorted(zip(bid_prices, bid_amounts), reverse=True)

            asks = asks_sorted[-10:]
            bids = bids_sorted[:10]

            print_orderbook(coin_name, coin_ticker, asks, bids)
            time.sleep(refresh_interval)

        except KeyboardInterrupt:
            print("\n사용자에 의해 중단됨.")
            break
        except Exception as e:
            print("오류 발생:", e)
            time.sleep(1)
