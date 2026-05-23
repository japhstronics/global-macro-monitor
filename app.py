"""
Global Macro Monitor — Dash Application
Entry point. Mounts sidebar + Dash Pages router.

Run:  python app.py  →  http://localhost:8888
"""

import dash
from dash import Dash, html, dcc, Input, Output, callback
from flask import request

from components.sidebar import sidebar
from data.indicators import INDICATORS
from utils.visit_tracker import record_visit, get_unique_visit_count

# ── App init ──────────────────────────────────────────────────────────────────
app = Dash(
    __name__,
    use_pages=True,               # multi-page routing (pages/ folder)
    suppress_callback_exceptions=True,
    title="Global Macro Monitor",
    update_title=None,
)

server = app.server  # expose for Gunicorn / Render deployment

# ── Visit tracking (Flask before_request hook) ────────────────────────────────
@server.before_request                             # ← ADD THIS BLOCK
def track_visit():
    # Skip Dash's internal asset/callback requests
    if request.path.startswith(("/_dash", "/assets", "/favicon")):
        return
    # Respect X-Forwarded-For from proxies (Render, Nginx, etc.)
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ip = ip.split(",")[0].strip()                  # take first IP if chained
    record_visit(ip)

# ── Root layout ───────────────────────────────────────────────────────────────
app.layout = html.Div(
    id="app-shell",
    children=[
        sidebar(),
        html.Div(
            id="page-content",
            children=[dash.page_container],
        ),
    ],
)

# ── Callbacks ──────────────────────────────────────────────────────────────────

@callback(
    Output("indicator-description",  "children"),
    Output("indicator-code-display", "children"),
    Input("sel-indicator", "value"),
)

def update_indicator_info(indicator_key):
    if not indicator_key or indicator_key not in INDICATORS:
        return "", ""
    ind = INDICATORS[indicator_key]
    return ind.description, f"WB code: {ind.code}"

@callback(
    Output("visitor-count-display", "children"),
    Input("visitor-count-display", "id"),   # fires once on page mount
)
def show_visitor_count(_):
    count = get_unique_visit_count()
    return f"👥 {count:,} app visitors"

# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=8888)