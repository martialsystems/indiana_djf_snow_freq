# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

from typing import Any

from snowfreqforge.graphs._common import binary_graph

_FLAGS = ("p_sfha_feature", "p_sfha_label", "hand_feature", "nora_q", "nwm_file")


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v = [k for k in _FLAGS if state.get(k)]
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(name="snowfreq.no_hydro", evaluate=_evaluate, extra=list(_FLAGS))
