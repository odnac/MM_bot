# utils.py
import os
import platform


def wait_for_manual_login(mode: int):
    mode_titles = {
        1: "Show VictoriaEX Order Book",
        2: "Print Binance-Referenced Price Mode Started",
        3: "Follow MM (BID)",
        4: "Follow MM (ASK)",
    }

    print("\n" + "=" * 45)
    print("         💎 Connected to VictoriaEX 💎")
    print("  Press Enter after logging in to continue.")
    print("=" * 45 + "\n")
    input()

    title = mode_titles.get(mode, "Unknown Mode")
    print(f"\n[Mode {mode}] {title}\n\n")


def clear_console():
    # os.system("cls" if platform.system() == "Windows" else "clear")
    pass
