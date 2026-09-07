# Copyright (c) 2026 Martial Systems LLC

from snowfreq.config import FROZEN_NORMALS_IN
from snowfreq.normals import csv_normal_for, load_frozen_normals


def test_frozen_json_matches_parent_lock() -> None:
    got = load_frozen_normals()
    assert got == FROZEN_NORMALS_IN
    assert set(got) == {"USW00014848", "USW00014827", "USW00093819", "USW00093817"}


def test_frozen_csv_matches_json() -> None:
    got = load_frozen_normals()
    for sid, inches in got.items():
        assert abs(csv_normal_for(sid) - inches) < 1e-9
