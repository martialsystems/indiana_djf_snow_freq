# Methodology: DJF above-normal frequency vs a flat rate

Question: Does a train-era Sen slope of DJF-above-normal winters beat the train-era above-normal rate at held-out Indiana GHCND cores?

## Label

GHCND `SNOW` summed 1 Dec through 28/29 Feb, inches. A station-winter is 1 if that total is greater than the frozen 1991-2020 DJF snowfall normal at that station, else 0. The normal is the parent lock from `indiana_djf_snow_tercile` `9aa7935` / `indiana_wx_pages` (South Bend 51.4, Fort Wayne 26.2, Indianapolis 21.2, Evansville 9.3). Do not refit it from live GHCND.

A DJF is complete only if Dec, Jan, and Feb each have numeric SNOW on at least 80% of that month's days. Missing SNOW is a drop. Empty SNOW for a required core stops.

## Stations

Required cores: South Bend `USW00014848`, Fort Wayne `USW00014827`, Indianapolis `USW00093819`, Evansville `USW00093817`.

Valparaiso `USW00004846`, Michigan City `USC00125604`, LaPorte `USC00124837`, and Indiana Dunes `USC00124244` stay out. Belt inches stay at `82ce0ce`.

## Bars

Bar A: train-era above-normal rate at that station, on the common window through DJF 2018-19. Constant probability. The four-core mean rate is a table row, not the method.

Bar B: last winter's 0/1 at that station.

Treatment: Theil-Sen slope of the 0/1 series versus winter-end year, fit on train winters only. Predicted holdout probability is clip(train_rate + slope * (year - train_anchor), 0, 1). Train-anchor is the mean of the integer years from the common start through 2019. Same anchor for all reported numbers. OLS linear-probability slope is a footnote only.

## Split

Rows: station × DJF winter. Winter-end year is the January/February year (DJF 2018-19 is 2019).

Train: through DJF 2018-19. Holdout: DJF 2019-20 through 2024-25. Confirmation: DJF 2025-26, out of train, out of the slope, and out of the rate.

History for the slope: complete DJF winters from the first year each core meets the floor through 2018-19. Common start year is the latest of the four first-complete DJF winters. If that common window has fewer than 40 train winters per core, stop and report the starts.

## Metrics

Lead with holdout Brier on the 0/1 label. MAE second. Sen slope is also reported as probability per decade. Counts of winters the slope gets the sign right are not the method. A holdout that is 2/6 or 4/6 at one station is a small-n row, not a regional trend.

## Figures

1. Four-core train and holdout 0/1 series versus winter-end year, with the frozen normal as the classifier.
2. Holdout Brier bars: Sen slope vs train rate vs last winter.

## Parents

Cite DJF snow `9aa7935`, NWI lake snow `82ce0ce`, first snow date `0ace8a1`. Do not restamp them. Live skill is `6de7758` from `logs/in_live/stage_c_report.json`. Sen does not beat the train-era rate on holdout Brier. Pages stay off.
