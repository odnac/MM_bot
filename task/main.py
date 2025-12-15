# main.py
from config import (
    VICTORIA_URL,
    DISCOUNT_MIN,
    DISCOUNT_MAX,
    FOLLOW_UPDATE_SEC,
    ORDERBOOK_REFRESH_INTERVAL,
)
from orderbook_mode import run_victoria_orderbook_mode
from referenced_mm_mode import print_binance_referenced_price_mode
from security import check_password


# -------------------------------------------------
#  main() — 실행 시작점
# -------------------------------------------------
def main():

    if not check_password():
        return

    while True:
        try:
            print("\n\n\n ⚙️  Select Mode ⚙️\n")
            print("1) Show Order Book (VictoriaEX)")
            print("2) Print Binance-Referenced Price")
            print("q) Quit")

            mode = input("\n👉  Select (1/2/q): ").strip().lower()

            if mode == "1":
                run_victoria_orderbook_mode(VICTORIA_URL, ORDERBOOK_REFRESH_INTERVAL)

            elif mode == "2":
                print_binance_referenced_price_mode(
                    VICTORIA_URL,
                    DISCOUNT_MIN,
                    DISCOUNT_MAX,
                    FOLLOW_UPDATE_SEC,
                )

            # TODO : 모드 3 바이낸스 가격 추적 후 빅토리아 거래소에 주문
            elif mode == "3":
                # run_binance_referenced_mm_mode()
                pass

            elif mode == "q":
                print("Exiting...\n\n")
                break

            else:
                print("Invalid input. Please enter 1, 2, or q.")

        except KeyboardInterrupt:
            print("\n[!] Interrupted by user (Ctrl+C). Exiting safely...")
            break


# -------------------------------------------------
# 프로그램 실행
# -------------------------------------------------
if __name__ == "__main__":
    main()
