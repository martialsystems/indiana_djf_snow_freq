# Copyright (c) 2026 Martial Systems LLC
"""Fail closed: above-normal frequency vs a flat rate, not a climate story."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from snowfreq.errors import ClaimBanError

_BANS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("casualty", re.compile(r"\b(deaths?|fatalit(?:y|ies)|casualt(?:y|ies)|killed)\b", re.I)),
    ("frost_warning", re.compile(r"(?<!not a )\bfrost warning\b", re.I)),
    ("freeze_warning", re.compile(r"(?<!not a )\bfreeze warning\b", re.I)),
    ("will_get_inches", re.compile(r"will get\s+\d+\s+inches", re.I)),
    ("flood_warning", re.compile(r"\bflood warning\b|\bflood AI\b", re.I)),
    ("p_sfha", re.compile(r"\bP\(sfha\b|\bp_sfha\b", re.I)),
    ("climate_change", re.compile(r"\bclimate change\b", re.I)),
    ("getting_less_snow", re.compile(r"\bgetting less snow\b", re.I)),
    ("frost_outlook", re.compile(r"\bfrost outlook\b", re.I)),
)


def scan_text(text: str) -> list[str]:
    hits = [name for name, pat in _BANS if pat.search(text or "")]
    if "\u2014" in (text or ""):
        hits.append("em_dash")
    return hits


def require_clean(text: str, *, source: str) -> None:
    hits = scan_text(text)
    if hits:
        raise ClaimBanError(f"{source}: banned claims {hits}")


def require_paths_clean(paths: Iterable[Path]) -> None:
    for path in paths:
        if path.is_file():
            require_clean(path.read_text(encoding="utf-8"), source=str(path))
