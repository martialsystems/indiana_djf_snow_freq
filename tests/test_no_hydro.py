# Copyright (c) 2026 Martial Systems LLC

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
_IMPORT = re.compile(r"(?:from|import)\s+(p_sfha|hand|nwm)\b", re.I)
_PATH = re.compile(r"p_sfha\.tif|/HAND/|channel_rt|analysis_assim", re.I)


def test_src_does_not_import_hydro() -> None:
    hits: list[str] = []
    for path in (REPO / "src").rglob("*.py"):
        for line in path.read_text(encoding="utf-8").splitlines():
            code = line.split("#", 1)[0]
            if _IMPORT.search(code):
                hits.append(f"{path.relative_to(REPO)}: {line.strip()}")
    assert hits == []


def test_src_does_not_name_refused_files() -> None:
    hits: list[str] = []
    for path in (REPO / "src").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if _PATH.search(text):
            hits.append(str(path.relative_to(REPO)))
    assert hits == []
