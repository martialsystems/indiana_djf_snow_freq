# Copyright (c) 2026 Martial Systems LLC

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from snowfreqforge._bootstrap import ensure_paths

ensure_paths()

from graphforge.product_law import LawBlockedError

from snowfreqforge.gate import (
    require_claims,
    require_completeness,
    require_label,
    require_no_hydro,
    require_pages,
    require_split,
    require_stage0,
)
from snowfreqforge.product_laws import laws


def test_laws() -> None:
    require_no_hydro(thread_id="t.h.ok")
    with pytest.raises(LawBlockedError):
        require_no_hydro(p_sfha_feature=True, thread_id="t.h.p")
    require_label(djf_snow_label=True, thread_id="t.l.ok")
    with pytest.raises(LawBlockedError):
        require_label(djf_snow_label=True, first_snow_as_label=True, thread_id="t.l.date")
    with pytest.raises(LawBlockedError):
        require_label(djf_snow_label=True, inches_sen_as_product=True, thread_id="t.l.in")
    require_completeness(floor_ok=True, thread_id="t.c.ok")
    with pytest.raises(LawBlockedError):
        require_completeness(floor_ok=True, belt_in_core_mean=True, thread_id="t.c.belt")
    require_split(thread_id="t.t.ok")
    with pytest.raises(LawBlockedError):
        require_split(enso_predictor=True, thread_id="t.t.enso")
    with pytest.raises(LawBlockedError):
        require_split(refit_normal=True, thread_id="t.t.norm")
    with pytest.raises(LawBlockedError):
        require_split(snowy_year_select=True, thread_id="t.t.snowy")
    require_claims(n_figures=2, thread_id="t.k.ok")
    with pytest.raises(LawBlockedError):
        require_claims(n_figures=3, thread_id="t.k.fig")
    with pytest.raises(LawBlockedError):
        require_claims(climate_change=True, thread_id="t.k.cc")
    require_pages(page_in_scope=False, thread_id="t.p.ok")
    with pytest.raises(LawBlockedError):
        require_pages(page_in_scope=True, slope_beats_rate=False, thread_id="t.p.loss")
    require_stage0(live=True, fixture_ok=True, thread_id="t.s.ok")
    with pytest.raises(LawBlockedError):
        require_stage0(live=True, fixture_ok=False, thread_id="t.s.early")
    assert {row["id"] for row in laws()} == {
        "snowfreq.no_hydro",
        "snowfreq.label",
        "snowfreq.completeness",
        "snowfreq.temporal_split",
        "snowfreq.claim_bans",
        "snowfreq.pages",
        "snowfreq.stage0",
    }
