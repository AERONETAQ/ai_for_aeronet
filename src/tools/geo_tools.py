"""Section 4 · Three deterministic tools about places: computed on the host, no LLM, no sandbox.

geocode (place name -> coordinates) is the geocode tool of VAYU v2, verbatim: it needs the internet (the sandbox
has none), asks Nominatim, the geocoder of OpenStreetMap, one request per second (Nominatim's rule), and
remembers every answer for the session. nearest_sites and site_coverage read the cached site tables of
data_tools (one parquet read per dataset, then nothing).
"""
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import requests
from timezonefinder import TimezoneFinder

from .. import config
from .data_tools import DATASETS, MAX_SITE_ROWS, Dataset, _sites

MAX_PLACES = config.GEOCODER["max_places_per_call"]

_TIMEZONES = TimezoneFinder()     # coordinates -> time zone name, offline
_FOUND = {}                       # place as typed -> Nominatim's best match (None = no match); kept for the session
_last_request = 0.0               # time of the last request to Nominatim


def _search(place):
    '''Nominatim's best match for one place (a dict), or None when it finds nothing.'''
    global _last_request
    wait = 1.0 - (time.time() - _last_request)          # Nominatim allows one request per second
    if wait > 0:
        time.sleep(wait)
    response = requests.get(config.GEOCODER["url"], timeout=20,
                            params={"q": place, "format": "jsonv2", "limit": 1, "addressdetails": 1, "accept-language": "en"},
                            headers={"User-Agent": config.GEOCODER["user_agent"]})
    _last_request = time.time()
    response.raise_for_status()
    matches = response.json()
    return matches[0] if matches else None


def _describe(place, match):
    '''The lines the model reads for one place.'''
    lat, lon = float(match["lat"]), float(match["lon"])
    address = match.get("address", {})
    state_codes = [value for key, value in sorted(address.items()) if key.startswith("ISO3166-2")]   # e.g. ["IN-PB"]
    state = address.get("state", "unknown") + (f" ({state_codes[0]})" if state_codes else "")
    south, north, west, east = [float(x) for x in match["boundingbox"]]
    tz_name = _TIMEZONES.timezone_at(lat=lat, lng=lon) or "UTC"
    local_now = datetime.now(ZoneInfo(tz_name))
    offset = local_now.strftime("%z")                    # "+0530"
    return (f"{place} -> {match['display_name']} ({match.get('addresstype', 'place')})\n"
            f"  lat {lat:.4f}, lon {lon:.4f} | country {address.get('country', 'unknown')} "
            f"({address.get('country_code', '??').upper()}) | state {state}\n"
            f"  bounding box: south {south:.4f}, north {north:.4f}, west {west:.4f}, east {east:.4f}\n"
            f"  time zone {tz_name} (UTC{offset[:3]}:{offset[3:]}), local time now {local_now:%Y-%m-%d %H:%M %A}")


def geocode(places: list[str]) -> str:
    '''Look up places by name: cities, addresses, landmarks, states, countries. For each one returns the matched
    name and its kind (city, state, country ...), latitude and longitude, country and state with their ISO codes,
    the bounding box (south, north, west, east) and the time zone with the local time now.
    Add the state or country when a name is ambiguous ("Springfield, Illinois", "Punjab, Pakistan"): only the best
    match is returned. A "lat, lon" string ("28.61, 77.21") returns the place at that point, e.g. to name a hotspot.
    Pass all places of the question in one call, at most 10 per call. This is the only tool with internet access.
    AERONET sites near the point: nearest_sites; sites inside a country or state: the maps skill (Natural Earth borders).
    Limits: it knows places (OpenStreetMap), not AERONET sites: try list_sites first, site names are often city
    names; one best match per place, so a wrong guess for an ambiguous name is silent unless you read the kind
    and country it returns; the point is a city's centre, the bounding box an administrative outline (a country's
    includes overseas parts), neither is a radius; a network error returns "lookup failed" (call again); one
    lookup per second, so one call for all places.

    Args:
        places: the place names to look up ("Kanpur, India", "Punjab, Pakistan", "Mauna Loa Observatory") or
            "lat, lon" strings ("28.61, 77.21"); all places of the question in one list, at most 10.
    '''
    lines = []
    for place in places[:MAX_PLACES]:
        try:
            if place not in _FOUND:
                _FOUND[place] = _search(place)
        except requests.RequestException as e:           # network error, timeout, HTTP error: tell the model, do not crash the turn
            lines.append(f"{place} -> lookup failed ({type(e).__name__}); call geocode again for this place")
            continue
        if _FOUND[place] is None:
            lines.append(f"{place} -> no match; try another spelling, or add the state or country")
        else:
            lines.append(_describe(place, _FOUND[place]))
    if len(places) > MAX_PLACES:
        lines.append(f"only the first {MAX_PLACES} of {len(places)} places were looked up; call geocode again for the rest")
    return "\n".join(lines)


def haversine_km(lat1, lon1, lat2, lon2):
    '''Great-circle distance in km (Earth radius 6371 km); any argument may be a pandas Series.'''
    lat1, lon1, lat2, lon2 = np.radians(lat1), np.radians(lon1), np.radians(lat2), np.radians(lon2)
    h = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(h))


def nearest_sites(lat: float, lon: float, max_km: float = 300, limit: int = 10, dataset: Dataset = "aod_l2") -> str:
    '''AERONET sites within max_km of a point (e.g. the coordinates geocode returned), nearest first: name,
    distance in km, latitude, longitude, elevation (m), first and last day with data and the number of days with
    data in that table. dataset: aod_l2 (default), aod_l15, inv, lunar. At most 50 rows; a wider circle or a
    region is a run_python selection instead.
    Limits: straight-line great-circle distance on a sphere (within 0.5 %), from the site's first-row
    coordinates; distance says nothing about representativeness: a mountain site or a coastal site 30 km away
    sees different air (compare elevations, site_comparison skill); one table per call, so a site absent from
    this table may still be in another.

    Args:
        lat: latitude of the point in decimal degrees, north positive (from geocode or the user).
        lon: longitude of the point in decimal degrees, east positive, west negative.
        max_km: radius of the circle around the point in kilometres (default 300).
        limit: how many rows to return, nearest first; never more than 50.
        dataset: the table whose sites are searched: aod_l2 (solar AOD Level 2.0 daily means, the default),
            aod_l15 (solar AOD Level 1.5 daily means), inv (hybrid inversions), lunar (lunar AOD all points).
    '''
    limit = min(limit, MAX_SITE_ROWS)
    s = _sites(dataset).copy()
    s.insert(0, "km", haversine_km(lat, lon, s["lat"], s["lon"]).round(1))
    s = s[s["km"] <= max_km].sort_values("km")
    if s.empty:
        return f"no site in {dataset} within {max_km:g} km of ({lat:.4f}, {lon:.4f}); widen max_km or try another dataset"
    head = f"{len(s)} site(s) in {dataset} within {max_km:g} km of ({lat:.4f}, {lon:.4f})"
    if len(s) > limit:
        head += f", showing the {limit} nearest"
    return head + "\n" + s.head(limit).to_string()


def site_coverage(site: str) -> str:
    '''What the four tables hold for one site (exact name from list_sites): per table the first and last day with
    data and the number of days with data, or "not in this table". One call answers which of solar Level 2.0,
    Level 1.5, inversions and lunar data exist for the site and over which period, before any cross-table analysis.
    The first call per table reads its site list once (the lunar table takes about 20 s).
    Limits: exact, case-sensitive site name (list_sites gives it); spans and day counts per table, not per
    wavelength or product (describe_columns) and not per year; in the lunar table "days" are UTC dates with a
    measurement, not nights; a span says nothing about gaps inside it.

    Args:
        site: exact site name from list_sites (case-sensitive, with underscores: "Mauna_Loa").
    '''
    lines = [f"site {site}:"]
    for name, path in DATASETS.items():
        s = _sites(name)
        if site in s.index:
            r = s.loc[site]
            lines.append(f"  {name:8} {r['first']} -> {r['last']}  {int(r['days']):>6} days with data  (lat {r['lat']}, lon {r['lon']}, {int(r['elev_m'])} m)")
        else:
            lines.append(f"  {name:8} not in this table")
    return "\n".join(lines)
