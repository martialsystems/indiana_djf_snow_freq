# Copyright (c) 2026 Martial Systems LLC
"""DJF completeness. Belt stations stay out of the four-core mean."""

from __future__ import annotations

from typing import Any

from snowfreqforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if not state.get("floor_ok"):
        v.append("floor")
    if state.get("thin_kept"):
        v.append("thin_kept")
    if state.get("belt_in_core_mean"):
        v.append("belt_in_core_mean")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="snowfreq.completeness",
        evaluate=_evaluate,
        extra=["floor_ok", "thin_kept", "belt_in_core_mean"],
    )
