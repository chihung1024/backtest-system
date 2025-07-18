from flask import Blueprint, request, jsonify
import yfinance as yf
from functools import lru_cache

bp = Blueprint("scan", __name__)

@lru_cache(maxsize=128)
def download_hist_cached(ticker):
    return yf.download(ticker, period="5y", auto_adjust=True, progress=False)[["Close"]]

@lru_cache(maxsize=128)
def get_info_cached(ticker):
    return yf.Ticker(ticker).info

@bp.post("/api/scan")
def scan_api():
    tk = request.json["ticker"].strip().upper()

    # 只抓 Close 欄，避免欄位數浮動
    hist = download_hist_cached(tk)
    if hist.empty:
        return jsonify({"error": "no data"}), 404

    hist.reset_index(inplace=True)
    hist.columns = ["Date", "Close"]

    info = get_info_cached(tk)
    resp = {
        "ticker": tk,
        "marketCap": info.get("marketCap"),
        "pe": info.get("trailingPE"),
        "price": hist["Close"].iloc[-1],
        "history": hist.to_dict(orient="records")
    }
    return jsonify(resp)
