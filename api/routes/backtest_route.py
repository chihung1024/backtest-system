from flask import Blueprint, request, jsonify
import yfinance as yf, pandas as pd, numpy as np
from api.utils.date_tools import safe_end_date
from functools import lru_cache

bp = Blueprint("backtest", __name__)

@lru_cache(maxsize=32)
def download_data_cached(tickers, start, end):
    return yf.download(tickers, start=start, end=end, group_by="ticker", auto_adjust=True, progress=False)

@bp.post("/api/backtest")
def backtest_api():
    p   = request.get_json()
    tks = tuple(sorted(p["tickers"])) # Convert to tuple for caching
    st  = p["start"]
    ed  = safe_end_date(p.get("end"))

    df = download_data_cached(tks, start=st, end=ed)

    # …以下保持原計算邏輯……………………………………
    closes = df.xs('Close', level=1, axis=1)
    weight = np.repeat(1/len(tks), len(tks))
    equity = closes.fillna(method="ffill").dot(weight)
    ret    = equity.pct_change().dropna()
    out = {
        "start": st,
        "end":   ed,
        "cagr":  (equity.iloc[-1]/equity.iloc[0]) ** (252/len(ret)) - 1,
        "mdd":   (equity/ equity.cummax()).min() - 1,
        "sharpe": np.sqrt(252)*ret.mean()/ret.std(),
        "equity": equity.to_json(date_format="iso")
    }
    return jsonify(out)
