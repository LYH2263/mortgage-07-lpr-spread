def compose_annual_rate(lpr: float, spread_bps: float) -> float:
    """合成年利率 = LPR + 加点基点 / 100（1 基点 = 0.01%），不得为负。"""
    rate = float(lpr) + float(spread_bps) / 100.0
    if rate < 0:
        raise ValueError("composed annual rate must not be negative")
    return round(rate, 6)
