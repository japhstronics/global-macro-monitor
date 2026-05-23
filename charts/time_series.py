"""
charts/time_series.py
=====================
Plotly figure factories for the Time Series page.
All functions are pure: DataFrame in → Figure out. No Dash imports here.
"""

from typing import Optional
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data.indicators import Indicator, COUNTRIES

# ── Shared dark theme tokens ───────────────────────────────────────────────────
BG          = "#0f1117"
PAPER       = "#0f1117"
GRID        = "rgba(255,255,255,0.06)"
ZERO_LINE   = "rgba(255,255,255,0.14)"
TEXT        = "#e0e0e0"
TEXT_DIM    = "rgba(224,224,224,0.45)"
FONT        = "Inter, -apple-system, sans-serif"
ACCENT      = "#4f8ef7"

PALETTE = [
    "#4f8ef7", "#f06060", "#50c87a", "#f5c518",
    "#c471ed", "#12c2e9", "#fa8231", "#43e97b",
    "#a29bfe", "#fd79a8", "#00cec9", "#e17055",
    "#6c5ce7", "#fdcb6e", "#74b9ff",
]

COUNTRY_COLOURS: dict[str, str] = {
    "US": "#4f8ef7", "GB": "#f06060", "DE": "#50c87a",
    "JP": "#f5c518", "CN": "#e31a1c", "IN": "#fa8231",
    "BR": "#2ecc71", "ZA": "#00b894", "AU": "#8e44ad",
    "CA": "#e377c2", "NG": "#27ae60", "KE": "#17becf",
    "FR": "#5c7cfa", "SG": "#cc0001", "AE": "#1abc9c",
}


def _colour(code: str, idx: int) -> str:
    return COUNTRY_COLOURS.get(code, PALETTE[idx % len(PALETTE)])


BASE = dict(
    font        = dict(family=FONT, color=TEXT, size=12),
    paper_bgcolor = PAPER,
    plot_bgcolor  = BG,
    hovermode   = "x unified",
    hoverlabel  = dict(
        bgcolor="rgba(26,29,39,0.95)",
        bordercolor="rgba(255,255,255,0.12)",
        font=dict(size=12, color=TEXT),
    ),
    margin = dict(l=60, r=20, t=60, b=50),
    legend = dict(
        bgcolor="rgba(0,0,0,0)",
        borderwidth=0,
        font=dict(size=11),
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
    ),
    xaxis = dict(
        showgrid=True, gridcolor=GRID, zeroline=False,
        tickfont=dict(size=11),
        tickcolor="rgba(255,255,255,0.2)",
        linecolor="rgba(255,255,255,0.08)",
    ),
    yaxis = dict(
        showgrid=True, gridcolor=GRID,
        zeroline=True, zerolinecolor=ZERO_LINE, zerolinewidth=1,
        tickfont=dict(size=11),
        tickcolor="rgba(255,255,255,0.2)",
        linecolor="rgba(255,255,255,0.08)",
    ),
)


# ── Main time-series chart ────────────────────────────────────────────────────
def make_time_series(
    df: pd.DataFrame,
    indicator: Indicator,
    show_ma: bool = False,
    ma_window: int = 3,
    selected_countries: Optional[list[str]] = None,
) -> go.Figure:
    """
    Multi-country line chart with optional rolling-average overlay.

    Parameters
    ----------
    df               : Wide DataFrame — index=Year, columns=country codes
    indicator        : Indicator metadata object
    show_ma          : Overlay 3-year moving average
    ma_window        : Rolling window size (default 3)
    selected_countries : Order of countries for colour assignment
    """
    fig = go.Figure()
    cols = selected_countries or list(df.columns)

    for i, code in enumerate(cols):
        if code not in df.columns:
            continue
        series = df[code].dropna()
        if series.empty:
            continue

        colour  = _colour(code, i)
        country = COUNTRIES.get(code, code)
        dp      = indicator.decimal_places

        # ── Raw line ──────────────────────────────────────────
        fig.add_trace(go.Scatter(
            x    = series.index,
            y    = series.values,
            name = f"{code} — {country}",
            mode = "lines",
            line = dict(color=colour, width=2),
            hovertemplate=(
                f"<b>{country}</b><br>"
                f"%{{x}}: <b>%{{y:.{dp}f}}</b> {indicator.unit}"
                "<extra></extra>"
            ),
        ))

        # ── Moving average overlay ────────────────────────────
        if show_ma and len(series) >= ma_window:
            ma = series.rolling(ma_window, min_periods=1).mean()
            fig.add_trace(go.Scatter(
                x    = ma.index,
                y    = ma.values,
                name = f"{code} {ma_window}yr MA",
                mode = "lines",
                line = dict(color=colour, width=1.5, dash="dot"),
                opacity=0.55,
                hovertemplate=(
                    f"<b>{country} ({ma_window}yr avg)</b><br>"
                    f"%{{x}}: <b>%{{y:.{dp}f}}</b> {indicator.unit}"
                    "<extra></extra>"
                ),
                showlegend=False,
            ))

    # ── Layout ────────────────────────────────────────────────
    fig.update_layout(
        **BASE,
        title=dict(
            text  = f"<b>{indicator.label}</b>",
            font  = dict(size=15, color=TEXT),
            x     = 0.01,
            xanchor = "left",
        ),
        yaxis_title = indicator.unit,
    )

    # ── Range selector ────────────────────────────────────────
    fig.update_xaxes(
        rangeslider_visible=False,
        rangeselector=dict(
            bgcolor      = "rgba(255,255,255,0.05)",
            activecolor  = ACCENT,
            bordercolor  = "rgba(255,255,255,0.1)",
            borderwidth  = 1,
            font         = dict(size=11, color=TEXT_DIM),
            buttons=[
                dict(count=5,  label="5Y",  step="year", stepmode="backward"),
                dict(count=10, label="10Y", step="year", stepmode="backward"),
                dict(count=15, label="15Y", step="year", stepmode="backward"),
                dict(label="All", step="all"),
            ],
        ),
    )

    return fig


# ── Helper: hex colour → rgba string ─────────────────────────────────────────
def _hex_to_rgba(hex_colour: str, alpha: float) -> str:
    """Convert '#4f8ef7' + alpha 0.1 → 'rgba(79,142,247,0.1)'."""
    h = hex_colour.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ── Individual country mini-chart (sparkline) ─────────────────────────────────
def make_country_sparkline(
    series: pd.Series,
    country_code: str,
    indicator: Indicator,
) -> go.Figure:
    """Single-country compact line chart with area fill."""
    colour    = _colour(country_code, 0)
    dp        = indicator.decimal_places
    fill_rgba = _hex_to_rgba(colour, 0.10)

    fig = go.Figure(go.Scatter(
        x             = series.index,
        y             = series.values,
        mode          = "lines",
        line          = dict(color=colour, width=1.8),
        fill          = "tozeroy",
        fillcolor     = fill_rgba,
        hovertemplate = f"%{{x}}: <b>%{{y:.{dp}f}}</b> {indicator.unit}<extra></extra>",
    ))

    # Build layout WITHOUT xaxis/yaxis from BASE to avoid duplicate-kwarg error,
    # then set them explicitly.

    SPARKLINE_BASE = {
    k: v for k, v in BASE.items()
    if k not in ("xaxis", "yaxis", "margin")
    }

    fig.update_layout(
        **SPARKLINE_BASE,
        title      = dict(text=COUNTRIES.get(country_code, country_code),
                          font=dict(size=12, color=TEXT), x=0.01),
        margin     = dict(l=40, r=10, t=35, b=30),
        showlegend = False,
        height     = 160,
        xaxis      = dict(**BASE["xaxis"], showticklabels=True),
        yaxis      = dict(**BASE["yaxis"], title=None),
    )
    
    return fig
