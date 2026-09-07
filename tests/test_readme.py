# Copyright (c) 2026 Martial Systems LLC

from pathlib import Path

from snowfreq.claims import scan_text
from snowfreq.config import QUESTION

REPO = Path(__file__).resolve().parents[1]


def test_readme_opens_with_the_question() -> None:
    text = (REPO / "README.md").read_text(encoding="utf-8")
    body = "\n".join(text.splitlines()[1:]).lstrip()
    assert body.startswith(QUESTION)
    assert body.splitlines()[2].startswith("No.")
    assert "`6de7758`" in text
    assert "1991-2020" in text
    assert "0.1947" in text
    assert "Pages stay off" in text
    assert "not a regional trend" in text
    assert "logs/in_live/series.png" in text
    assert "logs/in_live/brier_bars.png" in text
    assert "9aa7935" in text
    assert "82ce0ce" in text
    assert "0ace8a1" in text
    assert "USW00014848" in text
    assert "USW00004846" in text
    assert "USC00125604" in text
    assert "The fixture is not the result" in text
    assert "Research index: https://gist.github.com/martialsystems/66b896b0a4a0b8cba2b478aef64312f3" in text
    assert "b5f900aad37487bb8c0206a321c1ed5c" in text
    assert "Open_the_research_console" not in text
    assert "series.png" in text
    assert "brier_bars.png" in text
    assert scan_text(text) == []
    assert "\u2014" not in text
    assert "What it is not" not in text
    assert "climate change" not in text.lower()
    assert "getting less snow" not in text.lower()
    assert ".venv/bin/python -m pytest" in text
