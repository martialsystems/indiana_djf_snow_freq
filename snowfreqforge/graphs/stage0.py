# Copyright (c) 2026 Martial Systems LLC
"""Live scoring is refused until Stage 0 has a fixture report."""

from __future__ import annotations

from typing import Any

from snowfreqforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if state.get("live") and not state.get("fixture_ok"):
        v.append("live_before_stage0")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="snowfreq.stage0",
        evaluate=_evaluate,
        extra=["live", "fixture_ok"],
    )
