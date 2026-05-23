"""
pages/scatter.py
================
Page 4 — Scatter / Phillips Curve
Views: snapshot scatter, animated, time-path.
Presets: Phillips Curve, Okun's Law, Savings-Growth, Trade-Growth.
"""

import numpy as np
from dash import register_page, callback, html, dcc, Input, Output, State, no_update, ctx

from data.indicators import INDICATORS
from data.fetcher     import fetch_indicator
from charts.scatter   import make_snapshot_scatter, make_animated_scatter, make_time_path

register_page(
    __name__,
    path  = "/scatter",
    name  = "Scatter / Phillips",
    title = "Scatter — Global Macro Monitor",
    order = 4,
)

# ── Economic presets ──────────────────────────────────────────────────────────
PRESETS = {
    "phillips":  ("unemployment", "inflation",       "Phillips Curve"),
    "okun":      ("gdp_growth",   "unemployment",    "Okun's Law"),
    "savings":   ("gross_savings","gdp_growth",      "Savings vs Growth"),
    "trade":     ("trade_openness","gdp_growth",     "Trade vs Growth"),
    "fdi":       ("fdi_inflows",  "gdp_growth",      "FDI vs Growth"),
}

INDICATOR_OPTIONS = [{"label": v.label, "value": k} for k, v in INDICATORS.items()]

# ── Layout ────────────────────────────────────────────────────────────────────
layout = html.Div(
    className="page-wrap",
    children=[

        html.Div(
            className="page-header",
            children=[
                html.H1(id="sc-title",    className="page-title"),
                html.Div(id="sc-subtitle", className="page-subtitle"),
            ],
        ),

        # ── Preset buttons ─────────────────────────────────────
        html.Div([
            html.Div("Quick presets:", className="toolbar-label",
                     style={"marginBottom": "6px"}),
            html.Div(
                className="preset-strip",
                children=[
                    html.Button(label, id=f"preset-{key}",
                                className="preset-btn", n_clicks=0)
                    for key, (_, _, label) in PRESETS.items()
                ],
            ),
        ]),

        # ── Axis selectors ─────────────────────────────────────
        html.Div(
            className="toolbar",
            children=[
                html.Div(
                    className="toolbar-left",
                    style={"flexWrap": "wrap", "gap": "16px", "alignItems": "flex-start"},
                    children=[

                        html.Div([
                            html.Label("X-axis indicator:", className="toolbar-label"),
                            dcc.Dropdown(
                                id="sc-x-ind",
                                options=INDICATOR_OPTIONS,
                                value="unemployment",
                                clearable=False, searchable=True,
                                style={"width": "260px", "fontSize": "0.82rem"},
                            ),
                        ], style={"display":"flex","flexDirection":"column","gap":"5px"}),

                        html.Div([
                            html.Label("Y-axis indicator:", className="toolbar-label"),
                            dcc.Dropdown(
                                id="sc-y-ind",
                                options=INDICATOR_OPTIONS,
                                value="inflation",
                                clearable=False, searchable=True,
                                style={"width": "260px", "fontSize": "0.82rem"},
                            ),
                        ], style={"display":"flex","flexDirection":"column","gap":"5px"}),

                        html.Div([
                            html.Label("View:", className="toolbar-label"),
                            dcc.RadioItems(
                                id="sc-view",
                                options=[
                                    {"label": "Snapshot",   "value": "snapshot"},
                                    {"label": "Animated",   "value": "animated"},
                                    {"label": "Time path",  "value": "path"},
                                ],
                                value="snapshot",
                                inline=True,
                                inputStyle={"marginRight":"4px"},
                                labelStyle={"marginRight":"12px","fontSize":"0.82rem"},
                            ),
                        ], style={"display":"flex","flexDirection":"column","gap":"5px"}),

                    ],
                ),

                # Snapshot-only controls (right side)
                html.Div(
                    id="sc-snapshot-controls",
                    className="toolbar-right",
                    style={"flexDirection":"column","alignItems":"flex-end","gap":"8px"},
                    children=[

                        html.Div([
                            html.Label("Year:", className="toolbar-label"),
                            dcc.Dropdown(
                                id="sc-year",
                                options=[{"label": str(y), "value": y}
                                         for y in range(2023, 1999, -1)],
                                value=2019,
                                clearable=False, searchable=False,
                                style={"width":"85px","fontSize":"0.82rem"},
                            ),
                        ], style={"display":"flex","alignItems":"center","gap":"8px"}),

                        html.Div([
                            dcc.Checklist(
                                id="sc-options",
                                options=[
                                    {"label": " Regression line", "value": "regression"},
                                    {"label": " Country labels",  "value": "labels"},
                                ],
                                value=["regression","labels"],
                                inline=True,
                                inputStyle={"marginRight":"4px"},
                                labelStyle={"marginRight":"14px","fontSize":"0.82rem",
                                            "color":"rgba(224,224,224,0.65)"},
                            ),
                        ]),
                    ],
                ),
            ],
        ),

        # ── OLS stat strip (snapshot only) ────────────────────
        html.Div(id="sc-stat-strip", className="stat-strip"),

        # ── Main chart ─────────────────────────────────────────
        html.Div(
            className="chart-card",
            children=[
                dcc.Loading(
                    type="circle", color="#4f8ef7",
                    children=dcc.Graph(
                        id="sc-main-chart",
                        config={
                            "displayModeBar": True,
                            "modeBarButtonsToRemove": ["select2d","lasso2d"],
                            "displaylogo": False,
                            "toImageButtonOptions": {
                                "format": "png",
                                "filename": "macro_monitor_scatter",
                                "scale": 2,
                            },
                        },
                        style={"minHeight": "500px"},
                    ),
                ),
            ],
        ),

        # ── Economic interpretation ────────────────────────────
        html.Details(
            className="collapsible-section", open=False,
            children=[
                html.Summary("📖 Economic interpretation", className="collapsible-label"),
                html.Div(id="sc-interpretation", className="guide-box"),
            ],
        ),

    ],
)


# ── Preset callback — updates the two axis dropdowns ─────────────────────────
@callback(
    Output("sc-x-ind", "value"),
    Output("sc-y-ind", "value"),
    [Input(f"preset-{key}", "n_clicks") for key in PRESETS],
    prevent_initial_call=True,
)
def apply_preset(*args):
    triggered = ctx.triggered_id
    if not triggered:
        return no_update, no_update
    key = triggered.replace("preset-", "")
    if key in PRESETS:
        x_key, y_key, _ = PRESETS[key]
        return x_key, y_key
    return no_update, no_update


# ── Show/hide snapshot-only controls ─────────────────────────────────────────
@callback(
    Output("sc-snapshot-controls", "style"),
    Input("sc-view", "value"),
)
def toggle_controls(view):
    base = {"flexDirection":"column","alignItems":"flex-end","gap":"8px"}
    base["display"] = "flex" if view == "snapshot" else "none"
    return base


# ── Master chart callback ─────────────────────────────────────────────────────
@callback(
    Output("sc-title",         "children"),
    Output("sc-subtitle",      "children"),
    Output("sc-main-chart",    "figure"),
    Output("sc-stat-strip",    "children"),
    Output("sc-interpretation","children"),
    Input("sel-countries",  "value"),
    Input("sel-start-year", "value"),
    Input("sel-end-year",   "value"),
    Input("sc-x-ind",       "value"),
    Input("sc-y-ind",       "value"),
    Input("sc-view",        "value"),
    Input("sc-year",        "value"),
    Input("sc-options",     "value"),
)
def update_page(countries, start_year, end_year,
                x_key, y_key, view, snap_year, options):

    if not countries or not x_key or not y_key:
        return "—", "", {}, [], []

    ind_x      = INDICATORS[x_key]
    ind_y      = INDICATORS[y_key]
    start_year = int(start_year or 2000)
    end_year   = int(end_year   or 2023)
    snap_year  = int(snap_year  or 2019)
    options    = options or []

    # Find matching preset label for title
    preset_label = next(
        (label for _, (xk, yk, label) in PRESETS.items()
         if xk == x_key and yk == y_key), None
    )
    chart_name = preset_label or f"{ind_x.short_label} vs {ind_y.short_label}"
    title      = chart_name
    subtitle   = (f"{', '.join(countries)}  ·  {start_year}–{end_year}"
                  f"  ·  Source: World Bank Open Data")

    # Fetch both indicators
    df_x = fetch_indicator(x_key, tuple(countries), start_year, end_year)
    df_y = fetch_indicator(y_key, tuple(countries), start_year, end_year)

    if df_x.empty or df_y.empty:
        return title, subtitle, {}, [], []

    # ── Figure ────────────────────────────────────────────────
    if view == "snapshot":
        fig = make_snapshot_scatter(
            df_x=df_x, df_y=df_y,
            ind_x=ind_x, ind_y=ind_y,
            year=snap_year,
            countries=countries,
            show_labels    = "labels"     in options,
            show_regression= "regression" in options,
        )
        stats = _build_stat_strip(df_x, df_y, ind_x, ind_y, countries, snap_year)

    elif view == "animated":
        fig   = make_animated_scatter(
            df_x=df_x, df_y=df_y,
            ind_x=ind_x, ind_y=ind_y,
            countries=countries,
            start_year=start_year, end_year=end_year,
        )
        stats = []

    else:  # path
        fig   = make_time_path(
            df_x=df_x, df_y=df_y,
            ind_x=ind_x, ind_y=ind_y,
            countries=countries,
            start_year=start_year, end_year=end_year,
        )
        stats = []

    interp = _interpretation(x_key, y_key, ind_x, ind_y)
    return title, subtitle, fig, stats, interp


# ── Stat strip builder ────────────────────────────────────────────────────────
def _build_stat_strip(df_x, df_y, ind_x, ind_y, countries, year):
    """OLS stats + data coverage cards for the snapshot year."""
    xs, ys = [], []
    n_countries = 0
    for code in countries:
        x_val = df_x[code].get(year) if code in df_x.columns else None
        y_val = df_y[code].get(year) if code in df_y.columns else None
        if x_val is not None and y_val is not None:
            if not (np.isnan(x_val) or np.isnan(y_val)):
                xs.append(float(x_val))
                ys.append(float(y_val))
                n_countries += 1

    cards = [
        _stat_card("Countries plotted", str(n_countries),
                   f"with data in {year}"),
    ]

    if len(xs) >= 3:
        xs_a = np.array(xs)
        ys_a = np.array(ys)
        corr = float(np.corrcoef(xs_a, ys_a)[0, 1])
        slope = (np.sum((xs_a - xs_a.mean()) * (ys_a - ys_a.mean()))
                 / np.sum((xs_a - xs_a.mean()) ** 2))
        r2 = corr ** 2

        corr_colour = "stat-positive" if corr > 0.3 else \
                      "stat-negative" if corr < -0.3 else ""

        cards += [
            _stat_card("Correlation (r)",
                       f"{corr:+.3f}",
                       f"{ind_x.short_label} ↔ {ind_y.short_label}",
                       value_class=corr_colour),
            _stat_card("R²",
                       f"{r2:.3f}",
                       "variance explained"),
            _stat_card("OLS slope",
                       f"{slope:+.3f}",
                       f"Δ{ind_y.unit} per Δ{ind_x.unit}"),
        ]

    return cards


def _stat_card(label, value, sub="", value_class=""):
    return html.Div(className="stat-card", children=[
        html.Div(label, className="stat-label"),
        html.Div(value, className=f"stat-value {value_class}"),
        html.Div(sub,   className="stat-sub") if sub else None,
    ])


# ── Interpretation text ───────────────────────────────────────────────────────
def _interpretation(x_key, y_key, ind_x, ind_y):
    texts = {
        ("unemployment", "inflation"): [
            html.P([html.Strong("Phillips Curve: "),
                    "The classical short-run trade-off between unemployment and inflation. "
                    "A downward-sloping relationship (negative r) indicates the trade-off is "
                    "active — lower unemployment coincides with higher inflation pressure."]),
            html.P("Post-2008 and post-COVID data have flattened or shifted this curve in many "
                   "advanced economies, a key area of ongoing macroeconomic debate."),
        ],
        ("gdp_growth", "unemployment"): [
            html.P([html.Strong("Okun's Law: "),
                    "The empirical relationship between GDP growth and unemployment. "
                    "Strong GDP growth is associated with falling unemployment (negative r). "
                    "Okun's coefficient is typically estimated at −0.3 to −0.5 in developed economies."]),
        ],
        ("gross_savings", "gdp_growth"): [
            html.P([html.Strong("Savings-Growth: "),
                    "Tests the Solow growth model prediction that higher savings rates finance "
                    "investment, driving long-run growth. Positive correlation is expected but "
                    "varies significantly across development stages."]),
        ],
        ("trade_openness", "gdp_growth"): [
            html.P([html.Strong("Trade-Growth Nexus: "),
                    "Examines whether trade openness (exports + imports as % of GDP) is associated "
                    "with higher growth — a central question in development economics."]),
        ],
        ("fdi_inflows", "gdp_growth"): [
            html.P([html.Strong("FDI-Growth: "),
                    "Tests whether foreign direct investment inflows correlate with GDP growth. "
                    "FDI is often seen as bringing capital, technology, and productivity gains "
                    "beyond the direct investment effect."]),
        ],
    }

    key = (x_key, y_key)
    if key in texts:
        return texts[key]

    return [html.P([
        html.Strong(f"{ind_x.short_label} vs {ind_y.short_label}: "),
        "Use the Snapshot view for a cross-sectional comparison in a single year, "
        "the Animated view to watch country positions shift over time, and the "
        "Time Path view to trace each country's journey through this scatter space.",
    ])]
