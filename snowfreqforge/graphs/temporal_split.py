# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

from typing import Any

from snowfreqforge.graphs._common import binary_graph

_BAD = (
    "confirm_in_train",
    "confirm_in_slope",
    "confirm_in_rate",
    "random_split",
    "enso_predictor",
    "cpc_predictor",
    "radaronly_predictor",
    "refit_normal",
    "snowy_year_select",
)


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if not state.get("temporal_ok"):
        v.append("not_temporal")
    for k in _BAD:
        if state.get(k):
            v.append(k)
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="snowfreq.temporal_split",
        evaluate=_evaluate,
        extra=["temporal_ok", *_BAD],
    )
