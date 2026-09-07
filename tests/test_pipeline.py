# Copyright (c) 2026 Martial Systems LLC

from pathlib import Path

from snowfreq.config import CORE_IDS, MIN_TRAIN_WINTERS, QUESTION
from snowfreq.errors import FigureCapError
from snowfreq.figure import _cap
from snowfreq.pipeline import stage0_fixture


def test_fixture_two_figures(tmp_path: Path) -> None:
    report = stage0_fixture(tmp_path)
    assert report["question"] == QUESTION
    assert report["figures"] == ["series.png", "brier_bars.png"]
    assert (tmp_path / "series.png").is_file()
    assert (tmp_path / "brier_bars.png").is_file()
    assert report["p_sfha_feature"] is False
    assert report["nwm_file"] is False
    assert report["prcp_as_label"] is False
    assert report["first_snow_as_label"] is False
    assert report["inches_sen_as_product"] is False
    assert report["page_in_scope"] is False
    assert report["element"] == "SNOW"
    assert report["season"] == "DJF"
    assert report["estimator"] == "sen"
    assert report["holdout"]["n"] == 24
    assert report["slope_beats_rate_brier"] is True
    assert report["confirm_in_train"] is False
    assert report["confirm_in_slope"] is False
    assert report["confirm_in_rate"] is False
    assert set(report["by_station"]) == set(CORE_IDS)
    assert "USW00004846" not in report["by_station"]
    assert "USC00125604" not in report["by_station"]
    for sid in CORE_IDS:
        assert report["by_station"][sid]["train_n"] >= MIN_TRAIN_WINTERS
    assert report["holdout_winters"] == [2020, 2021, 2022, 2023, 2024, 2025]


def test_live_holdout_keeps_page_closed() -> None:
    import json

    path = Path(__file__).resolve().parents[1] / "logs" / "in_live" / "stage_c_report.json"
    live = json.loads(path.read_text(encoding="utf-8"))
    assert live["page_in_scope"] is False
    assert live["element"] == "SNOW"
    assert live["season"] == "DJF"
    assert live["belt_in_core_mean"] is False
    assert live["refit_normal"] is False
    assert live["slope_beats_rate_brier"] is False
    assert live["slope_beats_rate_mae"] is False
    assert live["brier_mae_agree"] is True
    assert live["holdout"]["n"] == 24
    assert abs(live["holdout"]["slope"]["brier"] - live["holdout"]["rate"]["brier"]) < 1e-12
    assert live["by_station"]["USW00014848"]["sen_slope_per_decade"] == 0.0
    assert live["by_station"]["USW00014848"]["holdout_above"] == "0/6"
    assert "USW00004846" not in live["by_station"]
    assert "USC00125604" not in live["by_station"]
    assert live["confirm_in_rate"] is False
    assert live["normals"]["USW00014848"] == 51.4
    assert live["common_start"] == 1949


def test_bar_labels_are_city_names_and_do_not_overlap() -> None:
    import json

    from snowfreq.config import CORE_STATIONS, LIVE_BARS_SUBTITLE
    from snowfreq.figure import bar_station_labels, draw_bars

    live = Path(__file__).resolve().parents[1] / "logs" / "in_live" / "stage_c_report.json"
    fit = json.loads(live.read_text(encoding="utf-8"))
    order, labels = bar_station_labels(fit["by_station"])
    cities = [name for sid, name in CORE_STATIONS if sid in order]
    assert labels == cities
    assert labels == ["South Bend", "Fort Wayne", "Indianapolis", "Evansville"]
    fig = draw_bars(fit, title="Holdout Brier", subtitle=LIVE_BARS_SUBTITLE)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for ax in fig.axes:
        boxes = [t.get_window_extent(renderer=renderer) for t in ax.get_xticklabels()]
        assert len(boxes) == 4
        for left, right in zip(boxes, boxes[1:]):
            assert not left.overlaps(right), (left, right)
    import matplotlib.pyplot as plt

    plt.close(fig)


def test_series_four_panels_are_separate_and_not_cropped() -> None:
    import json

    import numpy as np

    from snowfreq.config import CORE_STATIONS, LIVE_SERIES_SUBTITLE
    from snowfreq.figure import draw_series

    live = Path(__file__).resolve().parents[1] / "logs" / "in_live" / "stage_c_report.json"
    fit = json.loads(live.read_text(encoding="utf-8"))
    fig = draw_series(fit, title="DJF above-normal winters", subtitle=LIVE_SERIES_SUBTITLE)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    axes = list(fig.axes)
    assert len(axes) == 4
    titles = [ax.get_title() for ax in axes]
    assert titles == [city for _, city in CORE_STATIONS]
    w, h = fig.get_size_inches()
    assert w >= 11.0
    assert h >= 9.5
    title = fig._suptitle
    assert title is not None
    title_box = title.get_window_extent(renderer)
    legends = [c for c in fig.legends]
    assert legends
    legend_box = legends[0].get_window_extent(renderer)
    assert not title_box.overlaps(legend_box)
    for ax in axes:
        ax_box = ax.get_window_extent(renderer)
        assert ax_box.width >= 280
        assert ax_box.height >= 220
        assert not title_box.overlaps(ax_box)
        assert not legend_box.overlaps(ax_box)
        assert len(ax.patches) >= 20
        assert ax.get_xlabel() == "winter-end year"
        assert ax.get_ylabel() == "above-normal"
    sb = axes[0]
    hold0 = [
        r for r in fit["holdout_rows"] if r["station_id"] == "USW00014848" and int(r["above"]) == 0
    ]
    assert len(hold0) == 6
    y0 = np.concatenate([c.get_offsets()[:, 1] for c in sb.collections]) if sb.collections else np.array([])
    assert y0.size >= 6
    assert np.all(np.abs(y0) < 1e-9)
    texts = " ".join(t.get_text() for t in fig.legends[0].get_texts())
    assert "Sen = train rate (0.000 / decade)" in texts
    assert texts.count("train rate") == 1
    import matplotlib.pyplot as plt

    plt.close(fig)


def test_third_figure_refused() -> None:
    try:
        _cap(3)
        raise AssertionError("cap allowed 3")
    except FigureCapError:
        pass
