# src/quakeinsar/cli.py
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from .fetch_event import fetch_event_geojson, parse_quake_event


def ms_to_utc_str(ms: int) -> str:
    dt = datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def main() -> int:
    p = argparse.ArgumentParser(description="Mini earthquake deformation analysis (Step 1: fetch event).")
    p.add_argument("--event-id", required=True, help="USGS event id (e.g., us6000jllz)")
    p.add_argument("--out", default=None, help="Write event summary to a JSON file path (e.g., outputs/event.json)")
    args = p.parse_args()

    geojson = fetch_event_geojson(args.event_id)
    ev = parse_quake_event(args.event_id, geojson)

    print("=== USGS Event ===")
    print(f"Event ID : {ev.event_id}")
    print(f"Time     : {ms_to_utc_str(ev.time_ms)}")
    print(f"Place    : {ev.place}")
    print(f"Mw       : {ev.magnitude}")
    print(f"Lat/Lon  : {ev.latitude:.5f}, {ev.longitude:.5f}")
    print(f"Depth km : {ev.depth_km}")

    if args.out:
        payload = {
            "event_id": ev.event_id,
            "time_utc": ms_to_utc_str(ev.time_ms),
            "place": ev.place,
            "magnitude": ev.magnitude,
            "latitude": ev.latitude,
            "longitude": ev.longitude,
            "depth_km": ev.depth_km,
        }
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"\nSaved JSON -> {args.out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
