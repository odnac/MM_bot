# main.py
from config import VICTORIA_URL
from modes.security import check_password
from modes.orderbook_mode import run_victoria_orderbook_mode
from modes.print_referenced_price_mode import print_binance_referenced_price_mode
from modes.mm.binance_follow_mode import run_follow_mm_bid, run_follow_mm_ask


def prompt_mode() -> str:
    print("\n\n\n ⚙️  Select Mode ⚙️\n")
    print("1) Show Order Book (VictoriaEX)")
    print("2) Print Binance-Referenced Price")
    print("3) Run Follow Market Maker (Bid)")
    print("4) Run Follow Market Maker (Ask)")
    print("q) Quit")
    return input("\n👉  Select (1/2/3/4/q): ").strip().lower()


def prompt_ticker() -> str:
    t = input("👉  Coin ticker (e.g. BTC, ETH): ").strip().upper()
    if t.endswith("USDT"):
        t = t[:-4]
    return t


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
                ticker = prompt_ticker()
                run_follow_mm_bid(VICTORIA_URL, ticker)
            elif mode == "4":
                ticker = prompt_ticker()
                run_follow_mm_ask(VICTORIA_URL, ticker)
            elif mode == "q":
                print("Bye 👋...\n\n")
                break
            else:
                print("Invalid input. Please enter 1, 2, 3, 4 or q.")

        except KeyboardInterrupt:
            print("\n[!] Interrupted by user (Ctrl+C). Exiting safely...\n\n")
            break


if __name__ == "__main__":
    main()
