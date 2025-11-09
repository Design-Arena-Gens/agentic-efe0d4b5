from dataclasses import dataclass
from typing import Optional

@dataclass
class RiskConfig:
    balance: float
    risk_percent: float  # e.g. 1.0 means 1%
    stop_distance: float  # absolute price distance
    tick_value: float
    tick_size: float
    min_lot: float
    max_lot: float
    lot_step: float


def round_step(value: float, step: float) -> float:
    steps = round(value / step)
    return max(step, steps * step)


def compute_lot_size(cfg: RiskConfig) -> float:
    if cfg.stop_distance <= 0 or cfg.tick_size <= 0 or cfg.tick_value <= 0:
        return cfg.min_lot
    risk_amount = cfg.balance * (cfg.risk_percent / 100.0)
    ticks = cfg.stop_distance / cfg.tick_size
    if ticks <= 0:
        return cfg.min_lot
    # Money lost per 1.0 lot at stop
    loss_per_lot = ticks * cfg.tick_value
    if loss_per_lot <= 0:
        return cfg.min_lot
    raw_lot = risk_amount / loss_per_lot
    lot = min(cfg.max_lot, max(cfg.min_lot, round_step(raw_lot, cfg.lot_step)))
    return lot
