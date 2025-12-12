from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

CHROME_DRIVER_PATH = r"C:\chromedriver\chromedriver.exe"

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=options)


def parse_rows(rows):
    prices, amounts = [], []
    for row in rows:
        try:
            p = (
                row.find_element(By.CSS_SELECTOR, ".col-price")
                .text.strip()
                .replace(",", "")
            )
            a = (
                row.find_element(By.CSS_SELECTOR, ".col-amount")
                .text.strip()
                .replace(",", "")
            )
            if p and a and p != "-" and a != "-":
                prices.append(float(p))
                amounts.append(float(a))
        except:
            continue
    return prices, amounts


try:
    driver.get("https://www.victoriaex.com")
    print("\n빅토리아 연결됨 → 로그인 후 엔터를 눌러주세요")
    input()

    driver.get("https://www.victoriaex.com/trade")

    # 호가창이 뜰 때까지 기다림
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a.bidding-table-rows"))
    )

    print("\n실시간 호가창 시작 – 거래소 화면과 동일하게 표시됩니다!\n")

    while True:
        # ✔ 매도와 매수를 각자 컨테이너 기준으로 가져온다
        ask_rows = driver.find_elements(
            By.CSS_SELECTOR, "#mCSB_2_container > a.bidding-table-rows"
        )
        bid_rows = driver.find_elements(
            By.CSS_SELECTOR, "#mCSB_3_container > a.bidding-table-rows"
        )

        ask_prices, ask_amounts = parse_rows(ask_rows)
        bid_prices, bid_amounts = parse_rows(bid_rows)

        coin_name = driver.find_element(By.CSS_SELECTOR, "b.pair-title").text.strip()

        if len(ask_prices) < 10 or len(bid_prices) < 10:
            time.sleep(0.5)
            continue

        # 가격 높은 순 정렬
        asks = sorted(zip(ask_prices, ask_amounts), reverse=True)[:10]
        bids = sorted(zip(bid_prices, bid_amounts), reverse=True)[:10]

        print(
            f"┌──────── {time.strftime('%H:%M:%S')}  {coin_name} 실시간 호가창 ────────┐"
        )

        # 매도 호가
        asks_sorted = sorted(zip(ask_prices, ask_amounts), reverse=True)
        asks = asks_sorted[-10:]  # 뒤에서 10개 (가장 낮은 10개 → 1~10호가)

        print("\n         🟦 매도 호가 (Ask)\n")

        # asks[0] = 10호가, asks[9] = 1호가
        for i, (p, a) in enumerate(asks[:10], 1):
            print(f" {11-i:2d}호가 │ {p:>14,.2f} │ {a:>14,.6f}")

        # 🔴 매수 호가
        print("\n         🔴 매수 호가 (Bid)")
        for i, (p, a) in enumerate(bids, 1):
            amount_str = f"{a:,.6f}".rstrip("0").rstrip(".")
            print(f" {i:2d}호가 │ {p:>14,.2f} │ {a:>14,.6f}")

        print("└" + "─" * 58 + "┘\n")
        time.sleep(2.5)

except Exception as e:
    print("오류 발생:", e)
    input()
finally:
    driver.quit()
