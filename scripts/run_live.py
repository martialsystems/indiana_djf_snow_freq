#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC
"""Live GHCND DJF above-normal frequency. Empty or thin core SNOW stops."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "src")]

from snowfreq.errors import FetchError, NormalError  # noqa: E402
from snowfreq.pipeline import run_live  # noqa: E402


def main() -> int:
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "logs" / "in_live"
    cache = Path(sys.argv[2]) if len(sys.argv) > 2 else REPO / "data" / "raw"
    try:
        report = run_live(dest, cache_dir=cache)
    except (FetchError, NormalError) as exc:
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "fetch_stop.txt").write_text(str(exc) + "\n", encoding="utf-8")
        print(exc)
        return 2
    print(report["question"])
    hold = report["holdout"]
    print(
        "Sen Brier",
        round(hold["slope"]["brier"], 4),
        "rate Brier",
        round(hold["rate"]["brier"], 4),
        "last winter Brier",
        round(hold["last_year"]["brier"], 4),
        "n",
        hold["n"],
    )
    print("slope_beats_rate_brier", report["slope_beats_rate_brier"])
    print("common_start", report.get("common_start"))
    print(report["figures"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
