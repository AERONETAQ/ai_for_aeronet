"""Section 4 · Two deterministic tools: computed on the host from the parquet tables, no LLM, no sandbox.

Both take a `dataset`: one of the names in config data_files (the 20 tables), default aod_l2.
list_sites never returns more than MAX_SITE_ROWS rows. Neither tool ever holds a whole table: the site list is
built one row group at a time, and describe_columns(site) reads only the row groups that hold the site
(_site_counts()). describe_columns is registered sequential=True so calls never overlap (14 parallel
full-parquet reads once took the host to ~12 GB).

Data-specific: swap this file, prompt/data_dictionary.py and the data_access skill for another dataset.
"""
import re
from typing import Literal

import pandas as pd
import pyarrow.parquet as pq

from .. import config

DATASETS = config.DATA_FILES              # dataset name -> parquet path (config.yaml data_files)
Dataset = Literal["aod_l2", "aod_l15", "aod_l2_monthly", "aod_l15_monthly", "aod_l2_points", "aod_l15_points",
                  "lunar", "lunar_l15",
                  "inv", "inv_l15_daily", "inv_monthly", "inv_l15_monthly", "inv_points", "inv_l15_points",
                  "alm_daily", "alm_l15_daily", "alm_monthly", "alm_l15_monthly", "alm", "alm_l15"]   # the names the model may pass (an enum in the tool schema)
assert set(DATASETS) == set(Dataset.__args__), f"config data_files {list(DATASETS)} must be exactly {Dataset.__args__}"


def _path(dataset):
    if dataset not in DATASETS:
        raise ValueError(f"dataset must be one of {list(DATASETS)}, not {dataset!r}")
    return DATASETS[dataset]


def _unit(dataset):
    """What one row of the table is."""
    if dataset.endswith("monthly"):
        return "site-months"
    if dataset in ("lunar", "lunar_l15", "aod_l2_points", "aod_l15_points"):
        return "measurements"
    if dataset in ("alm", "alm_l15", "inv_points", "inv_l15_points"):
        return "retrievals"
    return "site-days"


_SITES = {}

def _sites(dataset):
    '''One row per site: location, record span, days with data (months in a monthly table). Read once per dataset,
    then cached. The file is read one row group at a time and only one row per site and date is kept, so the
    10 GB all-points tables cost no more memory than the daily ones.'''
    if dataset not in _SITES:
        cols = ["AERONET_Site_Name", "Site_Latitude_Degrees", "Site_Longitude_Degrees", "Site_Elevation_m", "date"]
        pf = pq.ParquetFile(_path(dataset))
        num_days = [c for c in pf.schema_arrow.names if c.startswith("NUM_DAYS_")]
        parts = []
        for i in range(pf.metadata.num_row_groups):
            df = pf.read_row_group(i, columns=cols + num_days).to_pandas()
            if num_days:          # a monthly table has a row for every month of the site's span: keep the months with data
                df = df[df[num_days].max(axis=1) > 0]
            parts.append(df[cols].drop_duplicates(["AERONET_Site_Name", "date"]))
        g = pd.concat(parts).groupby("AERONET_Site_Name")
        _SITES[dataset] = pd.DataFrame({"lat": g["Site_Latitude_Degrees"].first().round(3),
                                        "lon": g["Site_Longitude_Degrees"].first().round(3),
                                        "elev_m": g["Site_Elevation_m"].first().round(0).astype(int),
                                        "first": g["date"].min().dt.strftime("%Y-%m-%d"),
                                        "last": g["date"].max().dt.strftime("%Y-%m-%d"),
                                        "days": g["date"].nunique()}).sort_values("days", ascending=False)
        _SITES[dataset].index = _SITES[dataset].index.astype(str)
    return _SITES[dataset]


MAX_SITE_ROWS = config.MAX_SITE_ROWS     # list_sites never returns more rows than this, whatever limit the model asks for


def list_sites(name_contains: str = "", min_days: int = 0, limit: int = 40, dataset: Dataset = "aod_l2") -> str:
    '''Find AERONET sites in one table. Returns name, latitude, longitude, elevation (m), first and last day with
    data, and the number of days with data, sorted by record length. dataset names one of the 20 tables of the data
    dictionary (default aod_l2, solar AOD Level 2.0 daily means). name_contains is case-insensitive (e.g. "kanpur",
    "GSFC", "_Island"). Use this before any site analysis to get the exact site name. At most 50 rows are
    returned: to select many sites (a region, a threshold), do it in run_python instead.
    Limits: one table per call; name_contains is a plain substring (no regex, no fuzzy spelling: "Mauna" finds
    Mauna_Loa, "Mauna Loa" does not); coordinates and elevation are the site's first row, rounded to 3 decimals;
    "days" counts UTC dates with any value (in a monthly table: months with data; in an all-points table: dates
    with at least one measurement or retrieval), not the days of one wavelength or product (describe_columns)
    and not nights.

    Args:
        name_contains: case-insensitive substring of the site name ("kanpur", "GSFC", "_Island"); empty = every site.
        min_days: keep only sites with at least this many days (months in a monthly table) with data in that table (0 = all).
        limit: how many rows to return, the longest records first; never more than 50.
        dataset: the table. Solar AOD: aod_l2 (Level 2.0 daily means, the default), aod_l15 (Level 1.5 daily),
            aod_l2_monthly, aod_l15_monthly, aod_l2_points, aod_l15_points (all points: every measurement).
            Lunar AOD, all points: lunar (Level 2.0), lunar_l15 (Level 1.5).
            Hybrid-scan inversions: inv (Level 2.0 daily), inv_l15_daily, inv_monthly (Level 2.0),
            inv_l15_monthly, inv_points (Level 2.0, all points), inv_l15_points.
            Almucantar-scan inversions: alm_daily (Level 2.0 daily), alm_l15_daily, alm_monthly (Level 2.0),
            alm_l15_monthly, alm (Level 2.0, all points), alm_l15 (Level 1.5, all points).
    '''
    limit = min(limit, MAX_SITE_ROWS)
    s = _sites(dataset)
    if name_contains:
        s = s[s.index.str.contains(name_contains, case=False, regex=False)]
    s = s[s["days"] >= min_days]
    if s.empty:
        return f"no site in {dataset} matches name_contains={name_contains!r}, min_days={min_days}; try a shorter fragment or another dataset"
    head = f"{len(s)} site(s) match in {dataset}"
    if len(s) > limit:
        head += f", showing the {limit} with the longest records"
    return head + "\n" + s.head(limit).to_string()


def _site_counts(dataset, site):
    '''Rows with a value per column, for one site (None = the site is not in the table). Every row group stores
    the first and last site name it holds, and the tables are written one site after the other, so only the few
    row groups that can hold the site are read, one at a time: about a second, also in a 10 GB all-points table.'''
    pf = pq.ParquetFile(_path(dataset))
    k = pf.schema_arrow.names.index("AERONET_Site_Name")
    counts = None
    for i in range(pf.metadata.num_row_groups):
        stats = pf.metadata.row_group(i).column(k).statistics
        if stats is None or not stats.has_min_max or stats.min <= site <= stats.max:
            df = pf.read_row_group(i).to_pandas()
            n = df[df["AERONET_Site_Name"] == site].count()
            counts = n if counts is None else counts + n       # a site can span several row groups
    return counts if counts is not None and counts["date"] > 0 else None


COLUMN_MEANINGS = {
    "AERONET_Site_Name": "site name", "datetime_utc": "time stamp, UTC (12:00 for daily means; not in monthly tables)", "date": "day (monthly tables: first day of the month)",
    "year": "year", "month": "month", "Day_of_Year": "day of year 1–366", "Day_of_Year_Fraction": "day of year with the time as a fraction",
    "Site_Latitude_Degrees": "latitude (deg)", "Site_Longitude_Degrees": "longitude (deg)", "Site_Elevation_m": "elevation (m)",
    "Precipitable_Water_cm": "column water vapour (cm)", "Triplet_Variability_Precipitable_Water_cm": "triplet variability of the water vapour (cm)",
    "Data_Quality_Level": "lev20 or lev15", "AERONET_Instrument_Number": "sun-photometer id",
    # inversion table
    "Angstrom_Exponent_440_870nm_from_Coincident_Input_AOD": "Ångström exponent 440–870 nm of the measured input AOD",
    "Extinction_Angstrom_Exponent_440_870nm_Total": "Ångström exponent 440–870 nm of the retrieved extinction",
    "Absorption_Angstrom_Exponent_440_870nm": "absorption Ångström exponent 440–870 nm",
    "Minimum_Altitude_For_Flux_Calculations_km": "flux layer bottom (km)", "Maximum_Altitude_For_Flux_Calculations_km": "flux layer top (km)",
    "Flux_Down_BOA": "broadband downward flux at the surface (W/m²)", "Flux_Down_TOA": "broadband downward flux at the top of the atmosphere (W/m²)",
    "Flux_Up_BOA": "broadband upward flux at the surface (W/m²)", "Flux_Up_TOA": "broadband upward flux at the top of the atmosphere (W/m²)",
    "Rad_Forcing_BOA": "aerosol radiative forcing at the surface (W/m², negative = cooling)",
    "Rad_Forcing_TOA": "aerosol radiative forcing at the top of the atmosphere (W/m², negative = cooling)",
    "Forcing_Eff_BOA": "forcing efficiency at the surface (W/m² per unit AOD 550 nm)",
    "Forcing_Eff_TOA": "forcing efficiency at the top of the atmosphere (W/m² per unit AOD 550 nm)",
    "Diffuse_BOA": "diffuse broadband flux at the surface (W/m²)", "Diffuse_TOA": "diffuse broadband flux at the top of the atmosphere (W/m²)",
    "Retrieval_Measurement_Scan_Type": "Hybrid or Almucantar: one value per table",
    "Sphericity_Factor_percent": "retrieved share of spherical particles (%)",
    "Inflection_Radius_of_Size_Distribution_um": "radius that separates the fine from the coarse mode (µm)",
    "Average_Solar_Zenith_Angles_for_Flux_Calculation_Degrees": "solar zenith angle used for the fluxes (deg)",
    "Solar_Zenith_Angle_for_Measurement_Start_Degrees": "solar zenith angle when the sky scan started (deg)",
    "Sky_Residual_percent": "misfit between measured and modelled sky radiances (%)",
    "Sun_Residual_percent": "misfit between measured and modelled AOD (%)",
    "Coincident_AOD440nm": "measured AOD at 440 nm at the time of the scan",
    "If_Retrieval_is_L2_without_L2_0_4_AOD_440_threshold": "1 = the retrieval passes every Level 2.0 check except AOD(440) >= 0.4",
    "If_AOD_is_L2": "1 = the AOD that went into the retrieval is Level 2.0",
    "Last_Processing_Date_dd_mm_yyyy": "processing date (text)", "Last_Processing_Time_hh_mm_ss": "processing time (text)",
    # all-points AOD tables (lunar and solar)
    "Measurement_Type_solar_or_lunar": "lunar in the lunar tables", "Solar_Zenith_Angle_Degrees": "solar zenith angle (deg)",
    "Lunar_Zenith_Angle_Degrees": "zenith angle of the Moon (deg)", "Optical_Air_Mass": "optical air mass of the path to the Moon (to the Sun in the solar tables)",
    "Lunar_Phase_Angle_Degrees": "lunar phase angle (deg): 0 = full Moon, negative = waxing, positive = waning",
    "Sensor_Temperature_Degrees_C": "detector temperature (°C)", "Ozone_Dobson": "ozone column (DU)", "NO2_Dobson": "NO2 column (DU)",
    "Last_Date_Processed": "processing date", "Number_of_Wavelengths": "number of AOD wavelengths of the instrument",
    "Exact_Wavelengths_of_PW_um_935nm": "actual water-vapour filter wavelength (µm)",
}
COUNTS = ("N_", "NUM_DAYS_", "NUM_POINTS_")       # count columns: not listed one by one by describe_columns
MODE = {"T": "total", "F": "fine mode", "C": "coarse mode", "Total": "total", "Fine": "fine mode", "Coarse": "coarse mode"}
SIZE = {"VolC": "volume concentration (µm³/µm²)", "REff": "effective radius (µm)", "VMR": "volume median radius (µm)", "Std": "width of the size distribution (std of ln r)"}

PATTERNS = [   # (regex, lambda match -> meaning)
    (r"AOD_(\d+)nm",                                   lambda m: f"aerosol optical depth at {m[1]} nm (unitless)"),
    (r"Angstrom_Exponent_(\d+)_(\d+)nm(_Polar)?",       lambda m: f"Ångström exponent {m[1]}–{m[2]} nm" + (" (polar instrument)" if m[3] else "")),
    (r"Triplet_Variability_(\d+)",                      lambda m: f"triplet variability of AOD at {m[1]} nm (max − min of the three measurements)"),
    (r"Exact_Wavelengths_of_AOD_um_(\d+)nm",            lambda m: f"actual filter wavelength of the {m[1]} nm channel (µm)"),
    (r"AOD_Coincident_Input_(\d+)nm",                   lambda m: f"measured AOD at {m[1]} nm that went into the retrieval"),
    (r"AOD_Extinction_(Total|Fine|Coarse)_(\d+)nm",      lambda m: f"retrieved extinction AOD at {m[2]} nm, {MODE[m[1]]}"),
    (r"Single_Scattering_Albedo_(\d+)nm",               lambda m: f"single scattering albedo at {m[1]} nm"),
    (r"Absorption_AOD_(\d+)nm",                         lambda m: f"absorption AOD at {m[1]} nm"),
    (r"Refractive_Index_(Real|Imaginary)_Part_(\d+)nm",  lambda m: f"{m[1].lower()} part of the refractive index at {m[2]} nm"),
    (r"Asymmetry_Factor_(Total|Fine|Coarse)_(\d+)nm",    lambda m: f"asymmetry factor at {m[2]} nm, {MODE[m[1]]}"),
    (r"dVdlnr_(\d+)_(\d+)um",                           lambda m: f"volume size distribution dV/dln r at r = {m[1]}.{m[2]} µm (µm³/µm²)"),
    (r"(VolC|REff|VMR|Std)_(T|F|C)",                    lambda m: f"{SIZE[m[1]]}, {MODE[m[2]]}"),
    (r"Spectral_Flux_(Down|Up|Diffuse)_(\d+)nm",         lambda m: f"spectral {m[1].lower()}ward flux at {m[2]} nm (W/m²/µm)"),
    (r"Lidar_Ratio_(\d+)nm",                            lambda m: f"lidar ratio at {m[1]} nm (sr)"),
    (r"Depolarization_Ratio_(\d+)nm",                   lambda m: f"linear depolarization ratio at {m[1]} nm"),
    (r"Scattering_Angle_Bin_(.+)_(\d+)nm",                lambda m: f"sky radiances measured in the scattering-angle bin {m[1].replace('_', ' ')} at {m[2]} nm (count)"),
    (r"Surface_Albedo_(\d+)m",                          lambda m: f"surface albedo assumed at {m[1]} nm"),
    (r"N_(.+)",                                         lambda m: f"number of measurements in the daily {m[1]}"),
    (r"NUM_DAYS_(.+)",                                  lambda m: f"number of days in the monthly {m[1]}"),
    (r"NUM_POINTS_(.+)",                                lambda m: f"number of measurements in the monthly {m[1]}"),
]


def _describe(col):
    """Meaning of one column name, e.g. AOD_500nm -> aerosol optical depth at 500 nm (unitless)."""
    if col in COLUMN_MEANINGS:
        return COLUMN_MEANINGS[col]
    for pattern, meaning in PATTERNS:
        m = re.fullmatch(pattern, col)
        if m:
            return meaning(m)
    return ""


def describe_columns(site: str = "", dataset: Dataset = "aod_l2") -> str:
    '''Columns of one AERONET table with meaning, dtype and how many rows have a value. dataset names one of the 20
    tables of the data dictionary (default aod_l2). Without a site: every column (all sites). With a site (exact
    name from list_sites): only the columns that site has data for — one call, for the site the analysis is about,
    before choosing a wavelength or product. For a question over many sites do not call this per site: count valid
    values in run_python. The count columns (N_<column> in daily tables, NUM_DAYS_<column> and NUM_POINTS_<column>
    in monthly tables) are not listed one by one; every value column of those tables has them.
    Limits: counts of rows with a value over the whole record, not per period (a site that stopped in 2010 still
    shows full coverage) and no min, max or mean (compute them in run_python); a monthly table has a row for every
    month of the site's span, with or without data, so its cover is the share of months with a value; an inversion
    table lists only the filter set the site has (440/675/870 or 443/667/865 nm); one call takes
    about a second.

    Args:
        site: exact site name from list_sites (case-sensitive, with underscores: "Mauna_Loa") for that site's
            columns only; empty = every column, counted over all sites.
        dataset: the table. Solar AOD: aod_l2 (Level 2.0 daily means, the default), aod_l15 (Level 1.5 daily),
            aod_l2_monthly, aod_l15_monthly, aod_l2_points, aod_l15_points (all points: every measurement).
            Lunar AOD, all points: lunar (Level 2.0), lunar_l15 (Level 1.5).
            Hybrid-scan inversions: inv (Level 2.0 daily), inv_l15_daily, inv_monthly (Level 2.0),
            inv_l15_monthly, inv_points (Level 2.0, all points), inv_l15_points.
            Almucantar-scan inversions: alm_daily (Level 2.0 daily), alm_l15_daily, alm_monthly (Level 2.0),
            alm_l15_monthly, alm (Level 2.0, all points), alm_l15 (Level 1.5, all points).
    '''
    pf = pq.ParquetFile(_path(dataset))
    unit = _unit(dataset)
    nulls = {}                                            # column -> number of rows without a value
    if site:
        # one site: only the row groups that hold it are read
        have = _site_counts(dataset, site)
        if have is None:
            return f"no site named {site!r} in {dataset}; use list_sites(dataset={dataset!r}) to find the exact name"
        n_rows = int(have["date"])                        # date is never empty, so its count = the site's rows
        for c in pf.schema_arrow.names:
            nulls[c] = n_rows - int(have[c])
        header = f"{dataset}, site {site}: {n_rows} rows ({unit}); columns with no value at this site omitted"
    else:
        # all sites: no need to read the data, the parquet file stores null counts per row group
        n_rows = pf.metadata.num_rows
        for c in pf.schema_arrow.names:
            nulls[c] = 0
        for rg in range(pf.metadata.num_row_groups):
            for i in range(pf.metadata.num_columns):
                col = pf.metadata.row_group(rg).column(i)
                if col.statistics:
                    nulls[col.path_in_schema] += col.statistics.null_count
        header = f"{dataset}, all sites: {n_rows} rows ({unit})"
    lines = [header, f"{'column':48} {'dtype':13} {'rows_with_value':>15} {'cover':>6}  meaning"]
    for c in pf.schema_arrow.names:
        if c.startswith(COUNTS):
            continue
        have = n_rows - nulls[c]
        if site and have == 0:
            continue
        lines.append(f"{c:48} {str(pf.schema_arrow.field(c).type):13} {have:>15} {100 * have / n_rows:>5.1f}%  {_describe(c)}")
    if any(c.startswith("N_") for c in pf.schema_arrow.names):
        lines.append("N_<column> (Int32): number of measurements (retrievals in an inversion table) averaged into that day's value; "
                     "one per value column (0 -> value is NaN)")
    if any(c.startswith("NUM_DAYS_") for c in pf.schema_arrow.names):
        lines.append("NUM_DAYS_<column>, NUM_POINTS_<column> (Int32): days and measurements (retrievals in an inversion table) "
                     "averaged into that month's value; one pair per value column (0 -> value is NaN)")
    return "\n".join(lines)
