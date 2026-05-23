"""
charts/scatter.py
=================
Plotly figure factories for the Scatter / Phillips Curve page.
Pure functions: DataFrames in -> Figure out. No Dash imports.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from data.indicators import Indicator, COUNTRIES

BG        = "#0f1117"
PAPER     = "#0f1117"
GRID      = "rgba(255,255,255,0.06)"
ZERO_LINE = "rgba(255,255,255,0.14)"
TEXT      = "#e0e0e0"
TEXT_DIM  = "rgba(224,224,224,0.45)"
FONT      = "Inter, -apple-system, sans-serif"

PALETTE = [
    "#4f8ef7","#f06060","#50c87a","#f5c518",
    "#c471ed","#12c2e9","#fa8231","#43e97b",
    "#a29bfe","#fd79a8","#00cec9","#e17055",
    "#6c5ce7","#fdcb6e","#74b9ff",
]

COUNTRY_COLOURS = {
    "US":"#4f8ef7","GB":"#f06060","DE":"#50c87a",
    "JP":"#f5c518","CN":"#e31a1c","IN":"#fa8231",
    "BR":"#2ecc71","ZA":"#00b894","AU":"#8e44ad",
    "CA":"#e377c2","NG":"#27ae60","KE":"#17becf",
    "FR":"#5c7cfa","SG":"#cc0001","AE":"#1abc9c",
}

BASE_LAYOUT = dict(
    font          = dict(family=FONT, color=TEXT, size=12),
    paper_bgcolor = PAPER,
    plot_bgcolor  = BG,
    hovermode     = "closest",
    hoverlabel    = dict(
        bgcolor="rgba(26,29,39,0.95)",
        bordercolor="rgba(255,255,255,0.12)",
        font=dict(size=12, color=TEXT),
    ),
    margin = dict(l=70, r=30, t=70, b=70),
)


def _colour(code, idx=0):
    return COUNTRY_COLOURS.get(code, PALETTE[idx % len(PALETTE)])


def _hex_rgba(hex_colour, alpha):
    h = hex_colour.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{alpha})"


def _ols(x, y):
    """Return (slope, intercept, r_squared) for a simple OLS regression."""
    mask = ~(np.isnan(x) | np.isnan(y))
    x, y = x[mask], y[mask]
    if len(x) < 3:
        return None, None, None
    xm, ym  = x.mean(), y.mean()
    slope   = np.sum((x - xm) * (y - ym)) / np.sum((x - xm) ** 2)
    intercept = ym - slope * xm
    y_hat   = slope * x + intercept
    ss_res  = np.sum((y - y_hat) ** 2)
    ss_tot  = np.sum((y - ym) ** 2)
    r2      = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    return float(slope), float(intercept), float(r2)


# ── Single-year snapshot scatter ──────────────────────────────────────────────
def make_snapshot_scatter(
    df_x: pd.DataFrame,
    df_y: pd.DataFrame,
    ind_x: Indicator,
    ind_y: Indicator,
    year: int,
    countries: list[str],
    show_labels: bool = True,
    show_regression: bool = True,
) -> go.Figure:
    """
    Country bubbles: x = ind_x, y = ind_y for a single year.
    Optional OLS line + R² annotation.
    """
    points = []
    for i, code in enumerate(countries):
        x_val = df_x[code].get(year) if code in df_x.columns else None
        y_val = df_y[code].get(year) if code in df_y.columns else None
        if x_val is not None and y_val is not None and not (np.isnan(x_val) or np.isnan(y_val)):
            points.append(dict(
                code=code,
                name=COUNTRIES.get(code, code),
                x=float(x_val),
                y=float(y_val),
                colour=_colour(code, i),
            ))

    fig = go.Figure()

    if not points:
        return fig

    # ── Country bubbles ────────────────────────────────────────
    for p in points:
        fig.add_trace(go.Scatter(
            x    = [p["x"]],
            y    = [p["y"]],
            mode = "markers+text" if show_labels else "markers",
            name = f"{p['code']} — {p['name']}",
            marker = dict(
                size   = 14,
                color  = _hex_rgba(p["colour"], 0.85),
                line   = dict(color=p["colour"], width=1.5),
            ),
            text          = [p["code"]],
            textposition  = "top center",
            textfont      = dict(size=10, color=TEXT_DIM),
            hovertemplate = (
                f"<b>{p['name']}</b><br>"
                f"{ind_x.short_label}: <b>{p['x']:.{ind_x.decimal_places}f}</b> {ind_x.unit}<br>"
                f"{ind_y.short_label}: <b>{p['y']:.{ind_y.decimal_places}f}</b> {ind_y.unit}"
                "<extra></extra>"
            ),
            showlegend = True,
        ))

    # ── OLS regression line ────────────────────────────────────
    if show_regression and len(points) >= 3:
        xs = np.array([p["x"] for p in points])
        ys = np.array([p["y"] for p in points])
        slope, intercept, r2 = _ols(xs, ys)

        if slope is not None:
            x_line = np.linspace(xs.min(), xs.max(), 80)
            y_line = slope * x_line + intercept

            fig.add_trace(go.Scatter(
                x    = x_line,
                y    = y_line,
                mode = "lines",
                name = f"OLS fit  (R²={r2:.3f})",
                line = dict(color="rgba(224,224,224,0.35)", width=1.5, dash="dot"),
                hoverinfo = "skip",
                showlegend = True,
            ))

            # R² annotation in top-right corner
            fig.add_annotation(
                xref="paper", yref="paper",
                x=0.99, y=0.99,
                xanchor="right", yanchor="top",
                text=f"R² = {r2:.3f}  ·  slope = {slope:.3f}",
                showarrow=False,
                font=dict(size=11, color=TEXT_DIM),
                bgcolor="rgba(26,29,39,0.7)",
                bordercolor="rgba(255,255,255,0.1)",
                borderwidth=1,
                borderpad=6,
            )

    # ── Zero reference lines ───────────────────────────────────
    fig.add_hline(y=0, line_width=1, line_color=ZERO_LINE)
    fig.add_vline(x=0, line_width=1, line_color=ZERO_LINE)

    fig.update_layout(
        **BASE_LAYOUT,
        title = dict(
            text    = f"<b>{ind_x.short_label}</b> vs <b>{ind_y.short_label}</b> — {year}",
            font    = dict(size=15, color=TEXT),
            x=0.01, xanchor="left",
        ),
        height = 500,
        xaxis  = dict(
            title    = f"{ind_x.short_label} ({ind_x.unit})",
            showgrid = True, gridcolor=GRID,
            zeroline = True, zerolinecolor=ZERO_LINE,
            tickfont = dict(size=11),
        ),
        yaxis  = dict(
            title    = f"{ind_y.short_label} ({ind_y.unit})",
            showgrid = True, gridcolor=GRID,
            zeroline = True, zerolinecolor=ZERO_LINE,
            tickfont = dict(size=11),
        ),
        legend = dict(
            bgcolor="rgba(0,0,0,0)", borderwidth=0,
            font=dict(size=10), orientation="v",
            x=1.02, y=1, xanchor="left",
        ),
    )
    return fig


# ── Animated scatter (Play button through years) ──────────────────────────────
def make_animated_scatter(
    df_x: pd.DataFrame,
    df_y: pd.DataFrame,
    ind_x: Indicator,
    ind_y: Indicator,
    countries: list[str],
    start_year: int,
    end_year: int,
) -> go.Figure:
    """
    Animated bubble chart with a Play/Pause slider through years.
    Each frame = one year. Country bubbles move as data changes.
    """
    years  = sorted([y for y in df_x.index if start_year <= y <= end_year and y in df_y.index])
    if not years:
        return go.Figure()

    # Global axis range (fixed across all frames for stable axes)
    all_x, all_y = [], []
    for code in countries:
        if code in df_x.columns:
            all_x.extend(df_x[code].dropna().values)
        if code in df_y.columns:
            all_y.extend(df_y[code].dropna().values)

    x_pad = (max(all_x) - min(all_x)) * 0.12 if all_x else 1
    y_pad = (max(all_y) - min(all_y)) * 0.12 if all_y else 1
    x_range = [min(all_x) - x_pad, max(all_x) + x_pad] if all_x else [-1, 1]
    y_range = [min(all_y) - y_pad, max(all_y) + y_pad] if all_y else [-1, 1]

    # ── Build frames ──────────────────────────────────────────
    frames = []
    for year in years:
        frame_data = []
        for i, code in enumerate(countries):
            x_val = df_x[code].get(year) if code in df_x.columns else None
            y_val = df_y[code].get(year) if code in df_y.columns else None
            colour = _colour(code, i)
            frame_data.append(go.Scatter(
                x    = [float(x_val)] if x_val is not None and not np.isnan(x_val) else [None],
                y    = [float(y_val)] if y_val is not None and not np.isnan(y_val) else [None],
                mode = "markers+text",
                name = code,
                marker = dict(size=14, color=_hex_rgba(colour, 0.85),
                              line=dict(color=colour, width=1.5)),
                text         = [code],
                textposition = "top center",
                textfont     = dict(size=10, color=TEXT_DIM),
                hovertemplate=(
                    f"<b>{COUNTRIES.get(code,code)}</b> ({year})<br>"
                    f"{ind_x.short_label}: <b>%{{x:.{ind_x.decimal_places}f}}</b> {ind_x.unit}<br>"
                    f"{ind_y.short_label}: <b>%{{y:.{ind_y.decimal_places}f}}</b> {ind_y.unit}"
                    "<extra></extra>"
                ),
            ))
        frames.append(go.Frame(data=frame_data, name=str(year)))

    # ── Initial traces (first year) ───────────────────────────
    fig = go.Figure(data=frames[0].data, frames=frames)

    # ── Slider + buttons ──────────────────────────────────────
    sliders = [dict(
        active     = 0,
        steps      = [dict(method="animate", label=str(y),
                           args=[[str(y)], dict(mode="immediate", frame=dict(duration=500),
                                                transition=dict(duration=300))])
                      for y in years],
        x=0, y=0, len=1.0,
        currentvalue = dict(prefix="Year: ", font=dict(size=13, color=TEXT_DIM),
                             visible=True, xanchor="center"),
        pad          = dict(b=10, t=45),
        bgcolor      = "rgba(255,255,255,0.05)",
        bordercolor  = "rgba(255,255,255,0.1)",
        tickcolor    = "rgba(255,255,255,0.2)",
        font         = dict(color=TEXT_DIM, size=10),
    )]

    update_menus = [dict(
        type       = "buttons",
        showactive = False,
        x=0.05, y=1.08, xanchor="left",
        buttons=[
            dict(label="▶ Play",
                 method="animate",
                 args=[None, dict(frame=dict(duration=700, redraw=True),
                                  fromcurrent=True, transition=dict(duration=300))]),
            dict(label="⏸ Pause",
                 method="animate",
                 args=[[None], dict(frame=dict(duration=0, redraw=False),
                                     mode="immediate", transition=dict(duration=0))]),
        ],
        font      = dict(size=11, color=TEXT),
        bgcolor   = "rgba(255,255,255,0.06)",
        bordercolor = "rgba(255,255,255,0.15)",
    )]

    fig.update_layout(
        **BASE_LAYOUT,
        title = dict(
            text  = f"<b>{ind_x.short_label}</b> vs <b>{ind_y.short_label}</b> — Animated",
            font  = dict(size=15, color=TEXT),
            x=0.01, xanchor="left",
        ),
        height       = 540,
        margin       = dict(l=70, r=30, t=90, b=100),
        sliders      = sliders,
        updatemenus  = update_menus,
        xaxis = dict(title=f"{ind_x.short_label} ({ind_x.unit})",
                     range=x_range, showgrid=True, gridcolor=GRID,
                     zeroline=True, zerolinecolor=ZERO_LINE, tickfont=dict(size=11)),
        yaxis = dict(title=f"{ind_y.short_label} ({ind_y.unit})",
                     range=y_range, showgrid=True, gridcolor=GRID,
                     zeroline=True, zerolinecolor=ZERO_LINE, tickfont=dict(size=11)),
        legend = dict(bgcolor="rgba(0,0,0,0)", borderwidth=0,
                      font=dict(size=10), orientation="v",
                      x=1.02, y=1, xanchor="left"),
    )
    return fig


# ── Time-path chart: one country's journey through the scatter space ──────────
def make_time_path(
    df_x: pd.DataFrame,
    df_y: pd.DataFrame,
    ind_x: Indicator,
    ind_y: Indicator,
    countries: list[str],
    start_year: int,
    end_year: int,
) -> go.Figure:
    """
    Each country's data points connected chronologically — reveals
    how the relationship between two indicators evolved over time.
    """
    fig = go.Figure()

    for i, code in enumerate(countries):
        if code not in df_x.columns or code not in df_y.columns:
            continue

        xs = df_x[code].dropna()
        ys = df_y[code].dropna()
        common = sorted(set(xs.index) & set(ys.index) &
                        set(range(start_year, end_year + 1)))
        if len(common) < 2:
            continue

        xv     = [float(xs[yr]) for yr in common]
        yv     = [float(ys[yr]) for yr in common]
        colour = _colour(code, i)
        name   = COUNTRIES.get(code, code)

        # Line path
        fig.add_trace(go.Scatter(
            x         = xv, y=yv,
            mode      = "lines",
            name      = f"{code} path",
            line      = dict(color=_hex_rgba(colour, 0.35), width=1.5, dash="dot"),
            showlegend = False,
            hoverinfo  = "skip",
        ))

        # Dots — sized by recency (most recent = largest)
        sizes = [7 + 6 * (j / max(len(common)-1,1)) for j in range(len(common))]
        fig.add_trace(go.Scatter(
            x    = xv, y=yv,
            mode = "markers",
            name = f"{code} — {name}",
            marker = dict(
                size   = sizes,
                color  = [_hex_rgba(colour, 0.4 + 0.55 * j / max(len(common)-1,1))
                           for j in range(len(common))],
                line   = dict(color=colour, width=1),
            ),
            text = [str(yr) for yr in common],
            hovertemplate=(
                f"<b>{name}</b> (%{{text}})<br>"
                f"{ind_x.short_label}: <b>%{{x:.{ind_x.decimal_places}f}}</b> {ind_x.unit}<br>"
                f"{ind_y.short_label}: <b>%{{y:.{ind_y.decimal_places}f}}</b> {ind_y.unit}"
                "<extra></extra>"
            ),
            showlegend = True,
        ))

        # Label the most recent point
        fig.add_annotation(
            x=xv[-1], y=yv[-1],
            text=f"<b>{code}</b> {common[-1]}",
            showarrow=True, arrowhead=0,
            arrowcolor=_hex_rgba(colour, 0.5),
            ax=18, ay=-18,
            font=dict(size=9, color=colour),
        )

    fig.add_hline(y=0, line_width=1, line_color=ZERO_LINE)
    fig.add_vline(x=0, line_width=1, line_color=ZERO_LINE)

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(
            text  = f"<b>{ind_x.short_label}</b> vs <b>{ind_y.short_label}</b> — Time Path  ({start_year}–{end_year})",
            font  = dict(size=15, color=TEXT),
            x=0.01, xanchor="left",
        ),
        height = 520,
        xaxis  = dict(title=f"{ind_x.short_label} ({ind_x.unit})",
                      showgrid=True, gridcolor=GRID,
                      zeroline=True, zerolinecolor=ZERO_LINE, tickfont=dict(size=11)),
        yaxis  = dict(title=f"{ind_y.short_label} ({ind_y.unit})",
                      showgrid=True, gridcolor=GRID,
                      zeroline=True, zerolinecolor=ZERO_LINE, tickfont=dict(size=11)),
        legend = dict(bgcolor="rgba(0,0,0,0)", borderwidth=0,
                      font=dict(size=10), orientation="v",
                      x=1.02, y=1, xanchor="left"),
    )
    return fig
