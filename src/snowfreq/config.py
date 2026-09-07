# Copyright (c) 2026 Martial Systems LLC
"""Locked DJF above-normal frequency: train Sen slope vs train rate."""

from __future__ import annotations

from pathlib import Path

QUESTION = (
    "Does a train-era Sen slope of DJF-above-normal winters beat the "
    "train-era above-normal rate at held-out Indiana GHCND cores?"
)
USER_AGENT = "MartialSystemsResearch/indiana_djf_snow_freq"
MAX_FIGURES = 2
SNOW_MM_PER_IN = 25.4
COMPLETE_FRAC = 0.80
MIN_TRAIN_WINTERS = 40

# winter_id is the January/February year: DJF 2018-19 is 2019.
TRAIN_LAST_WINTER = 2019
HOLDOUT_FIRST_WINTER = 2020
HOLDOUT_LAST_WINTER = 2025
CONFIRM_WINTER = 2026
HOLDOUT_WINTERS = tuple(range(HOLDOUT_FIRST_WINTER, HOLDOUT_LAST_WINTER + 1))

CORE_STATIONS = (
    ("USW00014848", "South Bend"),
    ("USW00014827", "Fort Wayne"),
    ("USW00093819", "Indianapolis"),
    ("USW00093817", "Evansville"),
)
CORE_IDS = tuple(s for s, _ in CORE_STATIONS)
BELT_OUT = (
    ("USW00004846", "Valparaiso"),
    ("USC00125604", "Michigan City"),
    ("USC00124837", "LaPorte"),
    ("USC00124244", "Indiana Dunes"),
)
BELT_OUT_IDS = tuple(s for s, _ in BELT_OUT)

GHCND_STATION_URL = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/by_station/{sid}.csv.gz"
GHCND_STATIONS_URL = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"
REPO_ROOT = Path(__file__).resolve().parents[2]
FROZEN_NORMALS_PATH = REPO_ROOT / "data" / "frozen" / "djf_normals.json"

PARENT_DJF = "9aa7935"
PARENT_NWI = "82ce0ce"
PARENT_SNOWDATE = "0ace8a1"

INDEX_GIST = "https://gist.github.com/martialsystems/66b896b0a4a0b8cba2b478aef64312f3"
PRECIP_GIST = "https://gist.github.com/martialsystems/b5f900aad37487bb8c0206a321c1ed5c"

FROZEN_NORMALS_IN = {
    "USW00014848": 51.4,
    "USW00014827": 26.2,
    "USW00093819": 21.2,
    "USW00093817": 9.3,
}

LIVE_SERIES_SUBTITLE = (
    "Above-normal DJF winters (0/1) vs the frozen 1991-2020 normal. "
    "Holdout zeros are marked on y = 0. Sen equals the train rate (0.000 / decade). "
    "Not inches and not a storm."
)
LIVE_BARS_SUBTITLE = (
    "Holdout Brier. Sen slope vs train-era rate vs last winter. "
    "Probability error, not a decline story."
)
FIXTURE_SERIES_SUBTITLE = "Fixture 0/1 winters with a planted slope. Does not rescue live skill."
FIXTURE_BARS_SUBTITLE = "Fixture holdout Brier. Does not rescue live skill."
