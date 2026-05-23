"""
charts/heatmap.py
=================
Plotly figure factories for the Heat Map page.
Pure functions: DataFrame in -> Figure out. No Dash imports.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from data.indicators import Indicator, COUNTRIES

BG        = "#0f1117"
PAPER     = "#0f1117"
GRID      = "rgba(255,255,255,0.06)"
TEXT      = "#e0e0e0"
TEXT_DIM  = "rgba(224,224,224,0.45)"
FONT      = "Inter, -apple-system, sans-serif"

BASE_LAYOUT = dict(
    font          = dict(family=FONT, color=TEXT, size=12),
    paper_bgcolor = PAPER,
    plot_bgcolor  = BG,
    hoverlabel    = dict(
        bgcolor="rgba(26,29,39,0.95)",
        bordercolor="rgba(255,255,255,0.12)",
        font=dict(size=12, color=TEXT),
    ),
    margin = dict(l=20, r=20, t=70, b=60),
)

# Colour scales available to the user
COLOUR_SCALES = {
    "RdYlGn":   "RdYlGn",
    "RdYlGn_r": "RdYlGn_r",
    "Blues":    "Blues",
    "Plasma":   "plasma",
    "Viridis":  "Viridis",
    "RdBu":     "RdBu",
    "Spectral": "Spectral",
}


def _normalise_df(df: pd.DataFrame) -> pd.DataFrame:
    """Z-score normalise each column (country) independently."""
    return df.apply(lambda col: (col - col.mean()) / col.std(), axis=0)


def make_time_heatmap(
    df: pd.DataFrame,
    indicator: Indicator,
    countries: list[str],
    colour_scale: str = "RdYlGn",
    normalise: bool = False,
    show_values: bool = True,
    transpose: bool = False,
) -> go.Figure:
    """
    Countries x Years heatmap.

    Parameters
    ----------
    df           : Wide DataFrame — index=Year, columns=country codes
    indicator    : Indicator metadata
    countries    : Ordered list of country codes to show
    colour_scale : Plotly colour scale name
    normalise    : Z-score normalise per country (useful for cross-indicator comparison)
    show_values  : Annotate each cell with its value
    transpose    : Flip axes — Years on y, Countries on x
    """
    # Filter to selected countries in sidebar order
    cols    = [c for c in countries if c in df.columns]
    plot_df = df[cols].copy()

    if plot_df.empty:
        return go.Figure()

    if normalise:
        plot_df = _normalise_df(plot_df)

    # Matrix orientation
    if transpose:
        # x = countries, y = years
        z      = plot_df.values.T          # shape: countries × years
        x_vals = [str(yr) for yr in plot_df.index]
        y_vals = [f"{c} — {COUNTRIES.get(c,c)}" for c in cols]
        x_title, y_title = "Year", ""
    else:
        # x = years (default), y = countries
        z      = plot_df.values            # shape: years × countries
        x_vals = [f"{c} — {COUNTRIES.get(c,c)}" for c in cols]
        y_vals = [str(yr) for yr in plot_df.index]
        x_title, y_title = "", "Year"

    dp          = indicator.decimal_places if not normalise else 2
    unit_label  = "z-score" if normalise else indicator.unit

    # Build annotation text matrix
    text_matrix = []
    for row in z:
        text_row = []
        for v in row:
            text_row.append(f"{v:.{dp}f}" if not np.isnan(v) else "")
        text_matrix.append(text_row)

    # Invert colour scale if lower = better
    scale = colour_scale
    if indicator.invert_for_better and "_r" not in scale:
        scale = scale + "_r"

    heatmap = go.Heatmap(
        z            = z,
        x            = x_vals,
        y            = y_vals,
        colorscale   = scale,
        hoverongaps  = False,
        text         = text_matrix if show_values else None,
        texttemplate = "%{text}" if show_values else None,
        textfont     = dict(size=10, color="rgba(0,0,0,0.75)"),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "%{y}<br>"
            f"<b>%{{z:.{dp}f}}</b> {unit_label}"
            "<extra></extra>"
        ),
        colorbar=dict(
            title      = dict(text=unit_label, font=dict(size=11, color=TEXT_DIM)),
            tickfont   = dict(size=10, color=TEXT_DIM),
            thickness  = 14,
            len        = 0.85,
            outlinewidth = 0,
            bgcolor    = "rgba(0,0,0,0)",
        ),
    )

    title_suffix = " (Z-score normalised)" if normalise else ""
    fig = go.Figure(heatmap)

    cell_h   = max(28, min(52, 600 // max(len(y_vals), 1)))
    height   = max(380, len(y_vals) * cell_h + 120)

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(
            text    = f"<b>{indicator.label}</b>{title_suffix}",
            font    = dict(size=15, color=TEXT),
            x=0.01, xanchor="left",
        ),
        height = height,
        xaxis  = dict(
            title        = x_title,
            tickfont     = dict(size=10),
            tickangle    = -35 if not transpose else 0,
            showgrid     = False,
            side         = "bottom",
            automargin   = True,
        ),
        yaxis  = dict(
            title      = y_title,
            tickfont   = dict(size=11),
            showgrid   = False,
            automargin = True,
            autorange  = "reversed",
        ),
    )
    return fig


def make_correlation_heatmap(
    df: pd.DataFrame,
    indicator: Indicator,
    countries: list[str],
    colour_scale: str = "RdBu",
) -> go.Figure:
    """
    Pearson correlation matrix — how synchronised are countries' cycles?
    Cells annotated with r values. Diagonal always = 1.
    """
    cols    = [c for c in countries if c in df.columns]
    plot_df = df[cols].dropna(how="all")

    if plot_df.shape[1] < 2:
        return go.Figure()

    corr  = plot_df.corr().round(3)
    codes = list(corr.columns)
    labels = [f"{c} — {COUNTRIES.get(c,c)}" for c in codes]

    text_matrix = [[f"{v:.2f}" for v in row] for row in corr.values]

    heatmap = go.Heatmap(
        z            = corr.values,
        x            = labels,
        y            = labels,
        zmin         = -1,
        zmax         = 1,
        colorscale   = colour_scale,
        hoverongaps  = False,
        text         = text_matrix,
        texttemplate = "%{text}",
        textfont     = dict(size=11),
        hovertemplate=(
            "%{y}<br>vs %{x}<br>"
            "r = <b>%{z:.3f}</b>"
            "<extra></extra>"
        ),
        colorbar=dict(
            title      = dict(text="r", font=dict(size=11, color=TEXT_DIM)),
            tickfont   = dict(size=10, color=TEXT_DIM),
            tickvals   = [-1, -0.5, 0, 0.5, 1],
            ticktext   = ["-1", "-0.5", "0", "+0.5", "+1"],
            thickness  = 14,
            len        = 0.85,
            outlinewidth = 0,
            bgcolor    = "rgba(0,0,0,0)",
        ),
    )

    n      = len(codes)
    size   = max(380, n * 58 + 120)

    fig = go.Figure(heatmap)
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(
            text    = f"<b>{indicator.short_label}</b> — Cross-Country Correlation",
            font    = dict(size=15, color=TEXT),
            x=0.01, xanchor="left",
        ),
        height = size,
        width  = None,
        xaxis  = dict(tickfont=dict(size=10), tickangle=-35,
                      showgrid=False, automargin=True),
        yaxis  = dict(tickfont=dict(size=10), showgrid=False,
                      automargin=True, autorange="reversed"),
    )
    return fig


def make_missing_data_heatmap(
    df: pd.DataFrame,
    indicator: Indicator,
    countries: list[str],
) -> go.Figure:
    """
    Data coverage heatmap — which country/year cells have real data vs gaps.
    Green = data present, Red = missing.
    """
    cols    = [c for c in countries if c in df.columns]
    plot_df = df[cols].copy()

    if plot_df.empty:
        return go.Figure()

    has_data     = (~plot_df.isna()).astype(int)  # 1 = present, 0 = missing
    pct_coverage = (has_data.sum() / len(has_data) * 100).round(1)

    x_vals = [f"{c}  ({pct_coverage.get(c,0):.0f}%)" for c in cols]
    y_vals = [str(yr) for yr in plot_df.index]

    text_matrix = [
        ["✓" if v == 1 else "—" for v in row]
        for row in has_data.values
    ]

    fig = go.Figure(go.Heatmap(
        z            = has_data.values,
        x            = x_vals,
        y            = y_vals,
        colorscale   = [[0, "rgba(240,96,96,0.35)"], [1, "rgba(80,200,122,0.55)"]],
        zmin=0, zmax=1,
        showscale    = False,
        text         = text_matrix,
        texttemplate = "%{text}",
        textfont     = dict(size=10),
        hovertemplate=(
            "<b>%{x}</b> — %{y}<br>"
            "%{text}"
            "<extra></extra>"
        ),
    ))

    n_years = len(plot_df)
    height  = max(360, n_years * 20 + 120)

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(
            text    = f"<b>Data Coverage</b> — {indicator.short_label}  (✓ = available)",
            font    = dict(size=15, color=TEXT),
            x=0.01, xanchor="left",
        ),
        height = height,
        xaxis  = dict(tickfont=dict(size=10), tickangle=-35,
                      showgrid=False, automargin=True),
        yaxis  = dict(tickfont=dict(size=10), showgrid=False,
                      automargin=True, autorange="reversed"),
    )
    return fig
