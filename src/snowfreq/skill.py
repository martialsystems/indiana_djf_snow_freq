# Copyright (c) 2026 Martial Systems LLC
"""Train-era Sen slope vs train-era above-normal rate. Brier leads."""

from __future__ import annotations

from typing import Any

import numpy as np

from snowfreq.config import CORE_IDS, CORE_STATIONS, TRAIN_LAST_WINTER
from snowfreq.pack import WinterPack
from snowfreq.sen import clip01, ols_slope, sen_slope
from snowfreq.split import CONFIRM, HOLDOUT, TRAIN, assert_split, role


def _brier(y: np.ndarray, p: np.ndarray) -> float:
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    if y.size == 0:
        return float("nan")
    return float(np.mean((p - y) ** 2))


def _mae(y: np.ndarray, p: np.ndarray) -> float:
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    if y.size == 0:
        return float("nan")
    return float(np.mean(np.abs(p - y)))


def _metrics(y: list[int], p: list[float]) -> dict[str, float]:
    yy = np.asarray(y, dtype=float)
    pp = np.asarray(p, dtype=float)
    return {"n": int(yy.size), "brier": _brier(yy, pp), "mae": _mae(yy, pp)}


def score_pack(pack: WinterPack) -> dict[str, Any]:
    extra = pack.extra or {}
    common_start = int(extra.get("common_start") or pack.winter_id.min())
    assert_split(confirm_in_train=False, confirm_in_slope=False, confirm_in_rate=False, random_split=False)

    train_years = [y for y in range(common_start, TRAIN_LAST_WINTER + 1)]
    train_anchor = float(np.mean(np.asarray(train_years, dtype=float)))

    by_station: dict[str, dict[str, Any]] = {}
    hold_rows: list[dict[str, Any]] = []
    conf_rows: list[dict[str, Any]] = []
    train_rows: list[dict[str, Any]] = []

    for sid, city in CORE_STATIONS:
        mask = pack.station_id == sid
        wids = pack.winter_id[mask].astype(int)
        above = pack.above[mask].astype(int)
        snow = pack.snow_in[mask].astype(float)
        normals = pack.snow_normal_in[mask].astype(float)
        names = pack.name[mask]
        lats = pack.lat[mask]
        lons = pack.lon[mask]
        order = np.argsort(wids)
        wids, above, snow, normals, names, lats, lons = (
            wids[order],
            above[order],
            snow[order],
            normals[order],
            names[order],
            lats[order],
            lons[order],
        )
        train_m = np.array([role(int(w)) == TRAIN for w in wids])
        if int(train_m.sum()) < 2:
            raise ValueError(f"{sid} has too few train winters for Sen")
        x = wids[train_m].astype(float)
        y = above[train_m].astype(float)
        slope = sen_slope(x, y)
        ols = ols_slope(x, y)
        rate = float(np.mean(y))
        lookup = {int(w): int(a) for w, a in zip(wids, above)}
        hold_y: list[int] = []
        hold_ps: list[float] = []
        hold_pr: list[float] = []
        hold_y_last: list[int] = []
        hold_pl: list[float] = []
        n_above_hold = 0
        n_hold = 0
        name = str(names[0]) if names.size else city
        for i, wid in enumerate(wids):
            split = role(int(wid))
            if split == TRAIN:
                train_rows.append(
                    {
                        "station_id": sid,
                        "city": city,
                        "winter_id": int(wid),
                        "above": int(above[i]),
                        "snow_in": float(snow[i]),
                        "snow_normal_in": float(normals[i]),
                    }
                )
                continue
            if split not in {HOLDOUT, CONFIRM}:
                continue
            p_s = clip01(rate + slope * (float(wid) - train_anchor))
            p_r = clip01(rate)
            last = lookup.get(int(wid) - 1)
            row = {
                "station_id": sid,
                "name": name,
                "city": city,
                "lat": float(lats[i]),
                "lon": float(lons[i]),
                "winter_id": int(wid),
                "split": split,
                "snow_in": float(snow[i]),
                "snow_normal_in": float(normals[i]),
                "above": int(above[i]),
                "p_slope": p_s,
                "p_rate": p_r,
                "p_last": None if last is None else float(last),
                "last_year_above": last,
            }
            if split == HOLDOUT:
                hold_rows.append(row)
                n_hold += 1
                n_above_hold += int(above[i])
                hold_y.append(int(above[i]))
                hold_ps.append(p_s)
                hold_pr.append(p_r)
                if last is not None:
                    hold_y_last.append(int(above[i]))
                    hold_pl.append(float(last))
            else:
                conf_rows.append(row)
        by_station[sid] = {
            "name": name,
            "city": city,
            "station_id": sid,
            "train_n": int(train_m.sum()),
            "train_rate": rate,
            "sen_slope_per_year": float(slope),
            "sen_slope_per_decade": float(slope) * 10.0,
            "ols_slope_per_year": float(ols),
            "holdout_n": n_hold,
            "holdout_above_n": n_above_hold,
            "holdout_above": f"{n_above_hold}/{n_hold}" if n_hold else "0/0",
            "slope": _metrics(hold_y, hold_ps),
            "rate": _metrics(hold_y, hold_pr),
            "last_year": _metrics(hold_y_last, hold_pl),
        }

    def _pool(rows: list[dict[str, Any]], key: str) -> dict[str, float]:
        y = [int(r["above"]) for r in rows if r.get(key) is not None]
        p = [float(r[key]) for r in rows if r.get(key) is not None]
        return _metrics(y, p)

    hold_core = [r for r in hold_rows if r["station_id"] in CORE_IDS]
    pooled_slope = _pool(hold_core, "p_slope")
    pooled_rate = _pool(hold_core, "p_rate")
    pooled_last = _pool(hold_core, "p_last")
    mean_rate = float(np.mean([by_station[sid]["train_rate"] for sid in CORE_IDS]))
    slope_beats = float(pooled_slope["brier"]) < float(pooled_rate["brier"])
    mae_beats = float(pooled_slope["mae"]) < float(pooled_rate["mae"])
    return {
        "n_rows": pack.n_rows,
        "n_stations": pack.n_stations,
        "common_start": common_start,
        "train_last": TRAIN_LAST_WINTER,
        "train_anchor": train_anchor,
        "train_anchor_winter_id": train_anchor,
        "four_core_mean_rate": mean_rate,
        "by_station": by_station,
        "holdout": {
            "n": len(hold_core),
            "slope": pooled_slope,
            "rate": pooled_rate,
            "last_year": pooled_last,
        },
        "confirm": {
            "n": len(conf_rows),
            "slope": _pool(conf_rows, "p_slope"),
            "rate": _pool(conf_rows, "p_rate"),
            "last_year": _pool(conf_rows, "p_last"),
        },
        "holdout_rows": hold_core,
        "confirm_rows": conf_rows,
        "train_rows": train_rows,
        "slope_beats_rate_brier": slope_beats,
        "slope_beats_rate_mae": mae_beats,
        "brier_mae_agree": slope_beats == mae_beats,
        "page_in_scope": False,
        "confirm_in_train": False,
        "confirm_in_slope": False,
        "confirm_in_rate": False,
        "random_split": False,
        "units": "probability",
        "holdout_winters": list(range(2020, 2026)),
    }
