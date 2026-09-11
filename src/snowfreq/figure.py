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


def _sen_is_flat(by_st: dict[str, Any]) -> bool:
    slopes = [abs(float((by_st.get(sid) or {}).get("sen_slope_per_year") or 0.0)) for sid, _ in CORE_STATIONS]
    return bool(slopes) and max(slopes) < 1e-12


def draw_series(fit: dict[str, Any], *, title: str, subtitle: str):
    """Four station panels. Holdout zeros sit on y = 0. Flat Sen is one line."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    rows = list(fit.get("holdout_rows") or [])
    train = list(fit.get("train_rows") or [])
    by_st = fit["by_station"]
    flat = _sen_is_flat(by_st)
    fig, axes = plt.subplots(2, 2, figsize=(12.0, 10.2), sharex=False, sharey=False)
    years_line = np.arange(int(fit["common_start"]), int(fit.get("train_last") or TRAIN_LAST_WINTER) + 7)
    for ax, (sid, city) in zip(axes.ravel(), CORE_STATIONS):
        st = by_st[sid]
        rate = float(st["train_rate"])
        slope = float(st["sen_slope_per_year"])
        anchor = float(fit["train_anchor"])
        tr = [r for r in train if r["station_id"] == sid]
        hold = [r for r in rows if r["station_id"] == sid]
        ty = np.asarray([int(r["winter_id"]) for r in tr], dtype=float)
        ta = np.asarray([int(r["above"]) for r in tr], dtype=float)
        hy = np.asarray([int(r["winter_id"]) for r in hold], dtype=float)
        ha = np.asarray([int(r["above"]) for r in hold], dtype=float)
        if ty.size:
            ones = ta >= 0.5
            t0 = ~ones
            if np.any(ones):
                ax.bar(ty[ones], ta[ones], width=0.9, color="#94a3b8", linewidth=0, zorder=2)
            if np.any(t0):
                ax.scatter(
                    ty[t0],
                    np.zeros(int(t0.sum())),
                    s=42,
                    c="#94a3b8",
                    marker="o",
                    zorder=5,
                    edgecolors="#475569",
                    linewidths=0.6,
                )
        if hy.size:
            h1 = ha >= 0.5
            h0 = ~h1
            if np.any(h1):
                ax.bar(hy[h1], ha[h1], width=0.9, color="#b45309", linewidth=0, zorder=3)
            if np.any(h0):
                ax.scatter(
                    hy[h0],
                    np.zeros(int(h0.sum())),
                    s=42,
                    c="#b45309",
                    marker="o",
                    zorder=5,
                    edgecolors="#7c2d12",
                    linewidths=0.6,
                )
        if flat:
            ax.axhline(rate, color="#0f172a", lw=1.6, zorder=4)
        else:
            p = [clip01(rate + slope * (float(y) - anchor)) for y in years_line]
            ax.plot(years_line, p, color="#0f172a", lw=1.6, zorder=4)
            ax.axhline(rate, color="#334155", ls="--", lw=1.2, zorder=4)
        ax.set_title(city, fontsize=13, pad=8)
        ax.set_xlabel("winter-end year", fontsize=10)
        ax.set_ylabel("above-normal", fontsize=10)
        ax.set_ylim(-0.08, 1.18)
        ax.set_yticks([0, 1])
        ax.tick_params(labelsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    handles: list = [
        Patch(facecolor="#94a3b8", label="train above-normal"),
        Patch(facecolor="#b45309", label="holdout above-normal"),
        Line2D(
            [0],
            [0],
            marker="o",
            color="#94a3b8",
            markeredgecolor="#475569",
            linestyle="None",
            markersize=7,
            label="train below-normal",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="#b45309",
            markeredgecolor="#7c2d12",
            linestyle="None",
            markersize=7,
            label="holdout below-normal",
        ),
    ]
    if flat:
        handles.append(Line2D([0], [0], color="#0f172a", lw=1.6, label="Sen = train rate (0.000 / decade)"))
    else:
        handles.append(Line2D([0], [0], color="#0f172a", lw=1.6, label="Sen clipped p"))
        handles.append(Line2D([0], [0], color="#334155", lw=1.2, ls="--", label="train rate"))
    fig.legend(
        handles=handles,
        fontsize=8,
        loc="lower center",
        ncol=3,
        frameon=False,
        bbox_to_anchor=(0.5, 0.012),
    )
    fig.suptitle(title, fontsize=14, y=0.975)
    fig.text(0.5, 0.005, subtitle, ha="center", fontsize=9)
    fig.subplots_adjust(left=0.07, right=0.98, top=0.92, bottom=0.12, hspace=0.38, wspace=0.28)
    return fig


def write_series(dest: Path, *, fit: dict[str, Any], title: str, subtitle: str) -> Path:
    require_clean(title, source="fig1_title")
    require_clean(subtitle, source="fig1_sub")
    import matplotlib.pyplot as plt

    fig = draw_series(fit, title=title, subtitle=subtitle)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dest, dpi=140, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    return dest


def live_bars_subtitle(fit: dict[str, Any]) -> str:
    hold = fit.get("holdout") or {}
    sen = float((hold.get("slope") or {}).get("brier") or 0.0)
    rate = float((hold.get("rate") or {}).get("brier") or 0.0)
    last = float((hold.get("last_year") or {}).get("brier") or 0.0)
    return (
        f"Pooled Brier: Sen {sen:.4f} = train rate {rate:.4f} vs last winter {last:.3f}. "
        "Probability error, not a decline story."
    )


def draw_bars(fit: dict[str, Any], *, title: str, subtitle: str):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    by_st = fit["by_station"]
    order, labels = bar_station_labels(by_st)
    hold = fit.get("holdout") or {}

    def _brier_of(block: dict[str, Any] | None) -> float:
        if not block or "brier" not in block or block["brier"] is None:
            return float("nan")
        return float(block["brier"])

    sen_p = _brier_of(hold.get("slope"))
    rate_p = _brier_of(hold.get("rate"))
    last_p = _brier_of(hold.get("last_year"))
    fig, (ax_p, ax_s) = plt.subplots(
        2,
        1,
        figsize=(7.4, 7.0),
        gridspec_kw={"height_ratios": [1.15, 1.0]},
    )
    names = ["Sen slope", "train rate", "last winter"]
    pooled = np.array([sen_p, rate_p, last_p], dtype=float)
    colors = ["#0f172a", "#64748b", "#b45309"]
    plot_vals = np.where(np.isfinite(pooled), pooled, 0.0)
    bars = ax_p.bar(names, plot_vals, color=colors, width=0.62, edgecolor="#0f172a", linewidth=0.3)
    for rect, val in zip(bars, pooled):
        if not np.isfinite(val):
            continue
        ax_p.text(
            rect.get_x() + rect.get_width() / 2,
            val + 0.004,
            f"{val:.4f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    if np.isfinite(sen_p) and np.isfinite(rate_p) and abs(sen_p - rate_p) < 1e-9:
        ax_p.text(
            0.5,
            max(sen_p, rate_p) + 0.022,
            "Sen = rate",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    finite = [v for v in (sen_p, rate_p, last_p) if np.isfinite(v)]
    hero = max([v for v in (sen_p, rate_p) if np.isfinite(v)] or [1e-6])
    ymax = max(finite or [hero]) * 1.28
    if np.isfinite(last_p) and last_p > 1.35 * hero:
        ymax = 1.35 * hero
        ax_p.text(
            2,
            ymax * 0.96,
            f"last {last_p:.3f}",
            ha="center",
            va="top",
            fontsize=8,
            color="#b45309",
        )
    ax_p.set_ylim(0.0, ymax if np.isfinite(ymax) else 1.0)
    ax_p.set_ylabel("Brier")
    ax_p.set_title("Pooled holdout (four cores)", fontsize=10)
    ax_p.tick_params(axis="x", labelsize=9)

    x = np.arange(len(order), dtype=float)
    width = 0.24
    slope = [by_st[sid]["slope"]["brier"] for sid in order]
    rate = [by_st[sid]["rate"]["brier"] for sid in order]
    last = [by_st[sid]["last_year"]["brier"] for sid in order]
    ax_s.bar(x - width, slope, width, color="#0f172a", label="Sen slope")
    ax_s.bar(x, rate, width, color="#64748b", label="train rate")
    ax_s.bar(x + width, last, width, color="#b45309", label="last winter")
    ax_s.set_xticks(x)
    ax_s.set_xticklabels(labels, fontsize=8, rotation=28, ha="right")
    ax_s.set_ylabel("Brier")
    ax_s.set_title("Per station", fontsize=9)
    ax_s.legend(fontsize=7, loc="upper right")
    ax_s.tick_params(axis="x", pad=2)
    fig.suptitle(title, fontsize=11)
    fig.subplots_adjust(bottom=0.16, top=0.90, hspace=0.48)
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
        subtitle=live_bars_subtitle(fit) if live else FIXTURE_BARS_SUBTITLE,
    )
    paths = [series, bars]
    _cap(len(paths))
    return [p.name for p in paths]
