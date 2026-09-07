# Copyright (c) 2026 Martial Systems LLC
"""Station-winter DJF totals and 0/1 above-normal labels."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class WinterPack:
    station_id: np.ndarray
    name: np.ndarray
    lat: np.ndarray
    lon: np.ndarray
    winter_id: np.ndarray
    snow_in: np.ndarray
    snow_normal_in: np.ndarray
    above: np.ndarray
    complete_frac: np.ndarray
    source: str = "fixture"
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def n_rows(self) -> int:
        return int(self.station_id.shape[0])

    @property
    def n_stations(self) -> int:
        return int(np.unique(self.station_id).shape[0])
