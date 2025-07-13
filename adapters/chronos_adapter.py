import json
import os
import base64
import io

import pandas as pd
import matplotlib.pyplot as plt
import torch
from chronos import BaseChronosPipeline

# Load pre-trained Chronos model (CPU version)
pipeline = BaseChronosPipeline.from_pretrained(
    "amazon/chronos-t5-small",
    device_map="cpu",
    torch_dtype=torch.float32,
)


def load_financial_data(path=None):
    """
    Load financial data JSON from the project root directory.
    """
    if path is None:
        current_file = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(current_file))
        path = os.path.join(project_root, "NOCFO.json")

    with open(path, "r") as f:
        return json.load(f)


def extract_metric_series(company_data, metric: str):
    """
    Extract net debet-credit time series for a given metric from the company's ledger.
    """
    ledger = company_data.get("ledger", [])
    series = []
    for acc in ledger:
        acc_key = acc["account_name"].lower().replace(" ", "_")
        if acc_key == metric:
            for entry in sorted(acc["entries"], key=lambda x: x["date"]):
                net = entry.get("debet", 0) - entry.get("credit", 0)
                series.append(net)
    return pd.Series(series)


def format_metric_name(metric: str) -> str:
    """
    Format metric name from snake_case to Title Case for display.
    """
    return metric.replace("_", " ").title()


def forecast_company_metric(company_name: str, metric: str, forecast_periods: int = 12):
    """
    Forecast a company's financial metric using Hugging Face Chronos.
    Returns forecasted median values and a base64-encoded PNG plot.
    """
    data = load_financial_data()
    company = data.get(company_name)
    if not company:
        raise ValueError(f"Company '{company_name}' not found in data.")

    ts = extract_metric_series(company, metric)
    if len(ts) < 10:
        raise ValueError(f"Chronos model requires at least 10 historical time points, but only {len(ts)} were found.")

    # Find actual start date from ledger
    ledger_entries = []
    for acc in company.get("ledger", []):
        acc_key = acc["account_name"].lower().replace(" ", "_")
        if acc_key == metric:
            ledger_entries = sorted(acc["entries"], key=lambda x: x["date"])
            break

    if len(ledger_entries) < len(ts):
        raise ValueError("Mismatch between extracted time series and ledger entries.")

    start_date = pd.to_datetime(ledger_entries[0]["date"])

    # Forecast
    context = torch.tensor(ts.values, dtype=torch.float32)
    quantiles, _ = pipeline.predict_quantiles(
        context=context,
        prediction_length=forecast_periods,
        quantile_levels=[0.1, 0.5, 0.9],
    )

    # Build timeline index
    history_index = pd.date_range(start=start_date, periods=len(ts), freq="MS")
    forecast_index = pd.date_range(start=history_index[-1] + pd.offsets.MonthBegin(), periods=forecast_periods, freq="MS")
    low, median, high = quantiles[0, :, 0], quantiles[0, :, 1], quantiles[0, :, 2]

    # Plot
    plt.figure(figsize=(10, 4))
    plt.plot(history_index, ts, label="History", color="royalblue", linewidth=2)
    plt.plot(forecast_index, median, label="Forecast (median)", color="tomato", linewidth=2)
    plt.fill_between(forecast_index, low, high, color="tomato", alpha=0.3, label="Prediction Interval")

    plt.title(f"{company_name} – Forecast of '{format_metric_name(metric)}'", fontsize=14)
    plt.ylabel("Amount", fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    plot_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    return {
        "historical": ts.tolist(),
        "forecast": median.tolist(),
        "plot_base64": plot_base64
    }
