# src/quakeinsar/fetch_event.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
import requests


USGS_EVENT_DETAIL_GEOJSON = "https://earthquake.usgs.gov/fdsnws/event/1/query"


@dataclass(frozen=True)
class QuakeEvent:
    event_id: str
    time_ms: int
    magnitude: Optional[float]
    place: str
    latitude: float
    longitude: float
    depth_km: Optional[float]


def _safe_get(d: Dict[str, Any], key: str, default=None):
    return d.get(key, default) if isinstance(d, dict) else default


def fetch_event_geojson(event_id: str, timeout_s: int = 30) -> Dict[str, Any]:
    """
    Fetch a single event by USGS event id in GeoJSON format.
    Example event id: 'us6000jllz' or similar.
    """
    params = {
        "format": "geojson",
        "eventid": event_id,
    }
    r = requests.get(USGS_EVENT_DETAIL_GEOJSON, params=params, timeout=timeout_s)
    r.raise_for_status()
    return r.json()


def parse_quake_event(event_id: str, geojson: Dict[str, Any]) -> QuakeEvent:
    props = _safe_get(geojson, "properties", {})
    geom = _safe_get(geojson, "geometry", {})
    coords = _safe_get(geom, "coordinates", [])

    # GeoJSON coords: [lon, lat, depth_km] (depth can be null)
    lon = float(coords[0])
    lat = float(coords[1])
    depth_km = coords[2]
    depth_km = float(depth_km) if depth_km is not None else None

    time_ms = int(_safe_get(props, "time", 0))
    mag = _safe_get(props, "mag", None)
    mag = float(mag) if mag is not None else None
    place = str(_safe_get(props, "place", "") or "")

    return QuakeEvent(
        event_id=event_id,
        time_ms=time_ms,
        magnitude=mag,
        place=place,
        latitude=lat,
        longitude=lon,
        depth_km=depth_km,
    )
