# Agent notes: indiana_djf_snow_freq

Public GitHub. MIT. Question: Does a train-era Sen slope of DJF-above-normal winters beat the train-era above-normal rate at held-out Indiana GHCND cores?

The fixture is not the result. DJF SNOW only. Frozen 1991-2020 normals. Four cores. Belt stations stay out. No ENSO, CPC, RadarOnly, first-snow date, or inches Sen as the product. Do not restamp `9aa7935`, `82ce0ce`, `0ace8a1`. Do not paint HAND. Do not touch White River Q or Site hero copy. Precip lane, not Temp.

`snowfreqforge/` is the GraphForge pin. Verify-before-done is the finish gate.

Index: Precip lane on https://gist.github.com/martialsystems/66b896b0a4a0b8cba2b478aef64312f3

## Verify

`python3 ~/agent_laws_verify_before_done/vbd_gate.py check --app-root . --claim-done --not-promoted 'frequency vs season-total already adjacent in the precip lane'`
