# Copyright (c) 2026 Martial Systems LLC


class GateError(RuntimeError):
    """Stage hard gate failed."""


class ClaimBanError(GateError):
    """Report text hit a banned claim."""


class FetchError(GateError):
    """GHCND DJF SNOW empty or thin for a required core, or a refused substitute."""


class SplitError(GateError):
    """Temporal split leaked confirmation into train, the slope, or the rate."""


class FigureCapError(GateError):
    """This tree stops at two figures."""


class CompletenessError(GateError):
    """A kept row fails Dec/Jan/Feb numeric SNOW completeness."""


class NormalError(GateError):
    """Frozen 1991-2020 DJF normal missing or refit from GHCND."""
