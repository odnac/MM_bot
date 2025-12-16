# main.py
from .config import VICTORIA_URL
from .orderbook_mode import run_victoria_orderbook_mode
from .print_referenced_price_mode import print_binance_referenced_price_mode
from .security import check_password
from .binance_follow_mm_mode import run_follow_mm_bid, run_follow_mm_ask


def prompt_mode() -> str:
    print("\n\n\n ⚙️  Select Mode ⚙️\n")
    print("1) Show Order Book (VictoriaEX)")
    print("2) Print Binance-Referenced Price")
    print("3) Run Follow Market Maker (Bid)")
    print("4) Run Follow Market Maker (Ask)")
    print("q) Quit")
    return input("\n👉  Select (1/2/3/4/q): ").strip().lower()


# -------------------------------------------------
#  main() — 실행 시작점
# -------------------------------------------------
def main():

    if not check_password():
        return

    while True:
        try:
            mode = prompt_mode()

            if mode == "1":
                run_victoria_orderbook_mode(VICTORIA_URL)

            elif mode == "2":
                print_binance_referenced_price_mode(VICTORIA_URL)

            elif mode == "3":
                run_follow_mm_bid(VICTORIA_URL)

            elif mode == "4":
                run_follow_mm_ask(VICTORIA_URL)

            elif mode == "q":
                print("Bye 👋...\n\n")
                break

            else:
                print("Invalid input. Please enter 1, 2, 3, 4 or q.")

        except KeyboardInterrupt:
            print("\n[!] Interrupted by user (Ctrl+C). Exiting safely...")
            break


# -------------------------------------------------
# 프로그램 실행
# -------------------------------------------------
if __name__ == "__main__":
    main()
