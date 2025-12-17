# follow_mm_mode.py
from __future__ import annotations

import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dataclasses import dataclass
from typing import Literal, List, Optional
from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
)
from config import (
    DISCOUNT_MIN,
    DISCOUNT_MAX,
    MM_LEVELS,
    MM_REBASE_INTERVAL_SEC,
    MM_TOPUP_INTERVAL_SEC,
    MM_STEP_PERCENT,
    MM_CANCEL_ROW_TIMEOUT_SEC,
    MM_MAX_CANCEL_OPS_PER_CYCLE,
    MM_BUY_BUDGET_RATIO,
    MM_SELL_QTY_RATIO,
    MM_TOAST_WAIT_SEC,
)
from modes.utils_driver import init_driver
from modes.mm.victoria_balance import get_free_usdt, get_free_coin_qty
from modes.mm.victoria_trade import place_limit_order
from modes.mm.victoria_orders import read_open_orders_side, cancel_order_row, OrderRow
from modes.market_data import get_binance_price
from modes.utils_logging import setup_logger
from modes.utils_ui import validate_login_or_exit

logger = setup_logger()

Side = Literal["bid", "ask"]


@dataclass(frozen=True)
class EngineConfig:
    levels: int
    rebase_interval_sec: int
    topup_interval_sec: int
    step_percent: float
    cancel_row_timeout_sec: int
    max_cancel_ops_per_cycle: int
    buy_budget_ratio: float
    sell_qty_ratio: float
    toast_wait_sec: float


def _build_cfg() -> EngineConfig:
    return EngineConfig(
        levels=MM_LEVELS,
        rebase_interval_sec=MM_REBASE_INTERVAL_SEC,
        topup_interval_sec=MM_TOPUP_INTERVAL_SEC,
        step_percent=MM_STEP_PERCENT,
        cancel_row_timeout_sec=MM_CANCEL_ROW_TIMEOUT_SEC,
        max_cancel_ops_per_cycle=MM_MAX_CANCEL_OPS_PER_CYCLE,
        buy_budget_ratio=MM_BUY_BUDGET_RATIO,
        sell_qty_ratio=MM_SELL_QTY_RATIO,
        toast_wait_sec=MM_TOAST_WAIT_SEC,
    )


def _now() -> float:
    return time.time()


def _step_ratio(step_percent: float) -> float:
    # 0.2 -> 0.002
    return step_percent / 100.0


def _normalize_price(price: float) -> float:
    """
    tick size를 정확히 모르면 일단 소수 3자리로 맞추는 게 UI에 잘 맞는 경우가 많음.
    (너 스샷이 89,764.000 형태)
    """
    return round(float(price), 3)


def _normalize_qty(qty: float) -> float:
    """
    BTC 수량은 보통 8자리면 충분.
    """
    return round(float(qty), 8)


def _weights_pyramid(n: int) -> List[float]:
    # 1..n (합 1)
    raw = list(range(1, n + 1))
    s = sum(raw)
    return [r / s for r in raw]


def _weights_inverse_pyramid(n: int) -> List[float]:
    raw = list(range(n, 0, -1))
    s = sum(raw)
    return [r / s for r in raw]


def _sleep_tiny():
    time.sleep(0.15)


def _maybe_wait_toast(cfg: EngineConfig):
    """
    TODO: 나중에 토스트 CSS 주면 여기서 '토스트 나타남->사라짐' 대기 로직을 붙이면 됨.
    지금은 옵션으로만 두고 기본 0초.
    """
    if cfg.toast_wait_sec and cfg.toast_wait_sec > 0:
        time.sleep(cfg.toast_wait_sec)


def _victoria_trade_url(victoria_url: str, ticker: str) -> str:
    return f"{victoria_url}/trade?code=USDT-{ticker.upper()}"


# ---------------------------
# Core engine
# ---------------------------
class FollowMMEngine:

    def __init__(self, driver, side: Side, cfg: EngineConfig, ticker: str):
        self.driver = driver
        self.side = side
        self.cfg = cfg
        self.ticker = ticker.upper()

        self._step = _step_ratio(cfg.step_percent)
        self._anchor_price: Optional[float] = None
        self._discount_for_cycle: Optional[float] = None  # ratio (0.01 = 1%)
        self._last_rebase_ts = 0.0
        self._last_topup_ts = 0.0
        self._rebase_lock = False

    def run_forever(self):
        self.rebase()

        while True:
            now = _now()

            if now - self._last_rebase_ts >= self.cfg.rebase_interval_sec:
                self.rebase()

            if (not self._rebase_lock) and (
                now - self._last_topup_ts >= self.cfg.topup_interval_sec
            ):
                self.topup()

            time.sleep(0.5)

    def rebase(self):
        self._rebase_lock = True
        try:
            symbol = f"{self.ticker.upper()}USDT"
            self._anchor_price = get_binance_price(symbol)

            self._discount_for_cycle = (
                random.uniform(DISCOUNT_MIN, DISCOUNT_MAX) / 100.0
            )

            self._prune_keep_15()
            self._fill_to_15()
            self._last_rebase_ts = _now()

        finally:
            self._rebase_lock = False

    def topup(self):
        if self._anchor_price is None or self._discount_for_cycle is None:
            self.rebase()
            return

        self._fill_to_15()
        self._last_topup_ts = _now()

    def _prune_keep_15(self):
        rows = read_open_orders_side(self.driver, self.side)

        if len(rows) <= self.cfg.levels:
            return

        if self.side == "ask":
            rows_sorted = sorted(rows, key=lambda r: r.price)  # low -> high
            cancel = rows_sorted[self.cfg.levels :]  # high side
            cancel = sorted(cancel, key=lambda r: r.price, reverse=True)
        else:
            rows_sorted = sorted(
                rows, key=lambda r: r.price, reverse=True
            )  # high -> low
            cancel = rows_sorted[self.cfg.levels :]  # low side
            cancel = sorted(cancel, key=lambda r: r.price)

        ops = 0
        for row in cancel:
            if ops >= self.cfg.max_cancel_ops_per_cycle:
                break
            try:
                cancel_order_row(
                    self.driver, row, timeout=self.cfg.cancel_row_timeout_sec
                )
                _maybe_wait_toast(self.cfg)  # TODO: 토스트 CSS 적용 시 의미 생김
                ops += 1
            except (StaleElementReferenceException, WebDriverException):
                # UI가 흔들리면 다음 사이클에서 다시 맞춰짐
                continue

    def _fill_to_15(self):
        rows = read_open_orders_side(self.driver, self.side)
        need = self.cfg.levels - len(rows)
        if need <= 0:
            return

        # 완전 비어있으면 anchor 기반으로 full ladder 생성
        if len(rows) == 0:
            prices = self._build_full_ladder_prices()
            self._place_ladder(prices)
            return

        # “앞쪽이 먹히면 당겨지고 바깥쪽이 채워짐” 구현:
        # - ask: 남아있는 것 중 최고가(max) 기준으로 (1+step)^k로 바깥쪽(더 높은) 생성
        # - bid: 남아있는 것 중 최저가(min) 기준으로 (1-step)^k로 바깥쪽(더 낮은) 생성
        if self.side == "ask":
            outer = max(r.price for r in rows)
            new_prices = [
                _normalize_price(outer * ((1 + self._step) ** i))
                for i in range(1, need + 1)
            ]
        else:
            outer = min(r.price for r in rows)
            new_prices = [
                _normalize_price(outer * ((1 - self._step) ** i))
                for i in range(1, need + 1)
            ]

        self._place_ladder(new_prices)

    def _build_full_ladder_prices(self) -> List[float]:
        assert self._anchor_price is not None
        assert self._discount_for_cycle is not None

        p1 = _normalize_price(self._anchor_price)
        d = self._discount_for_cycle
        s = self._step

        prices: List[float] = [p1]

        if self.side == "bid":
            # 2..15 : anchor*(1-d) * (1-s)^(k-2)
            base = p1 * (1 - d)
            for k in range(2, self.cfg.levels + 1):
                pk = base * ((1 - s) ** (k - 2))
                prices.append(_normalize_price(pk))
        else:
            # 매도는 "바이낸스보다 비싸게" 가는 안전형으로 설정
            # (만약 싸게 던지는 전략이면 (1 - d)로 바꾸면 됨)
            base = p1 * (1 + d)
            for k in range(2, self.cfg.levels + 1):
                pk = base * ((1 + s) ** (k - 2))
                prices.append(_normalize_price(pk))

        return prices

    def _place_ladder(self, prices: List[float]):
        """
        - bid(매수): 피라미드(가까울수록 적게, 멀수록 많게) / 기준: USDT
        - ask(매도): 역피라미드(가까울수록 많게, 멀수록 적게) / 기준: 코인수량
        """
        if not prices:
            return

        if self.side == "bid":
            usdt = get_free_usdt(self.driver) * self.cfg.buy_budget_ratio
            weights = _weights_pyramid(len(prices))
            for price, w in zip(prices, weights):
                budget = usdt * w
                qty = _normalize_qty(budget / price)
                if qty <= 0:
                    continue
                logger.info(
                    f"[ORDER] {self.ticker} {self.side.upper()} "
                    f"price={price:.3f} qty={qty:.8f}"
                )
                place_limit_order(self.driver, "bid", price, qty)
                _maybe_wait_toast(self.cfg)
                _sleep_tiny()
        else:
            coin = get_free_coin_qty(self.driver) * self.cfg.sell_qty_ratio
            weights = _weights_inverse_pyramid(len(prices))
            for price, w in zip(prices, weights):
                qty = _normalize_qty(coin * w)
                if qty <= 0:
                    continue
                logger.info(
                    f"[ORDER] {self.ticker} {self.side.upper()} "
                    f"price={price:.3f} qty={qty:.8f}"
                )
                place_limit_order(self.driver, "ask", price, qty)
                _maybe_wait_toast(self.cfg)
                _sleep_tiny()


def run_follow_mm_bid(victoria_url: str, ticker: str):
    cfg = _build_cfg()
    driver = init_driver()

    try:
        driver.get(f"{victoria_url}/account/login")

        validate_login_or_exit(driver=driver, mode=3)

        driver.get(_victoria_trade_url(victoria_url, ticker))
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "user_base_trans"))
        )

        FollowMMEngine(driver=driver, side="bid", cfg=cfg, ticker=ticker).run_forever()

    except KeyboardInterrupt:
        print("\n[INFO] Follow MM BID stopped by user (KeyboardInterrupt)")

    except Exception as e:
        print(f"\n[ERROR] Follow MM BID crashed: {type(e).__name__} - {e}")

    finally:
        try:
            driver.quit()
        except Exception:
            pass
        print("[INFO] Driver shutdown complete.")


def run_follow_mm_ask(victoria_url: str, ticker: str):
    cfg = _build_cfg()
    driver = init_driver()

    try:
        driver.get(f"{victoria_url}/account/login")

        validate_login_or_exit(driver=driver, mode=4)

        driver.get(_victoria_trade_url(victoria_url, ticker))
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "user_base_coin"))
        )

        FollowMMEngine(driver=driver, side="ask", cfg=cfg, ticker=ticker).run_forever()

    except KeyboardInterrupt:
        print("\n[INFO] Follow MM ASK stopped by user (KeyboardInterrupt)")

    except Exception as e:
        print(f"\n[ERROR] Follow MM ASK crashed: {type(e).__name__} - {e}")

    finally:
        try:
            driver.quit()
        except Exception:
            pass
        print("[INFO] Driver shutdown complete.")


# 500
# 16,000
# 11,000
