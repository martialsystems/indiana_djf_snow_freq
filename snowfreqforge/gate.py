# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

from typing import Any

from snowfreqforge._bootstrap import ensure_paths

ensure_paths()

from graphforge.product_law import require_law

from snowfreqforge.graphs.claim_bans import build_graph as build_claims
from snowfreqforge.graphs.completeness import build_graph as build_complete
from snowfreqforge.graphs.label import build_graph as build_label
from snowfreqforge.graphs.no_hydro import build_graph as build_hydro
from snowfreqforge.graphs.pages import build_graph as build_pages
from snowfreqforge.graphs.stage0 import build_graph as build_stage0
from snowfreqforge.graphs.temporal_split import build_graph as build_split


def require_no_hydro(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "snowfreq_hydro"))
    state = {
        "p_sfha_feature": False,
        "p_sfha_label": False,
        "hand_feature": False,
        "nora_q": False,
        "nwm_file": False,
    }
    state.update(flags)
    require_law(build_hydro(), state, allow_decisions=["allow"], law_id="snowfreq.no_hydro", thread_id=thread_id, raise_error=True)


def require_label(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "snowfreq_label"))
    state = {
        "djf_snow_label": False,
        "prcp_as_label": False,
        "snwd_as_label": False,
        "first_snow_as_label": False,
        "inches_sen_as_product": False,
    }
    state.update(flags)
    require_law(build_label(), state, allow_decisions=["allow"], law_id="snowfreq.label", thread_id=thread_id, raise_error=True)


def require_completeness(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "snowfreq_complete"))
    state = {
        "floor_ok": False,
        "thin_kept": False,
        "belt_in_core_mean": False,
    }
    state.update(flags)
    require_law(
        build_complete(),
        state,
        allow_decisions=["allow"],
        law_id="snowfreq.completeness",
        thread_id=thread_id,
        raise_error=True,
    )


def require_split(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "snowfreq_split"))
    state = {
        "temporal_ok": True,
        "confirm_in_train": False,
        "confirm_in_slope": False,
        "confirm_in_rate": False,
        "random_split": False,
        "enso_predictor": False,
        "cpc_predictor": False,
        "radaronly_predictor": False,
        "refit_normal": False,
        "snowy_year_select": False,
    }
    state.update(flags)
    require_law(
        build_split(),
        state,
        allow_decisions=["allow"],
        law_id="snowfreq.temporal_split",
        thread_id=thread_id,
        raise_error=True,
    )


def require_claims(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "snowfreq_claims"))
    state = {
        "climate_change": False,
        "getting_less_snow": False,
        "will_get_inches": False,
        "flood": False,
        "p_sfha": False,
        "casualty": False,
        "restamp_parent": False,
        "n_figures": 2,
    }
    state.update(flags)
    require_law(
        build_claims(),
        state,
        allow_decisions=["allow"],
        law_id="snowfreq.claim_bans",
        thread_id=thread_id,
        raise_error=True,
    )


def require_pages(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "snowfreq_pages"))
    state = {
        "page_in_scope": False,
        "slope_beats_rate": False,
        "readme_states_yes": False,
    }
    state.update(flags)
    require_law(build_pages(), state, allow_decisions=["allow"], law_id="snowfreq.pages", thread_id=thread_id, raise_error=True)


def require_stage0(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "snowfreq_stage0"))
    state = {"live": False, "fixture_ok": False}
    state.update(flags)
    require_law(build_stage0(), state, allow_decisions=["allow"], law_id="snowfreq.stage0", thread_id=thread_id, raise_error=True)
