"""
pages/country_comparison.py
============================
Page 2 — Country Comparison
Three chart views: snapshot bar, grouped multi-year bar, rank bump chart.
"""

import pandas as pd
from dash import register_page, callback, html, dcc, Input, Output, State, no_update

from data.indicators import INDICATORS
from data.fetcher    import fetch_indicator
from charts.comparison import make_snapshot_bar, make_grouped_bar, make_rank_chart
from utils.helpers   import latest_and_delta, kpi_card, no_data_message

register_page(
    __name__,
    path  = "/comparison",
    name  = "Country Comparison",
    title = "Country Comparison — Global Macro Monitor",
    order = 2,
)

# ── Layout ────────────────────────────────────────────────────────────────────
layout = html.Div(
    className="page-wrap",
    children=[

        # ── Page header ────────────────────────────────────────
        html.Div(
            className="page-header",
            children=[
                html.H1(id="cc-title", className="page-title"),
                html.Div(id="cc-subtitle", className="page-subtitle"),
            ],
        ),

        # ── KPI strip ──────────────────────────────────────────
        html.Div(id="cc-kpi-strip", className="kpi-strip"),

        # ── Toolbar ────────────────────────────────────────────
        html.Div(
            className="toolbar",
            children=[

                html.Div(
                    className="toolbar-left",
                    style={"gap": "20px", "flexWrap": "wrap"},
                    children=[

                        # Chart type
                        html.Div([
                            html.Label("View:", className="toolbar-label"),
                            dcc.RadioItems(
                                id="cc-view-toggle",
                                options=[
                                    {"label": "Snapshot bar",   "value": "snapshot"},
                                    {"label": "Multi-year bar",  "value": "grouped"},
                                    {"label": "Rank over time",  "value": "rank"},
                                ],
                                value="snapshot",
                                inline=True,
                                inputStyle={"marginRight": "4px"},
                                labelStyle={"marginRight": "14px", "fontSize": "0.82rem"},
                            ),
                        ], style={"display": "flex", "alignItems": "center", "gap": "8px"}),

                        # Year picker (snapshot view)
                        html.Div(
                            id="cc-year-wrap",
                            style={"display": "flex", "alignItems": "center", "gap": "8px"},
                            children=[
                                html.Label("Year:", className="toolbar-label"),
                                dcc.Dropdown(
                                    id="cc-year-picker",
                                    options=[{"label": str(y), "value": y}
                                             for y in range(2035, 1999, -1)],
                                    value=2023,
                                    clearable=False,
                                    searchable=False,
                                    style={"width": "90px", "fontSize": "0.82rem"},
                                ),
                            ],
                        ),

                        # Compare years (grouped view)
                        html.Div(
                            id="cc-compare-wrap",
                            style={"display": "none", "alignItems": "center", "gap": "8px"},
                            children=[
                                html.Label("Compare:", className="toolbar-label"),
                                dcc.Dropdown(
                                    id="cc-compare-years",
                                    options=[{"label": str(y), "value": y}
                                             for y in range(2023, 1999, -1)],
                                    value=[2010, 2019, 2023],
                                    multi=True,
                                    placeholder="Pick 2–3 years…",
                                    style={"width": "230px", "fontSize": "0.82rem"},
                                ),
                            ],
                        ),

                        # Sort order (snapshot only)
                        html.Div(
                            id="cc-sort-wrap",
                            style={"display": "flex", "alignItems": "center", "gap": "8px"},
                            children=[
                                html.Label("Sort:", className="toolbar-label"),
                                dcc.RadioItems(
                                    id="cc-sort-order",
                                    options=[
                                        {"label": "Highest first", "value": "desc"},
                                        {"label": "Lowest first",  "value": "asc"},
                                    ],
                                    value="desc",
                                    inline=True,
                                    inputStyle={"marginRight": "4px"},
                                    labelStyle={"marginRight": "14px", "fontSize": "0.82rem"},
                                ),
                            ],
                        ),
                    ],
                ),

                html.Div(
                    className="toolbar-right",
                    children=[
                        html.Button(
                            "⬇ Download CSV",
                            id="cc-download-btn",
                            className="btn-ghost",
                            n_clicks=0,
                        ),
                        dcc.Download(id="cc-download"),
                    ],
                ),
            ],
        ),

        # ── Main chart ─────────────────────────────────────────
        html.Div(
            className="chart-card",
            children=[
                dcc.Loading(
                    type="circle", color="#4f8ef7",
                    children=dcc.Graph(
                        id="cc-main-chart",
                        config={
                            "displayModeBar": True,
                            "modeBarButtonsToRemove": ["select2d", "lasso2d"],
                            "displaylogo": False,
                            "toImageButtonOptions": {
                                "format": "png",
                                "filename": "macro_monitor_comparison",
                                "scale": 2,
                            },
                        },
                        style={"minHeight": "380px"},
                    ),
                ),
            ],
        ),

        # ── Rankings table ─────────────────────────────────────
        html.Details(
            className="collapsible-section", open=True,
            children=[
                html.Summary("🏆 Rankings table", className="collapsible-label"),
                html.Div(id="cc-rankings-table", className="data-table-wrap"),
            ],
        ),

    ],
)


# ── Callbacks ─────────────────────────────────────────────────────────────────

@callback(
    Output("cc-year-wrap",    "style"),
    Output("cc-sort-wrap",    "style"),
    Output("cc-compare-wrap", "style"),
    Input("cc-view-toggle",   "value"),
)
def toggle_toolbar_controls(view):
    """Show/hide toolbar controls depending on active chart view."""
    show      = {"display": "flex", "alignItems": "center", "gap": "8px"}
    hide      = {"display": "none"}
    if view == "snapshot":
        return show, show, hide
    elif view == "grouped":
        return hide, hide, show
    else:  # rank
        return hide, hide, hide


@callback(
    Output("cc-title",      "children"),
    Output("cc-subtitle",   "children"),
    Output("cc-kpi-strip",  "children"),
    Output("cc-main-chart", "figure"),
    Input("sel-countries",    "value"),
    Input("sel-start-year",   "value"),
    Input("sel-end-year",     "value"),
    Input("sel-indicator",    "value"),
    Input("cc-view-toggle",   "value"),
    Input("cc-year-picker",   "value"),
    Input("cc-sort-order",    "value"),
    Input("cc-compare-years", "value"),
)
def update_page(countries, start_year, end_year, indicator_key,
                view, snap_year, sort_order, compare_years):

    if not countries or not indicator_key:
        return "—", "", [], {}

    indicator  = INDICATORS[indicator_key]
    start_year = int(start_year or 2000)
    end_year   = int(end_year   or 2023)

    df = fetch_indicator(indicator_key, tuple(countries), start_year, end_year)

    title    = f"{indicator.label} — Country Comparison"
    subtitle = f"{', '.join(countries)}  ·  {start_year}–{end_year}  ·  Source: World Bank Open Data"

    # ── KPI strip ─────────────────────────────────────────────
    if df.empty:
        kpis = [no_data_message("World Bank returned no data for these selections.")]
        fig  = {}
        return title, subtitle, kpis, fig

    kpis = [
        kpi_card(code, v, d, y, indicator)
        for code in countries
        if code in df.columns
        for v, d, y in [latest_and_delta(df[code])]
    ]

    # ── Chart ─────────────────────────────────────────────────
    if view == "snapshot":
        year = int(snap_year or end_year)
        fig  = make_snapshot_bar(df, indicator, year, sort_order or "desc")

    elif view == "grouped":
        years = sorted([int(y) for y in (compare_years or [2010, 2019, 2023])
                        if start_year <= int(y) <= end_year])[:3]
        fig = make_grouped_bar(df, indicator, years, countries)

    else:  # rank
        fig = make_rank_chart(df, indicator, countries)

    return title, subtitle, kpis, fig


@callback(
    Output("cc-rankings-table", "children"),
    Input("sel-countries",   "value"),
    Input("sel-start-year",  "value"),
    Input("sel-end-year",    "value"),
    Input("sel-indicator",   "value"),
    Input("cc-year-picker",  "value"),
)
def update_rankings(countries, start_year, end_year, indicator_key, snap_year):
    """Build a ranked table for the selected snapshot year."""
    if not countries or not indicator_key:
        return []

    indicator  = INDICATORS[indicator_key]
    start_year = int(start_year or 2000)
    end_year   = int(end_year   or 2023)
    year       = int(snap_year  or end_year)

    df = fetch_indicator(indicator_key, tuple(countries), start_year, end_year)
    if df.empty:
        return [no_data_message()]

    # Find nearest available year
    available = df.index[df.index <= year]
    actual_yr = int(available[-1]) if not available.empty else int(df.index[-1])
    row       = df.loc[actual_yr].dropna()

    sorted_row = row.sort_values(ascending=indicator.invert_for_better)
    dp         = indicator.decimal_places

    header = html.Tr([
        html.Th("Rank"), html.Th("Country"), html.Th("Code"),
        html.Th(f"Value ({indicator.unit})"), html.Th("Year"),
    ])

    rows = []
    for rank, (code, val) in enumerate(sorted_row.items(), start=1):
        medal = MEDAL.get(rank, "")
        style = {"background": "rgba(79,142,247,0.06)"} if rank <= 3 else {}
        rows.append(html.Tr(
            style=style,
            children=[
                html.Td(f"{medal} #{rank}"),
                html.Td(COUNTRIES.get(code, code)),
                html.Td(code, style={"color": "#4f8ef7", "fontFamily": "monospace",
                                      "fontSize": "0.78rem"}),
                html.Td(f"{val:,.{dp}f}",
                        style={"fontVariantNumeric": "tabular-nums", "fontWeight": 500}),
                html.Td(str(actual_yr)),
            ],
        ))

    return [html.Table(
        className="data-table",
        children=[html.Thead(header), html.Tbody(rows)],
    )]


@callback(
    Output("cc-download",     "data"),
    Input("cc-download-btn",  "n_clicks"),
    State("sel-countries",    "value"),
    State("sel-start-year",   "value"),
    State("sel-end-year",     "value"),
    State("sel-indicator",    "value"),
    prevent_initial_call=True,
)
def download_csv(n_clicks, countries, start_year, end_year, indicator_key):
    if not n_clicks or not countries or not indicator_key:
        return no_update
    df = fetch_indicator(
        indicator_key, tuple(countries),
        int(start_year or 2000), int(end_year or 2023),
    )
    if df.empty:
        return no_update
    return dcc.send_data_frame(
        df.to_csv, f"comparison_{indicator_key}.csv", index=True,
    )

# Local alias used in rankings table
from data.indicators import COUNTRIES
MEDAL = {1: "🥇", 2: "🥈", 3: "🥉"}
