"""
World Bank API data fetcher — Dash-compatible version.
Uses functools.lru_cache for in-process memoisation (TTL via timestamp bucketing).
"""
import time
import logging
from functools import lru_cache

import requests
import pandas as pd

from data.indicators import INDICATORS, Indicator

logger = logging.getLogger(__name__)

WB_BASE_URL   = "https://api.worldbank.org/v2/country"
DEFAULT_START = 2000
DEFAULT_END   = 2023
MAX_RETRIES   = 3
RETRY_DELAY   = 1.5

def _ttl_bucket(ttl_seconds: int = 3600) -> int:
    """Bucket number that changes every ttl_seconds — expires lru_cache hourly."""
    return int(time.time() // ttl_seconds)

def _fetch_wb_series(country_code, indicator_code, start_year, end_year):
    url = (
        f"{WB_BASE_URL}/{country_code}/indicator/{indicator_code}"
        f"?format=json&date={start_year}:{end_year}&per_page=1000&mrv=50"
    )
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            payload = resp.json()
            if len(payload) < 2 or not payload[1]:
                return pd.DataFrame()
            records = []
            for entry in payload[1]:
                if entry.get("value") is not None:
                    records.append({
                        "year":         int(entry["date"]),
                        "value":        float(entry["value"]),
                        "country_code": country_code,
                        "country_name": entry.get("country", {}).get("value", country_code),
                    })
            if not records:
                return pd.DataFrame()
            return pd.DataFrame(records).sort_values("year").reset_index(drop=True)
        except requests.exceptions.RequestException as exc:
            logger.warning("Attempt %d failed (%s/%s): %s", attempt+1, country_code, indicator_code, exc)
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
    return pd.DataFrame()

@lru_cache(maxsize=256)
def fetch_indicator(indicator_key, country_codes, start_year=DEFAULT_START, end_year=DEFAULT_END, _ttl=0):
    """
    Fetch one indicator for multiple countries.
    Returns wide DataFrame: index=Year, columns=country_codes.
    Pass _ttl=_ttl_bucket() to auto-expire after 1 hour.
    """
    indicator = INDICATORS[indicator_key]
    frames = []
    for code in country_codes:
        df = _fetch_wb_series(code, indicator.code, start_year, end_year)
        if not df.empty:
            frames.append(df.rename(columns={"value": code})[["year", code]].set_index("year"))
    if not frames:
        return pd.DataFrame()
    combined = pd.concat(frames, axis=1).sort_index()
    combined.index.name = "Year"
    return combined


def get_indicator_df(indicator_key, country_codes, start_year=DEFAULT_START, end_year=DEFAULT_END):
    """Public helper for callbacks — injects TTL bucket automatically."""
    return fetch_indicator(indicator_key, tuple(country_codes), start_year, end_year, _ttl=_ttl_bucket())