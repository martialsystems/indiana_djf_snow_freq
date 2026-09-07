# Copyright (c) 2026 Martial Systems LLC
"""GHCND daily SNOW only. PRCP/SNWD/TMIN cannot substitute."""

from __future__ import annotations

import csv
import gzip
import io
from datetime import date
from pathlib import Path
from typing import Any, Callable

from snowfreq.config import GHCND_STATION_URL, GHCND_STATIONS_URL
from snowfreq.errors import FetchError
from snowfreq.http import get_bytes
from snowfreq.labels import snow_mm_to_inches


def parse_station_line(line: str) -> dict[str, Any] | None:
    if len(line) < 41:
        return None
    sid = line[0:11].strip()
    try:
        lat = float(line[12:20])
        lon = float(line[21:30])
        elev = float(line[31:37])
    except ValueError:
        return None
    name = line[41:71].strip() if len(line) >= 71 else sid
    return {"station_id": sid, "lat": lat, "lon": lon, "elev_m": elev, "name": name}


def load_station_inventory(cache_dir: Path, getter: Callable[[str], bytes] = get_bytes) -> dict[str, dict[str, Any]]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / "ghcnd-stations.txt"
    if not path.is_file() or path.stat().st_size == 0:
        path.write_bytes(getter(GHCND_STATIONS_URL))
    text = path.read_text(encoding="utf-8", errors="replace")
    out: dict[str, dict[str, Any]] = {}
    for line in text.splitlines():
        rec = parse_station_line(line)
        if rec:
            out[rec["station_id"]] = rec
    if not out:
        raise FetchError("empty GHCND station inventory")
    return out


def parse_snow_csv(text: str) -> list[tuple[date, float]]:
    rows: list[tuple[date, float]] = []
    for rec in csv.reader(io.StringIO(text)):
        if len(rec) < 4:
            continue
        if rec[2].strip() != "SNOW":
            continue
        qflag = rec[5].strip() if len(rec) > 5 else ""
        if qflag:
            continue
        try:
            raw = int(rec[3])
        except ValueError:
            continue
        if raw == -9999:
            continue
        day = date.fromisoformat(f"{rec[1][0:4]}-{rec[1][4:6]}-{rec[1][6:8]}")
        rows.append((day, snow_mm_to_inches(raw)))
    return rows


def load_station_snow(sid: str, cache_dir: Path, getter: Callable[[str], bytes] = get_bytes) -> list[tuple[date, float]]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"{sid}.csv.gz"
    if not path.is_file() or path.stat().st_size == 0:
        body = getter(GHCND_STATION_URL.format(sid=sid))
        if not body:
            raise FetchError(f"empty GHCND {sid}")
        path.write_bytes(body)
    raw = gzip.decompress(path.read_bytes()).decode("utf-8", errors="replace")
    days = parse_snow_csv(raw)
    if not days:
        raise FetchError(f"GHCND {sid} has no SNOW")
    return days
