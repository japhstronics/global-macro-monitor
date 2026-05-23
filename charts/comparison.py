"""
charts/comparison.py
====================
Plotly figure factories for the Country Comparison page.
Pure functions: DataFrame in -> Figure out. No Dash imports.
"""

from typing import Literal
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

MEDAL = {1:"🥇", 2:"🥈", 3:"🥉"}

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
)


def _colour(code, idx=0):
    return COUNTRY_COLOURS.get(code, PALETTE[idx % len(PALETTE)])


def _hex_rgba(hex_colour, alpha):
    h = hex_colour.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{alpha})"


def make_snapshot_bar(df, indicator, year, sort_order="desc"):
    """Horizontal bar — one bar per country for a chosen year, ranked."""
    if year not in df.index:
        available = df.index[df.index <= year]
        if available.empty:
            return go.Figure()
        year = int(available[-1])

    row = df.loc[year].dropna()
    if row.empty:
        return go.Figure()

    ascending  = (sort_order == "asc")
    row_sorted = row.sort_values(ascending=ascending)
    countries  = list(row_sorted.index)
    values     = list(row_sorted.values)
    dp         = indicator.decimal_places

    # Rank labels (1 = best, direction-aware)
    all_ranked = row.rank(ascending=indicator.invert_for_better, method="min")
    ranks      = {c: int(r) for c, r in all_ranked.items()}

    y_labels, bar_colours, border_colours = [], [], []
    for i, c in enumerate(countries):
        rank  = ranks.get(c, 0)
        medal = MEDAL.get(rank, f"#{rank}")
        name  = COUNTRIES.get(c, c)
        y_labels.append(f"{medal}  {c} — {name}")
        col = _colour(c, i)
        bar_colours.append(_hex_rgba(col, 0.80))
        border_colours.append(col)

    text_vals = [f"{v:,.{dp}f} {indicator.unit}" for v in values]

    fig = go.Figure(go.Bar(
        x           = values,
        y           = y_labels,
        orientation = "h",
        marker      = dict(color=bar_colours,
                           line=dict(color=border_colours, width=1.2)),
        text        = text_vals,
        textposition= "outside",
        textfont    = dict(size=11, color=TEXT_DIM),
        cliponaxis  = False,
        hovertemplate=(
            "<b>%{y}</b><br>"
            f"<b>%{{x:,.{dp}f}}</b> {indicator.unit}"
            "<extra></extra>"
        ),
    ))

    fig.add_vline(x=0, line_width=1, line_color=ZERO_LINE)

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text=f"<b>{indicator.label}</b> — {year}",
                   font=dict(size=15, color=TEXT), x=0.01, xanchor="left"),
        showlegend = False,
        height     = max(320, len(countries) * 54 + 110),
        xaxis      = dict(showgrid=True, gridcolor=GRID, zeroline=True,
                          zerolinecolor=ZERO_LINE, zerolinewidth=1,
                          tickfont=dict(size=11), title=indicator.unit),
        yaxis      = dict(showgrid=False, tickfont=dict(size=12),
                          automargin=True, title=None),
    )
    return fig


def make_grouped_bar(df, indicator, years, countries):
    """Grouped vertical bar — compare same countries across 2-3 chosen years."""
    valid_years = [y for y in years if y in df.index]
    if not valid_years or not countries:
        return go.Figure()

    YEAR_COLS = ["#4f8ef7","#f5c518","#50c87a","#f06060"]
    dp        = indicator.decimal_places
    fig       = go.Figure()

    for i, year in enumerate(valid_years):
        row    = df.loc[year]
        col    = YEAR_COLS[i % len(YEAR_COLS)]
        fig.add_trace(go.Bar(
            name         = str(year),
            x            = [COUNTRIES.get(c, c) for c in countries],
            y            = [row.get(c) for c in countries],
            marker_color = _hex_rgba(col, 0.80),
            marker_line  = dict(color=col, width=1),
            hovertemplate=(
                f"<b>%{{x}}</b> ({year})<br>"
                f"<b>%{{y:,.{dp}f}}</b> {indicator.unit}"
                "<extra></extra>"
            ),
        ))

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text=f"<b>{indicator.label}</b> — Multi-Year Comparison",
                   font=dict(size=15, color=TEXT), x=0.01, xanchor="left"),
        barmode    = "group",
        showlegend = True,
        legend     = dict(bgcolor="rgba(0,0,0,0)", borderwidth=0,
                          font=dict(size=11), orientation="h",
                          y=1.06, x=0, xanchor="left"),
        height = 440,
        xaxis  = dict(showgrid=False, tickfont=dict(size=11), title=None),
        yaxis  = dict(showgrid=True, gridcolor=GRID, tickfont=dict(size=11),
                      title=indicator.unit, zeroline=True, zerolinecolor=ZERO_LINE),
        margin = dict(l=60, r=30, t=70, b=40),
    )
    return fig


def make_rank_chart(df, indicator, countries):
    """Bump chart — each country's rank position over time. Rank 1 = best."""
    ascending = indicator.invert_for_better
    rank_rows = {}
    for year in df.index:
        row = df.loc[year].dropna()
        if not row.empty:
            rank_rows[year] = row.rank(ascending=ascending, method="min")

    if not rank_rows:
        return go.Figure()

    rank_df = pd.DataFrame(rank_rows).T
    fig     = go.Figure()
    n       = len([c for c in countries if c in rank_df.columns])

    for i, code in enumerate(countries):
        if code not in rank_df.columns:
            continue
        series = rank_df[code].dropna()
        col    = _colour(code, i)
        name   = COUNTRIES.get(code, code)
        fig.add_trace(go.Scatter(
            x    = series.index,
            y    = series.values,
            name = f"{code} — {name}",
            mode = "lines+markers",
            line = dict(color=col, width=2),
            marker = dict(color=col, size=7,
                          line=dict(color="rgba(0,0,0,0.4)", width=1)),
            hovertemplate=(
                f"<b>{name}</b><br>"
                "Year: %{x}<br>Rank: <b>#%{y:.0f}</b>"
                "<extra></extra>"
            ),
        ))

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text=f"<b>{indicator.short_label}</b> — Rank Over Time  (1 = best)",
                   font=dict(size=15, color=TEXT), x=0.01, xanchor="left"),
        showlegend = True,
        legend     = dict(bgcolor="rgba(0,0,0,0)", borderwidth=0,
                          font=dict(size=11), orientation="h",
                          y=1.06, x=0, xanchor="left"),
        height     = 400,
        xaxis      = dict(showgrid=True, gridcolor=GRID, zeroline=False,
                          tickfont=dict(size=11), title="Year"),
        yaxis      = dict(showgrid=True, gridcolor=GRID, autorange="reversed",
                          tickformat="d", dtick=1, title="Rank",
                          range=[n + 0.5, 0.5], tickfont=dict(size=11)),
        margin     = dict(l=60, r=30, t=70, b=40),
    )
    return fig
