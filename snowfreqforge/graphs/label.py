# Copyright (c) 2026 Martial Systems LLC
"""DJF SNOW vs frozen normal is the label. SNWD, PRCP, first-snow date, and inches Sen are refused."""

from __future__ import annotations

from typing import Any

from snowfreqforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if not state.get("djf_snow_label"):
        v.append("not_djf_snow")
    for k in ("prcp_as_label", "snwd_as_label", "first_snow_as_label", "inches_sen_as_product"):
        if state.get(k):
            v.append(k)
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="snowfreq.label",
        evaluate=_evaluate,
        extra=["djf_snow_label", "prcp_as_label", "snwd_as_label", "first_snow_as_label", "inches_sen_as_product"],
    )
