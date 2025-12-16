# victoria_balance.py
from __future__ import annotations

import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def _parse_number(text: str) -> float:
    """
    '381,629.061' / '0.31492109' / 공백 포함 등 케이스를 안전하게 float로.
    """
    if text is None:
        raise ValueError("empty text")
    t = text.strip()
    # 숫자/점/마이너스/콤마 외 제거
    t = re.sub(r"[^0-9\-,.]", "", t)
    # 콤마 제거
    t = t.replace(",", "")
    if t in ("", "-", ".", "-."):
        raise ValueError(f"cannot parse number: {text!r}")
    return float(t)


def get_free_usdt(driver, timeout: int = 10) -> float:
    """
    Available to Buy (USDT)
    CSS: <span id="user_base_trans">381,629.061</span>
    """
    el = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, "user_base_trans"))
    )
    return _parse_number(el.text)


def get_free_coin_qty(driver, timeout: int = 10) -> float:
    """
    Available to Sell (BTC) (또는 해당 코인)
    CSS: <span id="user_base_coin">0.31492109</span>
    """
    el = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, "user_base_coin"))
    )
    return _parse_number(el.text)
