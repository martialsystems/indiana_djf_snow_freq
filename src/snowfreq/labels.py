# Copyright (c) 2026 Martial Systems LLC
"""DJF SNOW totals and the 0/1 above-normal classifier."""

from __future__ import annotations

import calendar
from collections import defaultdict
from datetime import date

from snowfreq.config import COMPLETE_FRAC, SNOW_MM_PER_IN


def snow_mm_to_inches(raw_mm: float) -> float:
    return float(raw_mm) / SNOW_MM_PER_IN


def winter_id_of(day: date) -> int:
    return day.year + 1 if day.month == 12 else day.year


def month_ndays(winter_id: int, month: int) -> int:
    if month == 2:
        return 29 if calendar.isleap(int(winter_id)) else 28
    if month in {1, 12}:
        return 31
    raise ValueError(f"DJF month required, got {month}")


def above_normal(snow_in: float, normal_in: float) -> int:
    return 1 if float(snow_in) > float(normal_in) else 0


def assemble_djf(
    days: list[tuple[date, float]],
    *,
    floor: float = COMPLETE_FRAC,
) -> dict[int, dict[str, float]]:
    """Sum DJF SNOW inches. Complete only if Dec, Jan, and Feb each clear the floor."""
    buckets: dict[int, dict[str, float]] = defaultdict(
        lambda: {"snow_in": 0.0, "n_dec": 0.0, "n_jan": 0.0, "n_feb": 0.0, "n_days": 0.0}
    )
    for day, inches in days:
        if day.month not in {12, 1, 2}:
            continue
        wid = winter_id_of(day)
        b = buckets[wid]
        b["snow_in"] += float(inches)
        b["n_days"] += 1.0
        if day.month == 12:
            b["n_dec"] += 1.0
        elif day.month == 1:
            b["n_jan"] += 1.0
        else:
            b["n_feb"] += 1.0
    out: dict[int, dict[str, float]] = {}
    for wid, b in buckets.items():
        n_dec = month_ndays(wid, 12)
        n_jan = month_ndays(wid, 1)
        n_feb = month_ndays(wid, 2)
        n_djf = n_dec + n_jan + n_feb
        frac_dec = b["n_dec"] / float(n_dec)
        frac_jan = b["n_jan"] / float(n_jan)
        frac_feb = b["n_feb"] / float(n_feb)
        frac = b["n_days"] / float(n_djf)
        complete = frac_dec >= floor and frac_jan >= floor and frac_feb >= floor
        out[int(wid)] = {
            "snow_in": float(b["snow_in"]),
            "complete_frac": float(frac),
            "frac_dec": float(frac_dec),
            "frac_jan": float(frac_jan),
            "frac_feb": float(frac_feb),
            "complete": 1.0 if complete else 0.0,
        }
    return out
