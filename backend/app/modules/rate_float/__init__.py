"""LPR 加点模块：合成年利率 = LPR + 加点基点 / 100，且不得为负。"""


def synthesized_annual_rate(lpr: float, spread_bp: float) -> float:
    """由 LPR 与加点基点合成实际年利率（%）。基点可为负（减点），但合成结果不得为负。"""
    rate = round(float(lpr) + float(spread_bp) / 100.0, 6)
    if rate < 0:
        raise ValueError("synthesized annual rate must not be negative")
    return rate
