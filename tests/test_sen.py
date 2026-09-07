# Copyright (c) 2026 Martial Systems LLC

import numpy as np

from snowfreq.sen import clip01, sen_slope


def test_sen_recovers_unit_slope() -> None:
    x = np.arange(10.0)
    y = 3.0 + 0.5 * x
    assert abs(sen_slope(x, y) - 0.5) < 1e-9


def test_sen_is_robust_to_one_outlier() -> None:
    x = np.arange(11.0)
    y = np.zeros_like(x)
    y[5] = 20.0
    slope = sen_slope(x, y)
    assert abs(slope) < 0.05


def test_clip01() -> None:
    assert clip01(-0.2) == 0.0
    assert clip01(1.4) == 1.0
    assert clip01(0.3) == 0.3
