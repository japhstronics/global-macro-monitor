"""
pages/time_series.py
====================
Page 1 — Time Series
"""

import pandas as pd
from dash import (
    register_page, callback,
    html, dcc, Input, Output, State, no_update,
)

from data.indicators import INDICATORS
from data.fetcher    import fetch_indicator
from charts.time_series import make_time_series, make_country_sparkline
from utils.helpers   import latest_and_delta, kpi_card, no_data_message

register_page(
    __name__,
    path  = "/",
    name  = "Time Series",
    title = "Time Series — Global Macro Monitor",
    order = 1,
)

layout = html.Div(
    className="page-wrap",
    children=[

        html.Div(
            className="page-header",
            children=[
                html.H1(id="ts-page-title", className="page-title"),
                html.Div(id="ts-page-subtitle", className="page-subtitle"),
            ],
        ),

        html.Div(id="ts-kpi-strip", className="kpi-strip"),

        html.Div(
            className="toolbar",
            children=[
                html.Div(
                    className="toolbar-left",
                    children=[
                        html.Label("Moving average:", className="toolbar-label"),
                        dcc.RadioItems(
                            id="ts-ma-toggle",
                            options=[
                                {"label": "Off",  "value": "off"},
                                {"label": "3-yr",  "value": "3"},
                                {"label": "5-yr",  "value": "5"},
                            ],
                            value="off",
                            inline=True,
                            inputStyle={"marginRight": "4px"},
                            labelStyle={"marginRight": "16px", "fontSize": "0.82rem"},
                        ),
                    ],
                ),
                html.Div(
                    className="toolbar-right",
                    children=[
                        html.Button(
                            "⬇ Download CSV",
                            id="ts-download-btn",
                            className="btn-ghost",
                            n_clicks=0,
                        ),
                        dcc.Download(id="ts-download"),
                    ],
                ),
            ],
        ),

        html.Div(
            className="chart-card",
            children=[
                dcc.Loading(
                    type="circle", color="#4f8ef7",
                    children=dcc.Graph(
                        id="ts-main-chart",
                        config={
                            "displayModeBar": True,
                            "modeBarButtonsToRemove": ["select2d", "lasso2d"],
                            "displaylogo": False,
                            "toImageButtonOptions": {
                                "format": "png",
                                "filename": "macro_monitor_timeseries",
                                "scale": 2,
                            },
                        },
                        style={"height": "480px"},
                    ),
                ),
            ],
        ),

        html.Details(
            className="collapsible-section", open=False,
            children=[
                html.Summary("🔲 Individual country sparklines", className="collapsible-label"),
                html.Div(id="ts-sparklines", className="sparkline-grid"),
            ],
        ),

        html.Details(
            className="collapsible-section", open=False,
            children=[
                html.Summary("📋 Raw data table", className="collapsible-label"),
                html.Div(id="ts-data-table", className="data-table-wrap"),
            ],
        ),

    ],
)


@callback(
    Output("ts-page-title",    "children"),
    Output("ts-page-subtitle", "children"),
    Output("ts-kpi-strip",     "children"),
    Output("ts-main-chart",    "figure"),
    Input("sel-countries",   "value"),
    Input("sel-start-year",  "value"),
    Input("sel-end-year",    "value"),
    Input("sel-indicator",   "value"),
    Input("ts-ma-toggle",    "value"),
)
def update_chart(countries, start_year, end_year, indicator_key, ma_toggle):
    if not countries or not indicator_key:
        return "—", "", [], {}

    indicator  = INDICATORS[indicator_key]
    start_year = int(start_year or 2000)
    end_year   = int(end_year   or 2023)
    show_ma    = ma_toggle != "off"
    ma_window  = int(ma_toggle) if show_ma else 3

    df = fetch_indicator(
        indicator_key, tuple(countries), start_year, end_year,
    )

    title    = indicator.label
    subtitle = f"{', '.join(countries)}  ·  {start_year}–{end_year}  ·  Source: World Bank Open Data"

    if df.empty:
        return title, subtitle, [no_data_message("World Bank returned no data.")], {}

    kpis = [
        kpi_card(code, v, d, y, indicator)
        for code in countries
        if code in df.columns
        for v, d, y in [latest_and_delta(df[code])]
    ]

    fig = make_time_series(
        df=df, indicator=indicator,
        show_ma=show_ma, ma_window=ma_window,
        selected_countries=countries,
    )

    return title, subtitle, kpis, fig


@callback(
    Output("ts-sparklines",  "children"),
    Input("sel-countries",   "value"),
    Input("sel-start-year",  "value"),
    Input("sel-end-year",    "value"),
    Input("sel-indicator",   "value"),
)
def update_sparklines(countries, start_year, end_year, indicator_key):
    if not countries or not indicator_key:
        return []
    indicator  = INDICATORS[indicator_key]
    df = fetch_indicator(
        indicator_key, tuple(countries),
        int(start_year or 2000), int(end_year or 2023),
    )
    if df.empty:
        return [no_data_message()]
    return [
        html.Div(
            dcc.Graph(
                figure=make_country_sparkline(df[code].dropna(), code, indicator),
                config={"displayModeBar": False},
                style={"height": "160px"},
            ),
            className="sparkline-cell",
        )
        for code in countries
        if code in df.columns and not df[code].dropna().empty
    ]


@callback(
    Output("ts-data-table",  "children"),
    Input("sel-countries",   "value"),
    Input("sel-start-year",  "value"),
    Input("sel-end-year",    "value"),
    Input("sel-indicator",   "value"),
)
def update_data_table(countries, start_year, end_year, indicator_key):
    if not countries or not indicator_key:
        return []
    indicator  = INDICATORS[indicator_key]
    df = fetch_indicator(
        indicator_key, tuple(countries),
        int(start_year or 2000), int(end_year or 2023),
    )
    if df.empty:
        return [no_data_message()]
    dp = indicator.decimal_places
    header = html.Tr([html.Th("Year")] + [html.Th(c) for c in df.columns])
    rows = [
        html.Tr([html.Td(str(yr))] + [
            html.Td("—" if pd.isna(row[c]) else f"{row[c]:.{dp}f}")
            for c in df.columns
        ])
        for yr, row in df.sort_index(ascending=False).iterrows()
    ]
    return [html.Table(className="data-table", children=[html.Thead(header), html.Tbody(rows)])]


@callback(
    Output("ts-download",      "data"),
    Input("ts-download-btn",   "n_clicks"),
    State("sel-countries",     "value"),
    State("sel-start-year",    "value"),
    State("sel-end-year",      "value"),
    State("sel-indicator",     "value"),
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
    return dcc.send_data_frame(df.to_csv, f"{indicator_key}_{start_year}_{end_year}.csv", index=True)
