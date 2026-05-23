"""
Macroeconomic indicator definitions and metadata.
World Bank API indicator codes with display config.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Indicator:
    code: str
    label: str
    short_label: str
    unit: str
    description: str
    category: str
    invert_for_better: bool = False  # True = lower is better (e.g. inflation)
    decimal_places: int = 2


INDICATORS: dict[str, Indicator] = {
    "gdp_growth": Indicator(
        code="NY.GDP.MKTP.KD.ZG",
        label="GDP Growth Rate",
        short_label="GDP Growth",
        unit="% annual",
        description="Annual percentage growth rate of GDP at market prices in constant local currency.",
        category="Growth",
    ),
    "gdp_per_capita": Indicator(
        code="NY.GDP.PCAP.KD",
        label="GDP Per Capita (Constant 2015 USD)",
        short_label="GDP Per Capita",
        unit="USD",
        description="GDP per capita in constant 2015 US dollars. Measures standard of living.",
        category="Growth",
        decimal_places=0,
    ),
    "inflation": Indicator(
        code="FP.CPI.TOTL.ZG",
        label="Inflation (CPI, Annual %)",
        short_label="Inflation",
        unit="% annual",
        description="Consumer price inflation measured by the annual percentage change in CPI.",
        category="Prices",
        invert_for_better=True,
    ),
    "unemployment": Indicator(
        code="SL.UEM.TOTL.ZS",
        label="Unemployment Rate",
        short_label="Unemployment",
        unit="% of labor force",
        description="Share of the labor force without work but available and seeking employment.",
        category="Labour",
        invert_for_better=True,
    ),
    "current_account": Indicator(
        code="BN.CAB.XOKA.GD.ZS",
        label="Current Account Balance",
        short_label="Current Account",
        unit="% of GDP",
        description="Sum of net exports, net primary income, and net secondary income as % of GDP.",
        category="External",
    ),
    "govt_debt": Indicator(
        code="GC.DOD.TOTL.GD.ZS",
        label="Government Debt",
        short_label="Govt Debt",
        unit="% of GDP",
        description="Central government debt as a percentage of GDP.",
        category="Fiscal",
        invert_for_better=True,
    ),
    "trade_openness": Indicator(
        code="NE.TRD.GNFS.ZS",
        label="Trade Openness",
        short_label="Trade",
        unit="% of GDP",
        description="Sum of exports and imports of goods and services as % of GDP.",
        category="External",
    ),
    "fdi_inflows": Indicator(
        code="BX.KLT.DINV.WD.GD.ZS",
        label="FDI Net Inflows",
        short_label="FDI Inflows",
        unit="% of GDP",
        description="Foreign direct investment net inflows as % of GDP.",
        category="External",
    ),
    "gross_savings": Indicator(
        code="NY.GNS.ICTR.ZS",
        label="Gross Savings Rate",
        short_label="Savings Rate",
        unit="% of GNI",
        description="Gross savings as a percentage of gross national income.",
        category="Fiscal",
    ),
    "broad_money_growth": Indicator(
        code="FM.LBL.BMNY.ZG",
        label="Broad Money Growth (M2)",
        short_label="M2 Growth",
        unit="% annual",
        description="Annual growth rate of broad money (M2), a monetary policy indicator.",
        category="Monetary",
    ),
}

COUNTRIES: dict[str, str] = {
    "US": "United States",
    "GB": "United Kingdom",
    "DE": "Germany",
    "JP": "Japan",
    "CN": "China",
    "IN": "India",
    "BR": "Brazil",
    "ZA": "South Africa",
    "AU": "Australia",
    "CA": "Canada",
    "NG": "Nigeria",
    "KE": "Kenya",
    "FR": "France",
    "SG": "Singapore",
    "AE": "UAE",
}

CATEGORIES: list[str] = ["Growth", "Prices", "Labour", "External", "Fiscal", "Monetary"]

INDICATOR_KEYS = list(INDICATORS.keys())

COUNTRY_COLOURS: dict[str, str] = {
    "US": "#1f77b4",
    "GB": "#d62728",
    "DE": "#2ca02c",
    "JP": "#ff7f0e",
    "CN": "#e31a1c",
    "IN": "#ff6600",
    "BR": "#2ca02c",
    "ZA": "#006400",
    "AU": "#8c564b",
    "CA": "#e377c2",
    "NG": "#008000",
    "KE": "#17becf",
    "FR": "#003399",
    "SG": "#cc0001",
    "AE": "#006233",
}
