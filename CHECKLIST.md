# Operator checklist

1. Stage 0 fixture green before live GHCND DJF SNOW. Fixture does not rescue live.
2. GHCND SNOW fetch-or-stop on the four cores. PRCP, SNWD, and first-snow date cannot substitute.
3. Frozen 1991-2020 DJF normals from `9aa7935` / `indiana_wx_pages`. Do not refit.
4. Valparaiso, Michigan City, LaPorte, and Indiana Dunes stay out.
5. Train through DJF 2018-19. Holdout 2019-20 through 2024-25. Confirmation 2025-26 out of the slope and the rate.
6. Lead with holdout Brier vs the train-era rate. Per-station table. Sen slope is probability per decade, not a pour.
7. Two figures. Pages stay off unless Sen beats the train rate on holdout Brier and the README states that yes.
8. Do not restamp DJF snow, NWI lake snow, or first snow date. Do not edit White River Q or Site hero copy.
9. Research index: https://gist.github.com/martialsystems/66b896b0a4a0b8cba2b478aef64312f3 (Precip lane)
