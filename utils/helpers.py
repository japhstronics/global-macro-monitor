"""
utils/helpers.py
================
KPI formatting, delta calculations, and reusable layout helpers
shared across all dashboard pages.
"""

import pandas as pd
from dash import html

from data.indicators import Indicator, COUNTRIES


def latest_and_delta(
    series: pd.Series,
    periods: int = 1,
) -> tuple[float | None, float | None, int | None]:
    """
    Return (latest_value, yoy_delta, latest_year).
    Any element is None when data is insufficient.
    """
    clean = series.dropna()
    if clean.empty:
        return None, None, None

    latest      = float(clean.iloc[-1])
    latest_year = int(clean.index[-1])
    delta       = float(latest - clean.iloc[-1 - periods]) if len(clean) > periods else None

    return latest, delta, latest_year


def fmt(value: float, indicator: Indicator) -> str:
    dp = indicator.decimal_places
    if dp == 0:
        return f"{value:,.0f}"
    return f"{value:,.{dp}f}"


def kpi_card(
    country_code: str,
    value: float | None,
    delta: float | None,
    year: int | None,
    indicator: Indicator,
) -> html.Div:
    """
    Build a single KPI card div.
    Green delta = good unless indicator.invert_for_better is True.
    """
    country_name = COUNTRIES.get(country_code, country_code)

    # ── No data ───────────────────────────────────────────────
    if value is None:
        return html.Div(
            className="kpi-card kpi-nodata",
            children=[
                html.Div(country_code, className="kpi-code"),
                html.Div(country_name, className="kpi-name"),
                html.Div("No data", className="kpi-value kpi-dim"),
            ],
        )

    val_str  = f"{fmt(value, indicator)} {indicator.unit}"
    year_str = str(year) if year else ""

    # ── Delta ─────────────────────────────────────────────────
    delta_el = None
    if delta is not None:
        positive_is_good = not indicator.invert_for_better
        is_positive      = delta > 0
        good             = (is_positive and positive_is_good) or (not is_positive and not positive_is_good)

        arrow   = "▲" if is_positive else "▼"
        sign    = "+" if is_positive else ""
        colour  = "#50c87a" if good else "#f06060"
        dp      = indicator.decimal_places
        delta_el = html.Div(
            f"{arrow} {sign}{delta:.{dp}f} YoY",
            className="kpi-delta",
            style={"color": colour},
        )

    return html.Div(
        className="kpi-card",
        children=[
            html.Div(country_code, className="kpi-code"),
            html.Div(country_name, className="kpi-name"),
            html.Div(val_str, className="kpi-value"),
            html.Div(year_str, className="kpi-year"),
            delta_el or html.Div(),
        ],
    )


def no_data_message(reason: str = "") -> html.Div:
    """Consistent empty-state placeholder."""
    return html.Div(
        className="empty-state",
        children=[
            html.Div("⚠", style={"fontSize": "2rem", "marginBottom": "0.5rem"}),
            html.Div("No data available", style={"fontWeight": 600, "marginBottom": "4px"}),
            html.Div(reason, style={"fontSize": "0.82rem", "color": "rgba(224,224,224,0.4)"}),
        ],
    )
