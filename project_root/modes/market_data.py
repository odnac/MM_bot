# modes/market_data.py
import requests


def get_binance_last_from_ticker(ticker: str) -> float:
    symbol = f"{ticker.upper()}USDT"

    url = "https://api.binance.com/api/v3/ticker/price"

    r = requests.get(url, params={"symbol": symbol}, timeout=10)
    r.raise_for_status()

    return float(r.json()["price"])
