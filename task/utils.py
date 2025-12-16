# utils.py
import os
import platform


# -------------------------------------------------
#  콘솔 화면을 OS에 맞게 초기화
# -------------------------------------------------
def clear_console():
    # os.system("cls" if platform.system() == "Windows" else "clear")
    pass


# -------------------------------------------------
#  로그인 대기 문구 출력
# -------------------------------------------------
def wait_for_manual_login():
    print("\n" + "=" * 45)
    print("         💎 Connected to VictoriaEX 💎")
    print("  Press Enter after logging in to continue.")
    print("=" * 45 + "\n")
    input()
