# Copyright (c) 2026 Martial Systems LLC

import pytest

from snowfreq.errors import SplitError
from snowfreq.split import CONFIRM, HOLDOUT, TRAIN, assert_split, role


def test_pinned_winters() -> None:
    assert role(2018) == TRAIN
    assert role(2019) == TRAIN
    assert role(2020) == HOLDOUT
    assert role(2025) == HOLDOUT
    assert role(2026) == CONFIRM


def test_confirm_leak_refused() -> None:
    with pytest.raises(SplitError):
        assert_split(confirm_in_train=True, confirm_in_slope=False, confirm_in_rate=False, random_split=False)
    with pytest.raises(SplitError):
        assert_split(confirm_in_train=False, confirm_in_slope=True, confirm_in_rate=False, random_split=False)
    with pytest.raises(SplitError):
        assert_split(confirm_in_train=False, confirm_in_slope=False, confirm_in_rate=True, random_split=False)
