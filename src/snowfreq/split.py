# Copyright (c) 2026 Martial Systems LLC
"""Temporal winter split. Confirmation is out of train, the slope, and the rate."""

from __future__ import annotations

from snowfreq.config import (
    CONFIRM_WINTER,
    HOLDOUT_FIRST_WINTER,
    HOLDOUT_LAST_WINTER,
    TRAIN_LAST_WINTER,
)
from snowfreq.errors import SplitError

TRAIN = "train"
HOLDOUT = "holdout"
CONFIRM = "confirm"
OTHER = "other"


def role(winter_id: int) -> str:
    y = int(winter_id)
    if y <= TRAIN_LAST_WINTER:
        return TRAIN
    if HOLDOUT_FIRST_WINTER <= y <= HOLDOUT_LAST_WINTER:
        return HOLDOUT
    if y == CONFIRM_WINTER:
        return CONFIRM
    return OTHER


def assert_split(
    *,
    confirm_in_train: bool,
    confirm_in_slope: bool,
    confirm_in_rate: bool,
    random_split: bool,
) -> None:
    if confirm_in_train or confirm_in_slope or confirm_in_rate:
        raise SplitError("confirmation leaked into train, the slope, or the rate")
    if random_split:
        raise SplitError("random row split is refused")
