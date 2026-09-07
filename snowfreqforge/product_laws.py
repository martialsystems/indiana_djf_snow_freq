# Copyright (c) 2026 Martial Systems LLC
"""Refuse laws. Verify-before-done is the finish gate."""

from __future__ import annotations

from typing import Any


def laws() -> list[dict[str, Any]]:
    from snowfreqforge.graphs.claim_bans import build_graph as claim_bans
    from snowfreqforge.graphs.completeness import build_graph as completeness
    from snowfreqforge.graphs.label import build_graph as label
    from snowfreqforge.graphs.no_hydro import build_graph as no_hydro
    from snowfreqforge.graphs.pages import build_graph as pages
    from snowfreqforge.graphs.stage0 import build_graph as stage0
    from snowfreqforge.graphs.temporal_split import build_graph as temporal_split

    return [
        {
            "id": "snowfreq.no_hydro",
            "build": no_hydro,
            "state": {
                "p_sfha_feature": False,
                "p_sfha_label": False,
                "hand_feature": False,
                "nora_q": False,
                "nwm_file": False,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "snowfreq.label",
            "build": label,
            "state": {
                "djf_snow_label": True,
                "prcp_as_label": False,
                "snwd_as_label": False,
                "first_snow_as_label": False,
                "inches_sen_as_product": False,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "snowfreq.completeness",
            "build": completeness,
            "state": {"floor_ok": True, "thin_kept": False, "belt_in_core_mean": False},
            "allow_decisions": ["allow"],
        },
        {
            "id": "snowfreq.temporal_split",
            "build": temporal_split,
            "state": {
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
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "snowfreq.claim_bans",
            "build": claim_bans,
            "state": {
                "climate_change": False,
                "getting_less_snow": False,
                "will_get_inches": False,
                "flood": False,
                "p_sfha": False,
                "casualty": False,
                "restamp_parent": False,
                "n_figures": 2,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "snowfreq.pages",
            "build": pages,
            "state": {"page_in_scope": False, "slope_beats_rate": False, "readme_states_yes": False},
            "allow_decisions": ["allow"],
        },
        {
            "id": "snowfreq.stage0",
            "build": stage0,
            "state": {"live": False, "fixture_ok": True},
            "allow_decisions": ["allow"],
        },
    ]
