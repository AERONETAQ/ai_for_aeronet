"""Section 4 · Two deterministic tools: computed on the host from the parquet, no LLM, no sandbox.

list_sites never returns more than MAX_SITE_ROWS rows. describe_columns(site) reads a cached per-site count
table (_site_counts(), computed once in ~1 s) instead of the whole parquet per call, and is registered
sequential=True so calls never overlap (14 parallel full-parquet reads once took the host to ~12 GB).

Data-specific: swap this file, prompt/data_dictionary.py and the data_access skill for another dataset.
"""
import re

import pandas as pd
import pyarrow.parquet as pq

from .. import config

_SITES = None

def _sites():
    '''One row per site: location, record span, days with data. Read once (~10 s), then cached.'''
    global _SITES
    if _SITES is None:
        cols = ["AERONET_Site_Name", "Site_Latitude_Degrees", "Site_Longitude_Degrees", "Site_Elevation_m", "date"]
        df = pd.read_parquet(config.PARQUET, columns=cols)
        g = df.groupby("AERONET_Site_Name")
        _SITES = pd.DataFrame({"lat": g["Site_Latitude_Degrees"].first().round(3),
                               "lon": g["Site_Longitude_Degrees"].first().round(3),
                               "elev_m": g["Site_Elevation_m"].first().round(0).astype(int),
                               "first": g["date"].min().dt.strftime("%Y-%m-%d"),
                               "last": g["date"].max().dt.strftime("%Y-%m-%d"),
                               "days": g.size()}).sort_values("days", ascending=False)
    return _SITES


MAX_SITE_ROWS = config.MAX_SITE_ROWS     # list_sites never returns more rows than this, whatever limit the model asks for


def list_sites(name_contains: str = "", min_days: int = 0, limit: int = 40) -> str:
    '''Find AERONET sites. Returns name, latitude, longitude, elevation (m), first and last day with data, and the
    number of days with Level 2.0 data, sorted by record length. name_contains is case-insensitive
    (e.g. "kanpur", "GSFC", "_Island"). Use this before any site analysis to get the exact site name.
    At most 50 rows are returned: to select many sites (a region, a threshold), do it in run_python instead.'''
    limit = min(limit, MAX_SITE_ROWS)
    s = _sites()
    if name_contains:
        s = s[s.index.str.contains(name_contains, case=False, regex=False)]
    s = s[s["days"] >= min_days]
    if s.empty:
        return f"no site matches name_contains={name_contains!r}, min_days={min_days}; try a shorter fragment"
    head = f"{len(s)} site(s) match"
    if len(s) > limit:
        head += f", showing the {limit} with the longest records"
    return head + "\n" + s.head(limit).to_string()


_COUNTS = None

def _site_counts():
    '''Days with a value, per site and column. Computed once, one row group at a time (~1 s, <1 GB while it
    runs), then cached: a describe_columns(site) call reads nothing afterwards.'''
    global _COUNTS
    if _COUNTS is None:
        pf = pq.ParquetFile(config.PARQUET)
        parts = []
        for i in range(pf.metadata.num_row_groups):
            t = pf.read_row_group(i)
            cols = [c for c in t.column_names if c != "AERONET_Site_Name"]
            g = t.group_by("AERONET_Site_Name").aggregate([(c, "count") for c in cols]).to_pandas()
            g.columns = [c.replace("_count", "") if c != "AERONET_Site_Name" else c for c in g.columns]
            parts.append(g.set_index("AERONET_Site_Name"))
            del t
        _COUNTS = pd.concat(parts).groupby(level=0).sum()      # a site can span two row groups
    return _COUNTS


COLUMN_MEANINGS = {"AERONET_Site_Name": "site name", "datetime_utc": "day stamp, 12:00 UTC", "date": "day",
                   "year": "year", "month": "month", "Day_of_Year": "day of year 1–366",
                   "Site_Latitude_Degrees": "latitude (deg)", "Site_Longitude_Degrees": "longitude (deg)",
                   "Site_Elevation_m": "elevation (m)", "Precipitable_Water_cm": "column water vapour (cm)",
                   "Data_Quality_Level": "always lev20", "AERONET_Instrument_Number": "sun-photometer id",
                   "PI": "site principal investigator", "PI_Email": "PI e-mail"}


def _describe(col):
    """Meaning of one column name, e.g. AOD_500nm -> aerosol optical depth at 500 nm (unitless)."""
    m = re.fullmatch(r"AOD_(\d+)nm", col)
    if m:
        return f"aerosol optical depth at {m[1]} nm (unitless)"
    m = re.fullmatch(r"Angstrom_Exponent_(\d+)_(\d+)nm(_Polar)?", col)
    if m:
        text = f"Ångström exponent {m[1]}–{m[2]} nm"
        if m[3]:
            text += " (polar instrument)"
        return text
    m = re.fullmatch(r"N_(.+)", col)
    if m:
        return f"number of measurements in the daily {m[1]}"
    return COLUMN_MEANINGS.get(col, "")


def describe_columns(site: str = "") -> str:
    '''Columns of the AERONET table with meaning, dtype and how many days have a value.
    Without a site: every column (all sites). With a site (exact name from list_sites): only the columns that site
    has data for — one call, for the site the analysis is about, before choosing a wavelength. For a question
    over many sites do not call this per site: count valid values in run_python. The N_<column> measurement-count
    columns are not listed one by one; every value column has one.'''
    pf = pq.ParquetFile(config.PARQUET)
    nulls = {}                                            # column -> number of days without a value
    if site:
        # one site: its row from the cached per-site counts (nothing is read from the file here)
        counts = _site_counts()
        if site not in counts.index:
            return f"no site named {site!r}; use list_sites to find the exact name"
        have = counts.loc[site]
        n_days = int(have["date"])                        # date is never empty, so its count = the site's rows
        for c in pf.schema_arrow.names:
            nulls[c] = n_days - int(have.get(c, n_days))  # the site-name column itself is not in the counts
        header = f"site {site}: {n_days} rows (site-days); columns with no value at this site omitted"
    else:
        # all sites: no need to read the data, the parquet file stores null counts per row group
        n_days = pf.metadata.num_rows
        for c in pf.schema_arrow.names:
            nulls[c] = 0
        for rg in range(pf.metadata.num_row_groups):
            for i in range(pf.metadata.num_columns):
                col = pf.metadata.row_group(rg).column(i)
                if col.statistics:
                    nulls[col.path_in_schema] += col.statistics.null_count
        header = f"all sites: {n_days} rows (site-days)"
    lines = [header, f"{'column':34} {'dtype':13} {'days_with_value':>15} {'cover':>6}  meaning"]
    for c in pf.schema_arrow.names:
        if c.startswith("N_"):
            continue
        have = n_days - nulls[c]
        if site and have == 0:
            continue
        lines.append(f"{c:34} {str(pf.schema_arrow.field(c).type):13} {have:>15} {100 * have / n_days:>5.1f}%  {_describe(c)}")
    lines.append("N_<column> (int16): number of Level 2.0 measurements averaged into that day's value; one per AOD, "
                 "Angstrom and Precipitable_Water column (0 -> value is NaN)")
    return "\n".join(lines)
