# Copyright (c) 2026 Martial Systems LLC
"""Frozen 1991-2020 DJF snowfall normals. Do not refit from GHCND."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path

from snowfreq.config import CORE_IDS, FROZEN_NORMALS_IN, FROZEN_NORMALS_PATH, REPO_ROOT
from snowfreq.errors import NormalError


def parse_djf_snow_normal(text: str) -> float:
    months: dict[int, float] = {}
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or "MLY-SNOW-NORMAL" not in reader.fieldnames:
        raise NormalError("normals file missing MLY-SNOW-NORMAL")
    for rec in reader:
        try:
            month = int(float(rec.get("month") or rec.get("DATE") or "0"))
        except ValueError:
            continue
        raw = (rec.get("MLY-SNOW-NORMAL") or "").strip()
        if not raw or raw in {"-9999", ""}:
            continue
        try:
            months[month] = float(raw)
        except ValueError:
            continue
    if not {1, 2, 12}.issubset(months):
        raise NormalError("DJF snowfall normal incomplete")
    return float(months[12] + months[1] + months[2])


def load_frozen_normals(path: Path | None = None) -> dict[str, float]:
    src = path or FROZEN_NORMALS_PATH
    if not src.is_file():
        raise NormalError(f"frozen normals missing: {src}")
    raw = json.loads(src.read_text(encoding="utf-8"))
    out: dict[str, float] = {}
    for row in raw.get("stations") or []:
        sid = str(row.get("id") or "")
        if not sid:
            continue
        val = row.get("djf_snow_in")
        if val is None:
            raise NormalError(f"frozen normal missing inches for {sid}")
        out[sid] = float(val)
    missing = [sid for sid in CORE_IDS if sid not in out]
    if missing:
        raise NormalError(f"frozen parent normal missing for cores {missing}")
    for sid, expected in FROZEN_NORMALS_IN.items():
        if abs(out[sid] - expected) > 1e-9:
            raise NormalError(f"frozen normal for {sid} drifted from the parent lock")
    return {sid: out[sid] for sid in CORE_IDS}


def csv_normal_for(sid: str, frozen_dir: Path | None = None) -> float:
    folder = frozen_dir or (REPO_ROOT / "data" / "frozen")
    path = folder / f"{sid}_normals.csv"
    if not path.is_file():
        raise NormalError(f"frozen parent CSV missing for {sid}")
    return parse_djf_snow_normal(path.read_text(encoding="utf-8", errors="replace"))
