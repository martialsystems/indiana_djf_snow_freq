# Copyright (c) 2026 Martial Systems LLC
"""Stage 0 fixture. Live fetch-or-stop. Two figures. Pages refused unless Sen beats the rate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from snowfreq.claims import require_clean, require_paths_clean
from snowfreq.config import QUESTION, REPO_ROOT
from snowfreq.fetch import fetch_live
from snowfreq.figure import write_two
from snowfreq.fixture import build_fixture
from snowfreq.skill import score_pack

try:
    from snowfreqforge.gate import (
        require_claims,
        require_completeness,
        require_label,
        require_no_hydro,
        require_pages,
        require_split,
        require_stage0,
    )
except ImportError:  # pragma: no cover

    def require_claims(**kwargs):
        del kwargs

    def require_completeness(**kwargs):
        del kwargs

    def require_label(**kwargs):
        del kwargs

    def require_no_hydro(**kwargs):
        del kwargs

    def require_pages(**kwargs):
        del kwargs

    def require_split(**kwargs):
        del kwargs

    def require_stage0(**kwargs):
        del kwargs


def _jsonable(report: dict[str, Any]) -> dict[str, Any]:
    return dict(report)


def _run(log_dir: Path, *, pack, fixture: bool, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    require_no_hydro(thread_id="hydro")
    require_label(
        djf_snow_label=True,
        prcp_as_label=False,
        snwd_as_label=False,
        first_snow_as_label=False,
        inches_sen_as_product=False,
        thread_id="label",
    )
    require_clean(QUESTION, source="question")
    fit = score_pack(pack)
    extra_pack = pack.extra or {}
    require_completeness(
        floor_ok=True,
        belt_in_core_mean=bool(extra_pack.get("belt_in_core_mean")),
        thin_kept=False,
        thread_id="complete",
    )
    require_split(
        temporal_ok=True,
        confirm_in_train=bool(fit["confirm_in_train"]),
        confirm_in_slope=bool(fit["confirm_in_slope"]),
        confirm_in_rate=bool(fit["confirm_in_rate"]),
        random_split=bool(fit["random_split"]),
        enso_predictor=False,
        cpc_predictor=False,
        radaronly_predictor=False,
        refit_normal=bool(extra_pack.get("refit_normal")),
        snowy_year_select=bool(extra_pack.get("snowy_year_select")),
        thread_id="split",
    )
    if not fixture:
        stage0 = REPO_ROOT / "logs" / "stage0_fixture" / "stage0_report.json"
        require_stage0(fixture_ok=stage0.is_file(), live=True, thread_id="stage0")
    paths = write_two(log_dir, fit=fit, live=not fixture)
    require_claims(
        n_figures=len(paths),
        restamp_parent=False,
        climate_change=False,
        getting_less_snow=False,
        will_get_inches=False,
        flood=False,
        p_sfha=False,
        casualty=False,
        thread_id="claims",
    )
    readme_yes = bool(fit["slope_beats_rate_brier"]) and not fixture
    require_pages(
        page_in_scope=bool(fit["page_in_scope"]),
        slope_beats_rate=bool(fit["slope_beats_rate_brier"]),
        readme_states_yes=readme_yes,
        thread_id="pages",
    )
    log_dir.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "stage": "0" if fixture else "C",
        "fixture": fixture,
        "question": QUESTION,
        "source": pack.source,
        "n_rows": pack.n_rows,
        "n_stations": pack.n_stations,
        "units": "probability",
        "element": "SNOW",
        "season": "DJF",
        "p_sfha_feature": False,
        "hand_feature": False,
        "nora_q": False,
        "nwm_file": False,
        "prcp_as_label": False,
        "snwd_as_label": False,
        "first_snow_as_label": False,
        "inches_sen_as_product": False,
        "refit_normal": False,
        "snowy_year_select": False,
        "belt_in_core_mean": False,
        "page_in_scope": False,
        "slope_beats_rate_brier": fit["slope_beats_rate_brier"],
        "slope_beats_rate_mae": fit["slope_beats_rate_mae"],
        "brier_mae_agree": fit["brier_mae_agree"],
        "figures": paths,
        "normals": extra_pack.get("normals"),
        "first_complete": extra_pack.get("first_complete"),
        "common_start": fit["common_start"],
        "train_anchor": fit["train_anchor"],
        "four_core_mean_rate": fit["four_core_mean_rate"],
        "holdout": fit["holdout"],
        "confirm": fit["confirm"],
        "by_station": fit["by_station"],
        "holdout_rows": fit["holdout_rows"],
        "confirm_rows": fit["confirm_rows"],
        "train_rows": fit["train_rows"],
        "confirm_in_train": False,
        "confirm_in_slope": False,
        "confirm_in_rate": False,
        "random_split": False,
        "holdout_winters": fit["holdout_winters"],
        "estimator": "sen",
    }
    if extra:
        report.update(extra)
    require_clean(json.dumps(_jsonable(report), default=str), source="report")
    (log_dir / "stage0_report.json" if fixture else log_dir / "stage_c_report.json").write_text(
        json.dumps(_jsonable(report), indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    require_paths_clean(
        [
            REPO_ROOT / "README.md",
            log_dir / ("stage0_report.json" if fixture else "stage_c_report.json"),
        ]
    )
    return report


def stage0_fixture(log_dir: Path) -> dict[str, Any]:
    pack = build_fixture()
    return _run(log_dir, pack=pack, fixture=True)


def run_live(log_dir: Path, *, cache_dir: Path) -> dict[str, Any]:
    pack, meta = fetch_live(cache_dir=cache_dir)
    public_meta = {k: meta[k] for k in meta if k != "holes"}
    return _run(log_dir, pack=pack, fixture=False, extra={"fetch_meta": public_meta})
