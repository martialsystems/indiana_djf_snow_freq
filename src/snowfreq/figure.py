# Copyright (c) 2026 Martial Systems LLC
"""Two figures: 0/1 series vs year, holdout Brier bars."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from snowfreq.claims import require_clean
from snowfreq.config import (
    CORE_STATIONS,
    FIXTURE_BARS_SUBTITLE,
    FIXTURE_SERIES_SUBTITLE,
    LIVE_BARS_SUBTITLE,
    LIVE_SERIES_SUBTITLE,
    MAX_FIGURES,
    TRAIN_LAST_WINTER,
)
from snowfreq.errors import FigureCapError
from snowfreq.sen import clip01


def bar_station_labels(by_st: dict[str, Any]) -> tuple[list[str], list[str]]:
    order: list[str] = []
    labels: list[str] = []
    for sid, city in CORE_STATIONS:
        if sid in by_st:
            order.append(sid)
            labels.append(city)
    return order, labels


def _cap(n: int) -> None:
    if n > MAX_FIGURES:
        raise FigureCapError(f"this tree stops at {MAX_FIGURES} figures")


def write_series(dest: Path, *, fit: dict[str, Any], title: str, subtitle: str) -> Path:
    require_clean(title, source="fig1_title")
    require_clean(subtitle, source="fig1_sub")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = list(fit.get("holdout_rows") or [])
    train = list(fit.get("train_rows") or [])
    by_st = fit["by_station"]
    fig, axes = plt.subplots(2, 2, figsize=(7.4, 6.2), sharex=True, sharey=True)
    years_line = np.arange(int(fit["common_start"]), int(fit.get("train_last") or TRAIN_LAST_WINTER) + 7)
    for ax, (sid, city) in zip(axes.ravel(), CORE_STATIONS):
        st = by_st[sid]
        rate = float(st["train_rate"])
        slope = float(st["sen_slope_per_year"])
        anchor = float(fit["train_anchor"])
        tr = [r for r in train if r["station_id"] == sid]
        ax.scatter(
            [int(r["winter_id"]) for r in tr],
            [int(r["above"]) for r in tr],
            s=18,
            c="#94a3b8",
            marker=".",
            zorder=2,
            label="train 0/1",
        )
        hold = [r for r in rows if r["station_id"] == sid]
        ax.scatter(
            [int(r["winter_id"]) for r in hold],
            [int(r["above"]) for r in hold],
            s=28,
            c="#b45309",
            marker="o",
            zorder=3,
            label="holdout 0/1",
        )
        p = [clip01(rate + slope * (float(y) - anchor)) for y in years_line]
        ax.plot(years_line, p, color="#0f172a", lw=1.1, label="Sen clipped p")
        ax.axhline(rate, color="#64748b", ls="--", lw=1.0, label="train rate")
        ax.set_title(city, fontsize=10)
        ax.set_ylim(-0.08, 1.08)
        ax.set_yticks([0, 1])
        if sid in {"USW00093817", "USW00093819"}:
            ax.set_xlabel("winter-end year")
        if sid in {"USW00014848", "USW00093819"}:
            ax.set_ylabel("above-normal")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=7, loc="upper center", ncol=3, frameon=False)
    fig.suptitle(title, fontsize=11)
    fig.subplots_adjust(bottom=0.16, top=0.86, hspace=0.28, wspace=0.18)
    fig.text(0.5, 0.04, subtitle, ha="center", fontsize=8)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dest, dpi=130, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    return dest


def draw_bars(fit: dict[str, Any], *, title: str, subtitle: str):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    by_st = fit["by_station"]
    order, labels = bar_station_labels(by_st)
    x = np.arange(len(order), dtype=float)
    width = 0.24
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    slope = [by_st[sid]["slope"]["brier"] for sid in order]
    rate = [by_st[sid]["rate"]["brier"] for sid in order]
    last = [by_st[sid]["last_year"]["brier"] for sid in order]
    ax.bar(x - width, slope, width, color="#0f172a", label="Sen slope")
    ax.bar(x, rate, width, color="#64748b", label="train rate")
    ax.bar(x + width, last, width, color="#b45309", label="last winter")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8, rotation=28, ha="right")
    ax.set_ylabel("Brier")
    ax.legend(fontsize=7, loc="upper right")
    ax.tick_params(axis="x", pad=2)
    fig.suptitle(title, fontsize=11)
    fig.subplots_adjust(bottom=0.28, top=0.86)
    fig.text(0.5, 0.03, subtitle, ha="center", fontsize=8)
    return fig


def write_bars(dest: Path, *, fit: dict[str, Any], title: str, subtitle: str) -> Path:
    require_clean(title, source="fig2_title")
    require_clean(subtitle, source="fig2_sub")
    import matplotlib.pyplot as plt

    fig = draw_bars(fit, title=title, subtitle=subtitle)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dest, dpi=130, bbox_inches="tight", pad_inches=0.22)
    plt.close(fig)
    return dest


def write_two(log_dir: Path, *, fit: dict[str, Any], live: bool) -> list[str]:
    _cap(2)
    log_dir.mkdir(parents=True, exist_ok=True)
    series = write_series(
        log_dir / "series.png",
        fit=fit,
        title="DJF above-normal winters",
        subtitle=LIVE_SERIES_SUBTITLE if live else FIXTURE_SERIES_SUBTITLE,
    )
    bars = write_bars(
        log_dir / "brier_bars.png",
        fit=fit,
        title="Holdout Brier",
        subtitle=LIVE_BARS_SUBTITLE if live else FIXTURE_BARS_SUBTITLE,
    )
    paths = [series, bars]
    _cap(len(paths))
    return [p.name for p in paths]
