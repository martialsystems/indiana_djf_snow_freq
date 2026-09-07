# Copyright (c) 2026 Martial Systems LLC

import gzip
from datetime import date, timedelta
from pathlib import Path

import pytest

from snowfreq.errors import FetchError
from snowfreq.fetch import fetch_live
from snowfreq.ghcnd import parse_snow_csv
from snowfreq.labels import snow_mm_to_inches


def test_parse_snow_ignores_tmin_prcp_snwd() -> None:
    text = (
        "USW00014848,20181212,TMIN,0,,,\n"
        "USW00014848,20181212,PRCP,10,,,\n"
        "USW00014848,20181212,SNWD,50,,,\n"
        "USW00014848,20181212,SNOW,25,,,\n"
        "USW00014848,20181212,SNOW,-9999,,,\n"
    )
    rows = parse_snow_csv(text)
    assert rows == [(date(2018, 12, 12), snow_mm_to_inches(25))]


def _gz(lines: list[str]) -> bytes:
    return gzip.compress("\n".join(lines).encode("utf-8"))


def _djf_lines(sid: str, winter_id: int, snow_mm: int = 25) -> list[str]:
    start = date(winter_id - 1, 12, 1)
    end = date(winter_id, 2, 29 if winter_id % 4 == 0 else 28)
    out = []
    d = start
    while d <= end:
        ymd = d.strftime("%Y%m%d")
        out.append(f"{sid},{ymd},SNOW,{snow_mm},,,")
        d += timedelta(days=1)
    return out


def test_empty_core_snow_stops(tmp_path: Path) -> None:
    def getter(url: str) -> bytes:
        if url.endswith("ghcnd-stations.txt"):
            return (
                "USW00014848  41.7100  -86.3200  236.0 SOUTH BEND          IN US\n"
                "USW00014827  41.1200  -85.1900  248.0 FORT WAYNE         IN US\n"
                "USW00093819  39.7200  -86.2900  241.0 INDIANAPOLIS       IN US\n"
                "USW00093817  38.0400  -87.5300  118.0 EVANSVILLE         IN US\n"
            ).encode()
        if "USW00014848" in url:
            return _gz(["USW00014848,20181212,TMIN,0,,,"])
        return _gz(_djf_lines("USW00014827", 2019))

    with pytest.raises(FetchError, match="required core USW00014848"):
        fetch_live(cache_dir=tmp_path, getter=getter)
