"""
components/sidebar.py
=====================
Sidebar with navigation, controls, and indicator info card.
"""

from dash import dcc, html

from data.indicators import INDICATORS, COUNTRIES, INDICATOR_KEYS
from utils.visit_tracker import get_unique_visit_count

# ── Default selections ────────────────────────────────────────────────────────
DEFAULT_COUNTRIES = ["US", "GB", "DE", "CN", "ZA", "IN", "BR"]
DEFAULT_INDICATOR = "gdp_growth"
DEFAULT_START     = 2000
DEFAULT_END       = 2025

NAV_PAGES = [
    ("📈", "Time Series",         "/"),
    ("📊", "Country Comparison",  "/comparison"),
    ("🌡️", "Heat Map",            "/heatmap"),
    ("⚡", "Scatter / Phillips",  "/scatter"),
]

def _country_options() -> list[dict]:
    """Build the country dropdown option list."""
    return [
        {"label": f"{code} — {name}", "value": code}
        for code, name in COUNTRIES.items()
    ]


def _indicator_options() -> list[dict]:
    """Build the indicator dropdown option list, grouped by category."""
    return [
        {"label": ind.label, "value": key}
        for key, ind in INDICATORS.items()
    ]


def sidebar() -> html.Div:
    """
    Render the application sidebar.

    Contains:
        - Branding header
        - Country multi-select  (id: 'sel-countries')
        - Year range inputs     (id: 'sel-start-year', 'sel-end-year')
        - Primary indicator     (id: 'sel-indicator')
        - Dynamic indicator info card
        - Source / author footer
    """
    return html.Div(
        id="sidebar",
        children=[

            # ── Header / branding ──────────────────────────────
            html.Div(
                id="sidebar-header",
                children=[
                    html.Div(
                        children=[
                            html.Span("Global "),
                            html.Span("Macro", style={"color": "#4f8ef7"}),
                            html.Span(" Monitor"),
                        ],
                        className="sidebar-logo",
                    ),
                    html.Div(
                        "World Bank Open Data · Live",
                        className="sidebar-sub",
                    ),
                ],
            ),

            # ── Navigation ─────────────────────────────────────
            html.Nav(
                className="sidebar-nav",
                children=[
                    dcc.Link(
                        href=href,
                        className="nav-link",
                        children=[html.Span(icon), html.Span(f" {label}")],
                    )
                    for icon, label, href in NAV_PAGES
                ],
            ),

            html.Hr(className="sidebar-divider"),

            # ── Country selector ───────────────────────────────
            html.Div(
                className="sidebar-section",
                children=[
                    html.Div("Countries", className="sidebar-label"),
                    dcc.Dropdown(
                        id="sel-countries",
                        options=_country_options(),
                        value=DEFAULT_COUNTRIES,
                        multi=True,
                        placeholder="Select countries…",
                        clearable=False,
                        searchable=True,
                        optionHeight=36,
                    ),
                ],
            ),

            html.Hr(className="sidebar-divider"),

            # ── Year range ─────────────────────────────────────
            html.Div(
                className="sidebar-section",
                children=[
                    html.Div("Date Range", className="sidebar-label"),
                    html.Div(
                        style={"display": "flex", "gap": "10px"},
                        children=[
                            html.Div(
                                className="year-input",
                                style={"flex": 1},
                                children=[
                                    dcc.Input(
                                        id="sel-start-year",
                                        type="number",
                                        value=DEFAULT_START,
                                        min=1990,
                                        max=2035,
                                        step=1,
                                        debounce=True,
                                        placeholder="From",
                                        style={"width": "100%"},
                                    ),
                                    html.Div(
                                        "From",
                                        style={
                                            "fontSize": "0.65rem",
                                            "color": "rgba(224,224,224,0.3)",
                                            "marginTop": "3px",
                                            "textAlign": "center",
                                        },
                                    ),
                                ],
                            ),
                            html.Div(
                                className="year-input",
                                style={"flex": 1},
                                children=[
                                    dcc.Input(
                                        id="sel-end-year",
                                        type="number",
                                        value=DEFAULT_END,
                                        min=2001,
                                        max=2035,
                                        step=1,
                                        debounce=True,
                                        placeholder="To",
                                        style={"width": "100%"},
                                    ),
                                    html.Div(
                                        "To",
                                        style={
                                            "fontSize": "0.65rem",
                                            "color": "rgba(224,224,224,0.3)",
                                            "marginTop": "3px",
                                            "textAlign": "center",
                                        },
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),

            html.Hr(className="sidebar-divider"),

            # ── Primary indicator ──────────────────────────────
            html.Div(
                className="sidebar-section",
                children=[
                    html.Div("Primary Indicator", className="sidebar-label"),
                    dcc.Dropdown(
                        id="sel-indicator",
                        options=_indicator_options(),
                        value=DEFAULT_INDICATOR,
                        multi=False,
                        clearable=False,
                        searchable=True,
                        optionHeight=40,
                    ),
                ],
            ),

            # ── Dynamic indicator info card ────────────────────
            # Updated by callback in app.py when indicator changes
            html.Div(
                id="indicator-info-card",
                className="indicator-info",
                children=[
                    html.Div(id="indicator-description", children=""),
                    html.Div(id="indicator-code-display", className="indicator-code"),
                ],
            ),

            html.Hr(className="sidebar-divider"),

            # ── Footer ─────────────────────────────────────────
            html.Div(
                className="sidebar-footer",
                children=[
                    html.Div("Japhet Sibanda"),
                    html.Div(
                        children=[
                            html.Span("MSc Financial Engineering"),
                            html.Br(),
                            html.Span("MSc Applied Mathematical Modelling"),
                            html.Br(),
                            html.Span("BSc (Hons) Operations Research & Statistics"),
                            html.Br(),
                            html.Span("BSc Physics & Statistics"),
                        ],
                    ),
                    html.Br(),
                    html.Div(
                        children=[
                            html.A("LinkedIn", href="https://www.linkedin.com/in/japhet-sibanda-65942297/",
                                   target="_blank"),
                            html.Span(" · "),
                            html.A("GitHub", href="https://github.com/japhstronics",
                                   target="_blank"),
                             html.Span(" · "),
                            html.A("Credly", href="https://www.credly.com/users/japhet-sibanda",
                                   target="_blank"),
                        ]
                    ),
                    html.Br(),
                    html.Div(
                        "Data: World Bank Open Data (CC BY 4.0)",
                        style={"marginTop": "4px"},
                    ),
                    # ── Visitor counter ────────────────────────────────
                    html.Div(
                        id="visitor-count-display",
                        style={
                            "marginTop": "10px",
                            "fontSize": "0.7rem",
                            "color": "rgba(224,224,224,0.4)",
                            "textAlign": "center",
                            "letterSpacing": "0.04em",
                        },
                    ),
                ],
            ),

        ],
    )
