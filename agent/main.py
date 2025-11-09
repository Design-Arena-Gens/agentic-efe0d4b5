import json
import os
import time
import subprocess
from typing import Dict, Any, List

import MetaTrader5 as mt5
import requests

from risk import RiskConfig, compute_lot_size

CONFIG_PATH = os.environ.get("BOT_CONFIG", os.path.join(os.path.dirname(__file__), "config.json"))


def load_config() -> Dict[str, Any]:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_terminal(path: str | None):
    if not path:
        return
    try:
        # Launch Terminal silently if not running
        subprocess.Popen([path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def mt5_init(term_path: str | None, login: int, password: str, server: str):
    if term_path and os.path.exists(term_path):
        mt5.initialize(path=term_path)
    else:
        mt5.initialize()
    if login and password and server:
        mt5.login(login=login, password=password, server=server)


def timeframe_to_mt5(tf: str):
    mapping = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1,
    }
    return mapping.get(tf.upper(), mt5.TIMEFRAME_M5)


def fetch_rates(symbol: str, timeframe: str, count: int) -> List[Dict[str, Any]]:
    tf = timeframe_to_mt5(timeframe)
    rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
    if rates is None:
        return []
    candles: List[Dict[str, Any]] = []
    for r in rates:
        candles.append({
            "time": int(r["time"]),
            "open": float(r["open"]),
            "high": float(r["high"]),
            "low": float(r["low"]),
            "close": float(r["close"]),
            "volume": float(r["tick_volume"]),
        })
    return candles


def post_json(url: str, data: Dict[str, Any], secret: str) -> Any:
    resp = requests.post(url, headers={"Content-Type": "application/json", "x-webhook-secret": secret}, data=json.dumps(data), timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_signal(base: str, secret: str, symbol: str, timeframe: str, candles: List[Dict[str, Any]]):
    url = f"{base}/api/signal"
    return post_json(url, {"symbol": symbol, "timeframe": timeframe, "candles": candles}, secret)


def heartbeat(base: str, secret: str, agent_id: str):
    url = f"{base}/api/agent/heartbeat"
    try:
        post_json(url, {"id": agent_id}, secret)
    except Exception:
        pass


def register(base: str, secret: str, agent_id: str):
    url = f"{base}/api/agent/register"
    post_json(url, {"id": agent_id}, secret)


def place_order(symbol: str, direction: str, entry: float, sl: float | None, tp: float | None, lot: float) -> Dict[str, Any]:
    info = mt5.symbol_info(symbol)
    if info is None:
        raise RuntimeError(f"Unknown symbol: {symbol}")
    if not info.visible:
        mt5.symbol_select(symbol, True)

    order_type = mt5.ORDER_TYPE_BUY if direction == "buy" else mt5.ORDER_TYPE_SELL

    price = mt5.symbol_info_tick(symbol).ask if direction == "buy" else mt5.symbol_info_tick(symbol).bid
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "deviation": 20,
        "magic": 20251109,
        "comment": "ai-forex-bot",
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    if sl:
        request["sl"] = sl
    if tp:
        request["tp"] = tp

    result = mt5.order_send(request)
    if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
        raise RuntimeError(f"order_send failed: {getattr(result, 'retcode', 'no result')}")
    return {"order": result.order, "deal": getattr(result, 'deal', None), "price": price}


def compute_stop_distance(symbol: str, entry: float, sl: float | None) -> float:
    if sl is None:
        return 0.0
    return abs(entry - sl)


def main():
    cfg = load_config()

    ensure_terminal(cfg.get("terminal_path"))

    mt5_init(
        cfg.get("terminal_path"),
        int(cfg.get("mt5", {}).get("login", 0) or 0),
        str(cfg.get("mt5", {}).get("password", "")),
        str(cfg.get("mt5", {}).get("server", "")),
    )

    account_info = mt5.account_info()
    balance = float(account_info.balance) if account_info else 10000.0

    base = cfg["server_base"].rstrip("/")
    secret = cfg["webhook_secret"]
    agent_id = cfg["agent_id"]

    # Register once
    try:
        register(base, secret, agent_id)
    except Exception as e:
        print("Register failed:", e)

    timeframe = cfg.get("timeframe", "M5")
    candles_n = int(cfg.get("candles", 300))
    min_conf = float(cfg.get("min_confidence", 0.6))
    risk_percent = float(cfg.get("risk_percent", 1.0))
    max_spread_points = int(cfg.get("max_spread_points", 25))

    while True:
        for symbol in cfg.get("symbols", []):
            try:
                heartbeat(base, secret, agent_id)
                candles = fetch_rates(symbol, timeframe, candles_n)
                if len(candles) < 50:
                    continue
                signal = get_signal(base, secret, symbol, timeframe, candles)
                if signal.get("signal") == "none" or float(signal.get("confidence", 0)) < min_conf:
                    continue

                # Spread check
                tick = mt5.symbol_info_tick(symbol)
                if not tick:
                    continue
                spread_points = int(round((tick.ask - tick.bid) / mt5.symbol_info(symbol).point))
                if spread_points > max_spread_points:
                    continue

                entry = float(signal.get("entry") or tick.ask)
                sl = signal.get("stopLoss")
                tp = signal.get("takeProfit")
                stop_distance = compute_stop_distance(symbol, entry, sl)

                sinfo = mt5.symbol_info(symbol)
                if not sinfo:
                    continue
                risk_cfg = RiskConfig(
                    balance=balance,
                    risk_percent=risk_percent,
                    stop_distance=stop_distance,
                    tick_value=float(sinfo.trade_tick_value),
                    tick_size=float(sinfo.trade_tick_size or sinfo.point),
                    min_lot=float(sinfo.volume_min),
                    max_lot=float(sinfo.volume_max),
                    lot_step=float(sinfo.volume_step)
                )
                lot = compute_lot_size(risk_cfg)

                trade = place_order(symbol, signal["signal"], entry, sl, tp, lot)

                try:
                    post_json(f"{base}/api/agent/report", {
                        "id": agent_id,
                        "symbol": symbol,
                        "signal": signal,
                        "lot": lot,
                        "trade": trade
                    }, secret)
                except Exception:
                    pass
            except Exception as e:
                print("Error:", e)
                time.sleep(2)
                continue
        time.sleep(float(cfg.get("poll_seconds", 20)))


if __name__ == "__main__":
    main()
