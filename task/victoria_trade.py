# task/victoria_trade.py
from __future__ import annotations

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def _set_input_value(driver, by, locator, value: str, timeout: int = 10):
    el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, locator)))
    el.click()
    # Ctrl+A / Delete 로 완전 삭제 후 입력 (사이트에 따라 clear()가 안 먹는 경우가 많음)
    el.send_keys(Keys.CONTROL, "a")
    el.send_keys(Keys.DELETE)
    el.send_keys(value)
    return el


def place_limit_order(
    driver, side: str, price: float, qty: float, timeout: int = 10
) -> bool:
    """
    side: "bid" or "ask"
    price: USDT 가격
    qty: BTC 수량
    """
    if qty <= 0 or price <= 0:
        return False

    # 화면 표시가 89,764.000 같은 포맷이어도 input은 보통 숫자 문자열이면 됨
    price_str = f"{price:.6f}".rstrip("0").rstrip(".")
    qty_str = f"{qty:.8f}".rstrip("0").rstrip(".")

    if side == "bid":
        _set_input_value(driver, By.ID, "bid_price", price_str, timeout=timeout)
        _set_input_value(driver, By.ID, "bid_coin", qty_str, timeout=timeout)

        btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.ID, "btnBuying"))
        )
        btn.click()
    elif side == "ask":
        _set_input_value(driver, By.ID, "ask_price", price_str, timeout=timeout)
        _set_input_value(driver, By.ID, "ask_coin", qty_str, timeout=timeout)

        btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.ID, "btnSelling"))
        )
        btn.click()
    else:
        raise ValueError(f"unknown side: {side}")

    # 너무 빠르게 연속 클릭하면 UI가 씹히는 경우가 있어서 아주 짧게 텀
    time.sleep(0.15)
    return True
