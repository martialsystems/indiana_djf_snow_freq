# Copyright (c) 2026 Martial Systems LLC
"""Live GHCND DJF SNOW. Empty or thin required cores stop. Belt stations stay out."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import numpy as np

from snowfreq.config import (
    BELT_OUT,
    COMPLETE_FRAC,
    CORE_IDS,
    CORE_STATIONS,
    MIN_TRAIN_WINTERS,
)
from snowfreq.errors import FetchError
from snowfreq.ghcnd import load_station_inventory, load_station_snow
from snowfreq.http import get_bytes
from snowfreq.labels import above_normal, assemble_djf
from snowfreq.normals import load_frozen_normals
from snowfreq.pack import WinterPack
from snowfreq.split import TRAIN, role


def _meta_for(sid: str, inventory: dict[str, dict[str, Any]], fallback_name: str) -> dict[str, Any]:
    rec = inventory.get(sid) or {}
    return {
        "station_id": sid,
        "name": rec.get("name") or fallback_name,
        "lat": float(rec.get("lat") or 0.0),
        "lon": float(rec.get("lon") or 0.0),
    }


def _rows_for_station(
    *,
    sid: str,
    name: str,
    lat: float,
    lon: float,
    days: list,
    normal_in: float,
    floor: float = COMPLETE_FRAC,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    winters = assemble_djf(days, floor=floor)
    holes: dict[str, Any] = {"station_id": sid, "incomplete": []}
    rows: list[dict[str, Any]] = []
    first_complete: int | None = None
    for wid in sorted(winters):
        rec = winters[wid]
        if rec["complete"] < 1.0:
            holes["incomplete"].append({"winter_id": int(wid), "complete_frac": rec["complete_frac"]})
            continue
        if first_complete is None:
            first_complete = int(wid)
        snow = float(rec["snow_in"])
        rows.append(
            {
                "station_id": sid,
                "name": name,
                "lat": lat,
                "lon": lon,
                "winter_id": int(wid),
                "snow_in": snow,
                "snow_normal_in": float(normal_in),
                "above": above_normal(snow, normal_in),
                "complete_frac": float(rec["complete_frac"]),
            }
        )
    holes["first_complete"] = first_complete
    holes["n_complete"] = len(rows)
    return rows, holes


def _train_n(rows: list[dict[str, Any]], *, start: int) -> int:
    return sum(
        1
        for r in rows
        if role(r["winter_id"]) == TRAIN and int(r["winter_id"]) >= int(start)
    )


def fetch_live(*, cache_dir: Path, getter: Callable[[str], bytes] = get_bytes) -> tuple[WinterPack, dict[str, Any]]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    normals = load_frozen_normals()
    inventory = load_station_inventory(cache_dir, getter=getter)
    all_rows: list[dict[str, Any]] = []
    holes: list[dict[str, Any]] = []
    first_complete: dict[str, int] = {}

    for sid, name in CORE_STATIONS:
        if sid not in normals:
            raise FetchError(f"frozen parent normal missing for required core {sid}")
        try:
            days = load_station_snow(sid, cache_dir, getter=getter)
        except FetchError:
            raise FetchError(f"empty GHCND SNOW for required core {sid}") from None
        meta = _meta_for(sid, inventory, name)
        rows, hole = _rows_for_station(
            sid=sid,
            name=meta["name"],
            lat=meta["lat"],
            lon=meta["lon"],
            days=days,
            normal_in=float(normals[sid]),
        )
        if hole.get("first_complete") is None:
            raise FetchError(f"required core {sid} has no complete DJF SNOW")
        first_complete[sid] = int(hole["first_complete"])
        all_rows.extend(rows)
        holes.append(hole)

    for sid, name in BELT_OUT:
        holes.append({"station_id": sid, "name": name, "dropped": True, "reason": "belt station stays out"})

    if any(r["station_id"] in {s for s, _ in BELT_OUT} for r in all_rows):
        raise FetchError("belt station leaked into the four-core pack")
    missing_cores = set(CORE_IDS) - {r["station_id"] for r in all_rows}
    if missing_cores:
        raise FetchError(f"required cores missing after QC: {sorted(missing_cores)}")

    common_start = max(first_complete.values())
    train_counts = {sid: _train_n([r for r in all_rows if r["station_id"] == sid], start=common_start) for sid in CORE_IDS}
    thin = {sid: n for sid, n in train_counts.items() if n < MIN_TRAIN_WINTERS}
    if thin:
        raise FetchError(
            "common DJF window too short for Sen: "
            f"common_start={common_start} first_complete={first_complete} train_n={train_counts}"
        )

    kept = [r for r in all_rows if int(r["winter_id"]) >= int(common_start)]
    pack = WinterPack(
        station_id=np.array([r["station_id"] for r in kept], dtype=object),
        name=np.array([r["name"] for r in kept], dtype=object),
        lat=np.array([r["lat"] for r in kept], dtype=float),
        lon=np.array([r["lon"] for r in kept], dtype=float),
        winter_id=np.array([r["winter_id"] for r in kept], dtype=int),
        snow_in=np.array([r["snow_in"] for r in kept], dtype=float),
        snow_normal_in=np.array([r["snow_normal_in"] for r in kept], dtype=float),
        above=np.array([r["above"] for r in kept], dtype=int),
        complete_frac=np.array([r["complete_frac"] for r in kept], dtype=float),
        source="live",
        extra={
            "holes": holes,
            "first_complete": first_complete,
            "common_start": int(common_start),
            "train_n": train_counts,
            "normals": {sid: float(normals[sid]) for sid in CORE_IDS},
            "belt_in_core_mean": False,
            "refit_normal": False,
            "snowy_year_select": False,
        },
    )
    meta = {
        "n_stations": pack.n_stations,
        "n_rows": pack.n_rows,
        "product": "GHCND DJF SNOW",
        "units": "probability",
        "common_start": int(common_start),
        "first_complete": first_complete,
        "train_n": train_counts,
        "normals": {sid: float(normals[sid]) for sid in CORE_IDS},
        "cache_dir": str(cache_dir),
        "belt_in_core_mean": False,
        "refit_normal": False,
    }
    return pack, meta
