# Copyright (c) 2026 Martial Systems LLC
"""Theil-Sen slope. OLS is a footnote only."""

from __future__ import annotations

import numpy as np


def sen_slope(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size != y.size or x.size < 2:
        raise ValueError("Sen slope needs at least two paired points")
    slopes: list[np.ndarray] = []
    for i in range(x.size - 1):
        dx = x[i + 1 :] - x[i]
        dy = y[i + 1 :] - y[i]
        ok = dx != 0
        if np.any(ok):
            slopes.append(dy[ok] / dx[ok])
    if not slopes:
        raise ValueError("Sen slope has no pairwise year gaps")
    return float(np.median(np.concatenate(slopes)))


def ols_slope(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size != y.size or x.size < 2:
        raise ValueError("OLS slope needs at least two paired points")
    if float(np.std(x)) == 0.0:
        return 0.0
    coef = np.polyfit(x, y, 1)
    return float(coef[0])


def clip01(p: float) -> float:
    return float(min(1.0, max(0.0, p)))
