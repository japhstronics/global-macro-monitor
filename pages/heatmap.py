"""
pages/heatmap.py
================
Page 3 — Heat Map
Three views: time heatmap, correlation matrix, data coverage.
"""

import pandas as pd
from dash import register_page, callback, html, dcc, Input, Output

from data.indicators import INDICATORS
from data.fetcher    import fetch_indicator
from charts.heatmap  import (
    make_time_heatmap,
    make_correlation_heatmap,
    make_missing_data_heatmap,
    COLOUR_SCALES,
)
from utils.helpers import latest_and_delta, kpi_card, no_data_message

register_page(
    __name__,
    path  = "/heatmap",
    name  = "Heat Map",
    title = "Heat Map — Global Macro Monitor",
    order = 3,
)

# ── Colour scale options for dropdown ─────────────────────────────────────────
SCALE_OPTIONS = [{"label": k, "value": k} for k in COLOUR_SCALES]

# ── Layout ────────────────────────────────────────────────────────────────────
layout = html.Div(
    className="page-wrap",
    children=[

        # ── Page header ────────────────────────────────────────
        html.Div(
            className="page-header",
            children=[
                html.H1(id="hm-title", className="page-title"),
                html.Div(id="hm-subtitle", className="page-subtitle"),
            ],
        ),

        # ── KPI strip ──────────────────────────────────────────
        html.Div(id="hm-kpi-strip", className="kpi-strip"),

        # ── Toolbar ────────────────────────────────────────────
        html.Div(
            className="toolbar",
            children=[
                html.Div(
                    className="toolbar-left",
                    style={"flexWrap": "wrap", "gap": "18px"},
                    children=[

                        # View selector
                        html.Div(
                            style={"display":"flex","alignItems":"center","gap":"8px"},
                            children=[
                                html.Label("View:", className="toolbar-label"),
                                dcc.RadioItems(
                                    id="hm-view",
                                    options=[
                                        {"label": "Time heatmap",    "value": "time"},
                                        {"label": "Correlation",     "value": "corr"},
                                        {"label": "Data coverage",   "value": "coverage"},
                                    ],
                                    value="time",
                                    inline=True,
                                    inputStyle={"marginRight": "4px"},
                                    labelStyle={"marginRight": "14px", "fontSize": "0.82rem"},
                                ),
                            ],
                        ),

                        # Colour scale — hidden for coverage view
                        html.Div(
                            id="hm-scale-wrap",
                            style={"display":"flex","alignItems":"center","gap":"8px"},
                            children=[
                                html.Label("Colour scale:", className="toolbar-label"),
                                dcc.Dropdown(
                                    id="hm-colour-scale",
                                    options=SCALE_OPTIONS,
                                    value="RdYlGn",
                                    clearable=False,
                                    searchable=False,
                                    style={"width": "130px", "fontSize": "0.82rem"},
                                ),
                            ],
                        ),

                        # Normalise toggle — time view only
                        html.Div(
                            id="hm-normalise-wrap",
                            style={"display":"flex","alignItems":"center","gap":"8px"},
                            children=[
                                html.Label("Normalise:", className="toolbar-label"),
                                dcc.RadioItems(
                                    id="hm-normalise",
                                    options=[
                                        {"label": "Raw values",  "value": "raw"},
                                        {"label": "Z-score",     "value": "z"},
                                    ],
                                    value="raw",
                                    inline=True,
                                    inputStyle={"marginRight": "4px"},
                                    labelStyle={"marginRight": "14px", "fontSize": "0.82rem"},
                                ),
                            ],
                        ),

                        # Annotate cells — time view only
                        html.Div(
                            id="hm-annotate-wrap",
                            style={"display":"flex","alignItems":"center","gap":"8px"},
                            children=[
                                html.Label("Cell values:", className="toolbar-label"),
                                dcc.RadioItems(
                                    id="hm-annotate",
                                    options=[
                                        {"label": "Show", "value": "show"},
                                        {"label": "Hide", "value": "hide"},
                                    ],
                                    value="show",
                                    inline=True,
                                    inputStyle={"marginRight": "4px"},
                                    labelStyle={"marginRight": "14px", "fontSize": "0.82rem"},
                                ),
                            ],
                        ),

                        # Transpose — time view only
                        html.Div(
                            id="hm-transpose-wrap",
                            style={"display":"flex","alignItems":"center","gap":"8px"},
                            children=[
                                html.Label("Orientation:", className="toolbar-label"),
                                dcc.RadioItems(
                                    id="hm-transpose",
                                    options=[
                                        {"label": "Countries → x",  "value": "normal"},
                                        {"label": "Years → x",      "value": "transpose"},
                                    ],
                                    value="normal",
                                    inline=True,
                                    inputStyle={"marginRight": "4px"},
                                    labelStyle={"marginRight": "14px", "fontSize": "0.82rem"},
                                ),
                            ],
                        ),

                    ],
                ),
            ],
        ),

        # ── Insight strip (only for correlation view) ──────────
        html.Div(id="hm-insight-strip", className="insight-strip"),

        # ── Main chart ─────────────────────────────────────────
        html.Div(
            className="chart-card",
            children=[
                dcc.Loading(
                    type="circle", color="#4f8ef7",
                    children=dcc.Graph(
                        id="hm-main-chart",
                        config={
                            "displayModeBar": True,
                            "modeBarButtonsToRemove": ["select2d","lasso2d"],
                            "displaylogo": False,
                            "toImageButtonOptions": {
                                "format": "png",
                                "filename": "macro_monitor_heatmap",
                                "scale": 2,
                            },
                        },
                        style={"minHeight": "400px"},
                    ),
                ),
            ],
        ),

        # ── Interpretation guide ───────────────────────────────
        html.Details(
            className="collapsible-section", open=False,
            children=[
                html.Summary("ℹ️ How to read this chart", className="collapsible-label"),
                html.Div(id="hm-guide", className="guide-box"),
            ],
        ),

    ],
)


# ── Callbacks ─────────────────────────────────────────────────────────────────

@callback(
    Output("hm-scale-wrap",     "style"),
    Output("hm-normalise-wrap", "style"),
    Output("hm-annotate-wrap",  "style"),
    Output("hm-transpose-wrap", "style"),
    Input("hm-view", "value"),
)
def toggle_toolbar(view):
    show = {"display": "flex", "alignItems": "center", "gap": "8px"}
    hide = {"display": "none"}
    if view == "time":
        return show, show, show, show
    elif view == "corr":
        return show, hide, hide, hide
    else:  # coverage
        return hide, hide, hide, hide


@callback(
    Output("hm-title",       "children"),
    Output("hm-subtitle",    "children"),
    Output("hm-kpi-strip",   "children"),
    Output("hm-main-chart",  "figure"),
    Output("hm-insight-strip", "children"),
    Output("hm-guide",       "children"),
    Input("sel-countries",   "value"),
    Input("sel-start-year",  "value"),
    Input("sel-end-year",    "value"),
    Input("sel-indicator",   "value"),
    Input("hm-view",         "value"),
    Input("hm-colour-scale", "value"),
    Input("hm-normalise",    "value"),
    Input("hm-annotate",     "value"),
    Input("hm-transpose",    "value"),
)
def update_page(countries, start_year, end_year, indicator_key,
                view, colour_scale, normalise, annotate, transpose):

    if not countries or not indicator_key:
        return "—", "", [], {}, [], []

    indicator  = INDICATORS[indicator_key]
    start_year = int(start_year or 2000)
    end_year   = int(end_year   or 2023)

    df = fetch_indicator(indicator_key, tuple(countries), start_year, end_year)

    view_labels = {
        "time":     "Heat Map",
        "corr":     "Correlation Matrix",
        "coverage": "Data Coverage",
    }
    title    = f"{indicator.label} — {view_labels.get(view,'Heat Map')}"
    subtitle = (
        f"{', '.join(countries)}  ·  {start_year}–{end_year}"
        f"  ·  Source: World Bank Open Data"
    )

    if df.empty:
        empty = no_data_message("World Bank returned no data for these selections.")
        return title, subtitle, [empty], {}, [], []

    # ── KPI strip ─────────────────────────────────────────────
    kpis = [
        kpi_card(code, v, d, y, indicator)
        for code in countries
        if code in df.columns
        for v, d, y in [latest_and_delta(df[code])]
    ]

    # ── Main figure ───────────────────────────────────────────
    if view == "time":
        fig = make_time_heatmap(
            df           = df,
            indicator    = indicator,
            countries    = countries,
            colour_scale = colour_scale or "RdYlGn",
            normalise    = (normalise == "z"),
            show_values  = (annotate == "show"),
            transpose    = (transpose == "transpose"),
        )
        insight = []

    elif view == "corr":
        scale = colour_scale if colour_scale in ("RdBu", "RdYlGn", "Spectral") else "RdBu"
        fig   = make_correlation_heatmap(
            df           = df,
            indicator    = indicator,
            countries    = countries,
            colour_scale = scale,
        )
        insight = _build_correlation_insights(df, indicator, countries)

    else:  # coverage
        fig     = make_missing_data_heatmap(df, indicator, countries)
        insight = []

    # ── Guide text ────────────────────────────────────────────
    guide = _guide_text(view, indicator)

    return title, subtitle, kpis, fig, insight, guide


# ── Helper: correlation insights ─────────────────────────────────────────────
def _build_correlation_insights(df, indicator, countries):
    cols = [c for c in countries if c in df.columns]
    if len(cols) < 2:
        return []

    from data.indicators import COUNTRIES as C
    corr = df[cols].corr()

    # Find strongest and weakest pair (off-diagonal)
    pairs = []
    for i, a in enumerate(cols):
        for b in cols[i+1:]:
            pairs.append((a, b, corr.loc[a, b]))

    if not pairs:
        return []

    pairs.sort(key=lambda x: abs(x[2]), reverse=True)
    top    = pairs[0]
    bottom = pairs[-1]

    def pair_label(a, b):
        return f"{C.get(a,a)} & {C.get(b,b)}"

    cards = [
        html.Div(className="insight-card insight-positive", children=[
            html.Div("Strongest sync", className="insight-card-label"),
            html.Div(pair_label(top[0], top[1]), className="insight-card-value"),
            html.Div(f"r = {top[2]:.3f}", className="insight-card-sub"),
        ]),
        html.Div(className="insight-card insight-neutral", children=[
            html.Div("Weakest sync", className="insight-card-label"),
            html.Div(pair_label(bottom[0], bottom[1]), className="insight-card-value"),
            html.Div(f"r = {bottom[2]:.3f}", className="insight-card-sub"),
        ]),
    ]
    # Add note on direction
    cards.append(html.Div(className="insight-card insight-info", children=[
        html.Div("Interpretation", className="insight-card-label"),
        html.Div("r ≈ +1 = cycles move together", className="insight-card-value"),
        html.Div("r ≈ -1 = cycles move opposite  ·  r ≈ 0 = no link",
                 className="insight-card-sub"),
    ]))
    return cards


# ── Helper: guide text ────────────────────────────────────────────────────────
def _guide_text(view, indicator):
    if view == "time":
        return [
            html.P([
                html.Strong("Time Heat Map: "),
                f"Each cell shows {indicator.short_label} for one country in one year. "
                "Colour intensity encodes the value — scan horizontally to track a country "
                "over time, or vertically to compare countries in the same year.",
            ]),
            html.P([
                html.Strong("Z-score normalisation: "),
                "Rescales each country's series to mean=0, std=1. "
                "Use this when comparing indicators with very different magnitudes "
                "(e.g. GDP per capita vs inflation rate) — the colour then reflects "
                "relative performance rather than absolute level.",
            ]),
            html.P([
                html.Strong("Colour scale direction: "),
                f"For {indicator.short_label}, "
                + ("lower values are better — the scale is automatically inverted so red = worse, green = better."
                   if indicator.invert_for_better
                   else "higher values are generally better — green = stronger, red = weaker."),
            ]),
        ]
    elif view == "corr":
        return [
            html.P([
                html.Strong("Correlation Matrix: "),
                f"Each cell shows the Pearson correlation (r) of {indicator.short_label} "
                "between two countries across the selected date range.",
            ]),
            html.P([
                html.Strong("Economic interpretation: "),
                "High positive correlations suggest synchronised economic cycles — "
                "relevant for assessing contagion risk, portfolio diversification, and "
                "the effectiveness of regional monetary policy coordination.",
            ]),
            html.P([
                html.Strong("Note: "),
                "Correlation measures linear co-movement only. "
                "Always inspect the time series (Page 1) to validate the relationship "
                "before drawing causal conclusions.",
            ]),
        ]
    else:
        return [
            html.P([
                html.Strong("Data Coverage: "),
                "Green cells (✓) indicate a data point exists in the World Bank database "
                "for that country-year combination. Red cells (—) are gaps.",
            ]),
            html.P([
                "Coverage percentages shown in the column headers. "
                "Gaps are common for developing economies in early years and for "
                "indicators with complex measurement requirements (e.g. government debt).",
            ]),
        ]
