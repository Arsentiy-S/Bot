from tradingview_ta import TA_Handler, Interval, Exchange
import matplotlib.pyplot as plt

intervals = {
    "1m": Interval.INTERVAL_1_MINUTE,
    "5m": Interval.INTERVAL_5_MINUTES,
    "15m": Interval.INTERVAL_15_MINUTES
}

def analyze_pair(pair: str, interval: str = "1m"):
    handler = TA_Handler(
        symbol=pair,
        screener="forex",
        exchange="FX_IDC",
        interval=intervals[interval]
    )

    try:
        analysis = handler.get_analysis()
        summary = analysis.summary
        indicators = analysis.indicators

        return {
            "RECOMMENDATION": summary["RECOMMENDATION"],
            "BUY": summary["BUY"],
            "SELL": summary["SELL"],
            "NEUTRAL": summary["NEUTRAL"],
            "INDICATORS": indicators
        }

    except Exception as e:
        return {"error": str(e)}

def plot_indicators(indicators: dict, pair: str):
    keys = list(indicators.keys())[:10]
    values = [indicators[k] for k in keys]
    plt.figure(figsize=(10, 4))
    plt.bar(keys, values, color='skyblue')
    plt.title(f"{pair} - Indicators Snapshot")
    plt.xticks(rotation=45)
    plt.tight_layout()
    img_path = f"{pair}_indicators.png"
    plt.savefig(img_path)
    plt.close()
    return img_path
