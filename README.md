# 📊 Global Macro Monitor

> Interactive macroeconomic analytics dashboard tracking 10 key indicators 
> across 15 countries — built with Python Dash, Plotly, and the World Bank Open Data API.

![Python](https://img.shields.io/badge/Python-3.11+-4f8ef7?style=flat-square&logo=python&logoColor=white)
![Dash](https://img.shields.io/badge/Dash-2.17-FF4B4B?style=flat-square&logo=plotly&logoColor=white)
![Data](https://img.shields.io/badge/Data-World%20Bank%20API-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**🚀 [Live Demo](https://your-render-url.onrender.com)** — *(update after Render deployment)*

---

## Features

| Page | Description |
|---|---|
| 📈 **Time Series** | Multi-country line charts with 3/5-yr moving averages, KPI strip, sparkline grid, CSV export |
| 📊 **Country Comparison** | Ranked horizontal bar chart, grouped multi-year bars, rank bump chart |
| 🌡️ **Heat Map** | Countries × years matrix, correlation matrix with p-values, data coverage audit |
| ⚡ **Scatter / Phillips Curve** | 5 economic presets, snapshot, animated Play button, time-path with OLS regression |

## Indicators

| Code | Indicator |
|---|---|
| NY.GDP.MKTP.KD.ZG | GDP Growth Rate (% annual) |
| FP.CPI.TOTL.ZG | Inflation — CPI (% annual) |
| SL.UEM.TOTL.ZS | Unemployment Rate (% labour force) |
| BN.CAB.XOKA.GD.ZS | Current Account Balance (% GDP) |
| GC.DOD.TOTL.GD.ZS | Government Debt (% GDP) |
| NE.TRD.GNFS.ZS | Trade Openness (% GDP) |
| NY.GNS.ICTR.ZS | Gross Savings Rate (% GNI) |
| FM.LBL.BMNY.ZG | Broad Money Growth — M2 (% annual) |

## Architecture
global_macro_monitor/
├── app.py              # Entry point — Dash init, sidebar, page router
├── assets/style.css    # Dark theme — 425+ lines
├── components/sidebar.py  # Global controls shared across all pages
├── data/
│   ├── indicators.py   # Indicator metadata — World Bank codes, units, categories
│   └── fetcher.py      # API client — retry logic, 1hr caching
├── charts/             # Pure Plotly figure factories (no Dash imports)
├── pages/              # One file per dashboard page (Dash Pages routing)
└── utils/helpers.py    # KPI cards, delta calculations, formatting

## Local Setup

```bash
git clone https://github.com/japhstronics/global-macro-monitor.git
cd global-macro-monitor
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python app.py
# → http://localhost:8888
```
No API keys required — World Bank API is fully public.

## Skills Demonstrated

`Python` · `Dash` · `Plotly` · `REST API` · `pandas` · `World Bank Data` · 
`ETL` · `SQL` · `CSS` · `Time Series` · `Econometrics` · `Data Visualisation` · 
`Financial Engineering` · `Gunicorn` · `Render Deployment`

## Author

**Japhet Sibanda**  
MSc Financial Engineering (WorldQuant University, 91%) · MSc Applied Mathematical Modelling  
📧 japhetsibanda.js@gmail.com · [LinkedIn](https://www.linkedin.com/in/japhet-sibanda-65942297/) · [Credly](https://www.credly.com/users/japhet-sibanda)

---
*Data: World Bank Open Data (CC BY 4.0)*


