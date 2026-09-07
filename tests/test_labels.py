# Copyright (c) 2026 Martial Systems LLC

from datetime import date, timedelta

from snowfreq.labels import above_normal, assemble_djf, snow_mm_to_inches, winter_id_of


def test_above_normal_is_strict() -> None:
    assert above_normal(21.3, 21.2) == 1
    assert above_normal(21.2, 21.2) == 0
    assert above_normal(21.1, 21.2) == 0


def test_december_belongs_to_next_winter() -> None:
    assert winter_id_of(date(2018, 12, 1)) == 2019
    assert winter_id_of(date(2019, 1, 1)) == 2019
    assert winter_id_of(date(2019, 2, 28)) == 2019


def test_missing_february_is_incomplete() -> None:
    days = []
    d = date(2018, 12, 1)
    while d <= date(2019, 1, 31):
        days.append((d, 0.4))
        d += timedelta(days=1)
    out = assemble_djf(days, floor=0.80)
    rec = out[2019]
    assert rec["complete"] == 0.0
    assert rec["frac_feb"] == 0.0


def test_complete_djf_sums_inches() -> None:
    days = []
    d = date(2018, 12, 1)
    while d <= date(2019, 2, 28):
        inches = 1.0 if d == date(2018, 12, 15) else 0.0
        days.append((d, inches))
        d += timedelta(days=1)
    rec = assemble_djf(days, floor=0.80)[2019]
    assert rec["complete"] == 1.0
    assert abs(rec["snow_in"] - 1.0) < 1e-9


def test_tenth_inch_from_mm() -> None:
    assert abs(snow_mm_to_inches(25.4) - 1.0) < 1e-9
