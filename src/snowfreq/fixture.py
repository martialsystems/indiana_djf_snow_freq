# Copyright (c) 2026 Martial Systems LLC
"""Synthetic 0/1 winters with a planted Sen slope. Does not rescue live skill."""

from __future__ import annotations

import numpy as np

from snowfreq.config import (
    CONFIRM_WINTER,
    CORE_STATIONS,
    FROZEN_NORMALS_IN,
    TRAIN_LAST_WINTER,
)
from snowfreq.pack import WinterPack

_COORDS = {
    "USW00014848": (41.71, -86.32),
    "USW00014827": (41.12, -85.19),
    "USW00093819": (39.72, -86.29),
    "USW00093817": (38.04, -87.53),
}
# Latest first-complete is Indianapolis 1980, so the common window is 40 train winters.
_FIRST = {
    "USW00014848": 1975,
    "USW00014827": 1978,
    "USW00093819": 1980,
    "USW00093817": 1979,
}
# Balanced 0/1 split so Theil-Sen pairwise slopes are not a zero median.
_STEP = {
    "USW00014848": 1999,
    "USW00014827": 2000,
    "USW00093819": 2001,
    "USW00093817": 2002,
}


def build_fixture() -> WinterPack:
    rows: list[dict] = []
    for sid, city in CORE_STATIONS:
        lat, lon = _COORDS[sid]
        normal = float(FROZEN_NORMALS_IN[sid])
        start = _FIRST[sid]
        step = _STEP[sid]
        for wid in range(start, CONFIRM_WINTER + 1):
            above = 1 if wid >= step else 0
            snow = normal + (4.0 if above else -4.0)
            rows.append(
                {
                    "station_id": sid,
                    "name": city,
                    "lat": lat,
                    "lon": lon,
                    "winter_id": wid,
                    "snow_in": snow,
                    "snow_normal_in": normal,
                    "above": above,
                    "complete_frac": 1.0,
                }
            )
    common_start = max(_FIRST.values())
    kept = [r for r in rows if int(r["winter_id"]) >= common_start]
    train_n = {
        sid: sum(1 for r in kept if r["station_id"] == sid and int(r["winter_id"]) <= TRAIN_LAST_WINTER)
        for sid, _ in CORE_STATIONS
    }
    return WinterPack(
        station_id=np.array([r["station_id"] for r in kept], dtype=object),
        name=np.array([r["name"] for r in kept], dtype=object),
        lat=np.array([r["lat"] for r in kept], dtype=float),
        lon=np.array([r["lon"] for r in kept], dtype=float),
        winter_id=np.array([r["winter_id"] for r in kept], dtype=int),
        snow_in=np.array([r["snow_in"] for r in kept], dtype=float),
        snow_normal_in=np.array([r["snow_normal_in"] for r in kept], dtype=float),
        above=np.array([r["above"] for r in kept], dtype=int),
        complete_frac=np.array([r["complete_frac"] for r in kept], dtype=float),
        source="fixture",
        extra={
            "first_complete": dict(_FIRST),
            "common_start": int(common_start),
            "train_n": train_n,
            "normals": dict(FROZEN_NORMALS_IN),
            "belt_in_core_mean": False,
            "refit_normal": False,
            "snowy_year_select": False,
            "planted_slope": True,
        },
    )
