# Copyright (c) 2026 Martial Systems LLC
"""Pages snow-frequency hero refused on a Brier loss."""

from __future__ import annotations

from typing import Any

from snowfreqforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if state.get("page_in_scope"):
        if not state.get("slope_beats_rate"):
            v.append("page_from_loss")
        elif not state.get("readme_states_yes"):
            v.append("page_without_readme_yes")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="snowfreq.pages",
        evaluate=_evaluate,
        extra=["page_in_scope", "slope_beats_rate", "readme_states_yes"],
    )
