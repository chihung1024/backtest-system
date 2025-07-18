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

    if df.empty:
        return jsonify({"error": "No data found for the given tickers and date range."}), 400

    closes = df.xs('Close', level=1, axis=1)
    weights = np.repeat(1.0 / len(tks), len(tks))
    
    closes = closes.apply(pd.to_numeric, errors='coerce')
    
    closes.fillna(method='ffill', inplace=True)
    
    closes.dropna(inplace=True)

    if closes.empty:
        return jsonify({"error": "Data could not be processed after cleaning. Check ticker data availability."}), 400

    equity = closes.dot(weights)
    
    if equity.empty:
        return jsonify({"error": "Equity curve could not be calculated."}), 400

    ret = equity.pct_change().dropna()

    if ret.empty:
        return jsonify({"error": "Could not calculate returns."}), 400

    # Calculations
    cagr = (equity.iloc[-1] / equity.iloc[0]) ** (252 / len(ret)) - 1 if len(ret) > 0 else 0
    cumulative_max = equity.cummax()
    drawdown = (equity - cumulative_max) / cumulative_max
    mdd = drawdown.min() if not drawdown.empty else 0
    sharpe_ratio = np.sqrt(252) * ret.mean() / ret.std() if ret.std() != 0 else 0

    out = {
        "start": st,
        "end":   ed,
        "cagr":  cagr,
        "mdd":   mdd,
        "sharpe": sharpe_ratio,
        "equity": equity.to_json(date_format="iso")
    }
    return jsonify(out)
