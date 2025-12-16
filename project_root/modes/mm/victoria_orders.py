# victoria_orders.py
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Literal
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

Side = Literal["bid", "ask"]

TBODY = (By.CSS_SELECTOR, "tbody#out-standing-list")
ROWS = (By.CSS_SELECTOR, "tbody#out-standing-list > tr")
CANCEL_BTN_IN_ROW = (By.CSS_SELECTOR, "button.order-cancel[data-orderid]")

# row 내부 컬럼 인덱스 (스샷 기준)
# 0: Date, 1: Pair, 2: Type, 3: Price, 4: Qty, 5: Pending Qty, 6: Cancel(btn)
TYPE_TD_IDX = 2
PRICE_TD_IDX = 3


@dataclass
class OrderRow:
    side: Side
    price: float
    order_id: str
    row_el: object  # selenium webelement (타입 주석 단순화)


def _parse_number(text: str) -> float:
    t = (text or "").strip()
    t = re.sub(r"[^0-9\-,.]", "", t).replace(",", "")
    if not t:
        raise ValueError(f"cannot parse number from: {text!r}")
    return float(t)


def _infer_side_from_type_text(type_text: str) -> Side:
    # 화면에 buy/sell 로 나오므로 이를 side로 매핑
    t = (type_text or "").strip().lower()
    if t == "buy":
        return "bid"
    if t == "sell":
        return "ask"
    # 예외 케이스 대비: tradetype 속성으로도 판단할 수 있게 위에서 보조 처리함
    raise ValueError(f"unknown type text: {type_text!r}")


def read_open_orders_side(driver, side: Side, timeout: int = 10) -> List[OrderRow]:
    """
    미체결 주문 목록에서 bid/ask 한쪽만 읽어온다.
    - 행(row) 기준으로 파싱
    - type 컬럼(buy/sell)로 side 판단
    - price 컬럼에서 가격 파싱
    """
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located(TBODY))
    rows = driver.find_elements(*ROWS)

    out: List[OrderRow] = []
    for tr in rows:
        tds = tr.find_elements(By.TAG_NAME, "td")
        if len(tds) <= PRICE_TD_IDX:
            continue

        # type
        type_text = tds[TYPE_TD_IDX].text  # 보통 'sell' / 'buy'
        try:
            row_side = _infer_side_from_type_text(type_text)
        except Exception:
            # 버튼의 data-tradetype로도 보조 판단 가능 (스샷: ask)
            try:
                btn = tr.find_element(*CANCEL_BTN_IN_ROW)
                tradetype = (btn.get_attribute("data-tradetype") or "").strip().lower()
                if tradetype == "ask":
                    row_side = "ask"
                elif tradetype == "bid":
                    row_side = "bid"
                else:
                    continue
            except Exception:
                continue

        if row_side != side:
            continue

        # price
        price_text = tds[PRICE_TD_IDX].text  # "90,935\nUSDT" 형태 가능
        try:
            price = _parse_number(price_text)
        except Exception:
            continue

        # order id
        try:
            btn = tr.find_element(*CANCEL_BTN_IN_ROW)
            order_id = btn.get_attribute("data-orderid")
            if not order_id:
                continue
        except Exception:
            continue

        out.append(OrderRow(side=row_side, price=price, order_id=order_id, row_el=tr))

    return out


def cancel_order_row(driver, order_row: OrderRow, timeout: int = 10) -> bool:
    """
    row의 cancel 버튼 클릭 후,
    '해당 order_id가 DOM에서 사라졌는지'로 성공 판정.
    (행 사라짐 조건을 가장 안정적으로 구현한 방식)
    """
    order_id = order_row.order_id

    # 1) row 안에서 버튼 클릭
    try:
        btn = order_row.row_el.find_element(*CANCEL_BTN_IN_ROW)
        btn.click()
    except Exception:
        # row가 이미 사라졌을 수도 있음
        pass

    # 2) orderid 버튼이 더 이상 존재하지 않으면 취소 완료로 간주
    selector = f'button.order-cancel[data-orderid="{order_id}"]'
    try:
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, selector))
        )
        return True
    except Exception:
        # 아직 남아있으면 실패(또는 UI 지연) -> 상위 루틴에서 리트라이/리로드 처리
        return False
