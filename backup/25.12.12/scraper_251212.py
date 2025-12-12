from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# -------------------------------------------------
# 환경 설정
# -------------------------------------------------
CHROME_DRIVER_PATH = r"C:\chromedriver\chromedriver.exe"
VICTORIA_URL = "https://www.victoriaex.com"
ORDERBOOK_REFRESH_INTERVAL = 2.5  # 초


# -------------------------------------------------
# 1️⃣ 드라이버 초기화
# -------------------------------------------------
def init_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    return driver


# -------------------------------------------------
# 2️⃣ 호가 행(Row) 데이터 파싱
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
# 3️⃣ 콘솔 출력 함수
# -------------------------------------------------
def print_orderbook(coin_name, coin_ticker, asks, bids):
    print(f"┌──────────── {time.strftime('%H:%M:%S')}  {coin_ticker} ────────────┐")

    # 매도 (Ask)
    print("\n            🟦 매도 호가 (Ask)\n")
    for i, (price, amount) in enumerate(asks[:10], 1):
        print(f" {11 - i:2d}호가 │ {price:>14,.4f} │ {amount:>14,.6f}")

    # 매수 (Bid)
    print("\n            🔴 매수 호가 (Bid)\n")
    for i, (price, amount) in enumerate(bids, 1):
        print(f" {i:2d}호가 │ {price:>14,.4f} │ {amount:>14,.6f}")

    print("\n└" + "─" * 40 + "┘\n")


# -------------------------------------------------
# 4️⃣ 실시간 호가창 루프
# -------------------------------------------------
def run_orderbook(driver):
    driver.get(f"{VICTORIA_URL}/trade")

    # 호가창 로딩 대기
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

            # 매도/매수 정렬
            asks_sorted = sorted(zip(ask_prices, ask_amounts), reverse=True)
            bids_sorted = sorted(zip(bid_prices, bid_amounts), reverse=True)

            asks = asks_sorted[-10:]  # 낮은 매도 10개
            bids = bids_sorted[:10]  # 높은 매수 10개

            print_orderbook(coin_name, coin_ticker, asks, bids)
            time.sleep(ORDERBOOK_REFRESH_INTERVAL)

        except KeyboardInterrupt:
            print("\n사용자에 의해 중단됨.")
            break
        except Exception as e:
            print("오류 발생:", e)
            time.sleep(1)


# -------------------------------------------------
# 5️⃣ main() — 실행 시작점
# -------------------------------------------------
def main():
    driver = init_driver()
    try:
        driver.get(f"{VICTORIA_URL}/account/login")
        print("\n" + "=" * 45)
        print("         💎 VictoriaEX 연결 완료 💎")
        print("  로그인 후 Enter 키를 눌러 계속 진행하세요.")
        print("=" * 45 + "\n")
        input()
        run_orderbook(driver)
    finally:
        driver.quit()
        print("드라이버 종료 완료.")


# -------------------------------------------------
# 프로그램 실행
# -------------------------------------------------
if __name__ == "__main__":
    main()
