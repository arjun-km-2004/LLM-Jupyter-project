"""
Stock Analysis Flask API (single file version)

Dependencies (install these before running):
    pip install flask yfinance pandas
"""

from flask import Flask, request, jsonify
import yfinance as yf
import pandas as pd

app = Flask(__name__)

# ---------- Helper functions ----------

def _clean_symbol(symbol: str) -> str:
    return symbol.upper().strip()


# ---------- 1. Company Information Endpoint ----------

def get_company_info(symbol: str):
    symbol = _clean_symbol(symbol)
    ticker = yf.Ticker(symbol)

    info = ticker.info  # basic company info from Yahoo Finance
    if not info:
        return None

    result = {
        "symbol": symbol,
        "longName": info.get("longName"),
        "shortName": info.get("shortName"),
        "summary": info.get("longBusinessSummary"),
        "industry": info.get("industry"),
        "sector": info.get("sector"),
        "website": info.get("website"),
        "country": info.get("country"),
        "currency": info.get("currency"),
    }

    officers = info.get("companyOfficers", []) or []
    key_officers = []
    for officer in officers:
        key_officers.append({
            "name": officer.get("name"),
            "title": officer.get("title"),
        })
    result["key_officers"] = key_officers

    return result


@app.route("/company/<symbol>", methods=["GET"])
def company_info(symbol):
    try:
        data = get_company_info(symbol)
        if data is None:
            return jsonify({"error": "Invalid symbol or data not found"}), 404
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- 2. Stock Market Data Endpoint (real-time-like) ----------

def get_realtime_market_data(symbol: str):
    symbol = _clean_symbol(symbol)
    ticker = yf.Ticker(symbol)

    info = ticker.info
    if not info:
        return None

    current_price = info.get("regularMarketPrice")
    previous_close = info.get("regularMarketPreviousClose")
    market_state = info.get("marketState")

    if current_price is None or previous_close is None:
        return None

    price_change = current_price - previous_close
    percent_change = (price_change / previous_close) * 100 if previous_close else None

    data = {
        "symbol": symbol,
        "market_state": market_state,
        "current_price": current_price,
        "previous_close": previous_close,
        "price_change": price_change,
        "percent_change": percent_change,
        "currency": info.get("currency"),
        "exchange": info.get("exchange"),
        "volume": info.get("regularMarketVolume"),
        "day_low": info.get("dayLow"),
        "day_high": info.get("dayHigh"),
        "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
    }
    return data


@app.route("/market/<symbol>", methods=["GET"])
def market_data(symbol):
    try:
        data = get_realtime_market_data(symbol)
        if data is None:
            return jsonify({"error": "Invalid symbol or data not found"}), 404
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- 3. Historical Market Data Endpoint (POST) ----------

def get_historical_data(symbol: str, start_date: str, end_date: str, interval: str = "1d"):
    symbol = _clean_symbol(symbol)
    ticker = yf.Ticker(symbol)

    try:
        df = ticker.history(start=start_date, end=end_date, interval=interval)
    except Exception:
        return None

    if df is None or df.empty:
        return None

    df = df.reset_index()
    # yfinance Date column is usually a Timestamp; convert to string
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    records = []
    for _, row in df.iterrows():
        records.append({
            "date": row["Date"],
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "volume": int(row["Volume"]),
        })

    return records


@app.route("/historical", methods=["POST"])
def historical_data():
    """
    Expected JSON body:
    {
        "symbol": "AAPL",
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
        "interval": "1d"
    }
    """
    try:
        payload = request.get_json(force=True, silent=True) or {}
        symbol = payload.get("symbol")
        start_date = payload.get("start_date")
        end_date = payload.get("end_date")
        interval = payload.get("interval", "1d")

        if not symbol or not start_date or not end_date:
            return jsonify({"error": "symbol, start_date, end_date are required"}), 400

        data = get_historical_data(symbol, start_date, end_date, interval)
        if data is None:
            return jsonify({"error": "No historical data found"}), 404

        return jsonify({
            "symbol": symbol,
            "data_points": len(data),
            "history": data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- 4. Analytical Insights Endpoint (POST) ----------

def analyze_company_from_history(symbol: str, start_date: str, end_date: str, interval: str = "1d"):
    symbol = _clean_symbol(symbol)
    ticker = yf.Ticker(symbol)

    try:
        df = ticker.history(start=start_date, end=end_date, interval=interval)
    except Exception:
        return None

    if df is None or df.empty:
        return None

    df = df.copy()

    # daily returns
    df["Return"] = df["Close"].pct_change()
    avg_daily_return = df["Return"].mean()
    volatility = df["Return"].std()
    cumulative_return = (df["Close"].iloc[-1] / df["Close"].iloc[0]) - 1

    # moving averages
    df["SMA_20"] = df["Close"].rolling(window=20).mean()
    df["SMA_50"] = df["Close"].rolling(window=50).mean()

    last_row = df.iloc[-1]
    close_price = float(last_row["Close"])
    sma_20 = float(last_row["SMA_20"]) if pd.notna(last_row["SMA_20"]) else None
    sma_50 = float(last_row["SMA_50"]) if pd.notna(last_row["SMA_50"]) else None

    # trend description
    if cumulative_return > 0.2:
        trend_desc = "strong uptrend"
    elif cumulative_return > 0:
        trend_desc = "mild uptrend"
    elif cumulative_return < -0.2:
        trend_desc = "strong downtrend"
    else:
        trend_desc = "mild downtrend or sideways"

    ma_signal = None
    if sma_20 is not None and sma_50 is not None:
        if sma_20 > sma_50:
            ma_signal = "short-term is above long-term (bullish bias)"
        elif sma_20 < sma_50:
            ma_signal = "short-term is below long-term (bearish bias)"
        else:
            ma_signal = "short-term and long-term are at similar levels (neutral)"

    insights = {
        "symbol": symbol,
        "period": {
            "start_date": start_date,
            "end_date": end_date,
            "interval": interval
        },
        "summary": {
            "cumulative_return_percent": round(cumulative_return * 100, 2),
            "avg_daily_return_percent": round(avg_daily_return * 100, 4) if pd.notna(avg_daily_return) else None,
            "volatility_percent": round(volatility * 100, 4) if pd.notna(volatility) else None,
            "trend_description": trend_desc
        },
        "moving_averages": {
            "last_close_price": close_price,
            "SMA_20": sma_20,
            "SMA_50": sma_50,
            "ma_signal": ma_signal
        },
        "actionable_insights": []
    }

    ai = insights["actionable_insights"]

    if cumulative_return > 0.1:
        ai.append("The stock delivered a positive return over this period, indicating upward momentum.")
    elif cumulative_return < -0.1:
        ai.append("The stock delivered a negative return over this period, indicating downward pressure.")

    if volatility is not None:
        if volatility > 0.03:
            ai.append("The stock shows relatively high volatility; suitable for risk-tolerant investors.")
        else:
            ai.append("The stock shows relatively lower volatility; may appeal to conservative investors.")

    if ma_signal:
        ai.append(f"Based on moving averages, the price currently shows: {ma_signal}.")

    return insights


@app.route("/analytics", methods=["POST"])
def analytics():
    """
    Expected JSON body:
    {
        "symbol": "AAPL",
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
        "interval": "1d"
    }
    """
    try:
        payload = request.get_json(force=True, silent=True) or {}
        symbol = payload.get("symbol")
        start_date = payload.get("start_date")
        end_date = payload.get("end_date")
        interval = payload.get("interval", "1d")

        if not symbol or not start_date or not end_date:
            return jsonify({"error": "symbol, start_date, end_date are required"}), 400

        insights = analyze_company_from_history(symbol, start_date, end_date, interval)
        if insights is None:
            return jsonify({"error": "Unable to generate insights (no data)"}), 404

        return jsonify(insights), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- Home route ----------

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Stock Analysis API is running",
        "endpoints": {
            "company_info": "/company/<symbol>",
            "market_data": "/market/<symbol>",
            "historical_data": "/historical (POST)",
            "analytics": "/analytics (POST)"
        }
    }), 200


# ---------- Entry point ----------

if __name__ == "__main__":
    # debug=True only for development
    app.run(debug=True)
