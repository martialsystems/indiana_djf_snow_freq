# Copyright (c) 2026 Martial Systems LLC

import pytest

from snowfreq.claims import require_clean, scan_text
from snowfreq.config import QUESTION
from snowfreq.errors import ClaimBanError


def test_allowed_and_banned() -> None:
    assert scan_text(QUESTION) == []
    assert scan_text("slope, Brier, above-normal, frozen normal") == []
    assert "climate_change" in scan_text("driven by climate change")
    assert "getting_less_snow" in scan_text("Indiana is getting less snow")
    assert "will_get_inches" in scan_text("will get 12 inches")
    assert "frost_warning" in scan_text("a frost warning is in effect")
    assert "flood_warning" in scan_text("flood warning tonight")
    assert "p_sfha" in scan_text("p_sfha as a snow date")
    with pytest.raises(ClaimBanError):
        require_clean("getting less snow every decade", source="t")
