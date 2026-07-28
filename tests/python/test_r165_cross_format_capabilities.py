"""
test_r165_cross_format_capabilities.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT31-001
Added: 2026-06-10

Cross-format smoke test validating that all get_capabilities() functions
return a consistent Gate 5 neutral-model structure.

Formats with get_capabilities(): PBM, PGM, PPM, XCF, DIF, SYLK, ODS, CSV
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from pbm.pbm_parser import get_capabilities as pbm_caps
from pgm.pgm_parser import get_capabilities as pgm_caps
from ppm.ppm_parser import get_capabilities as ppm_caps
from xcf.xcf_parser import get_capabilities as xcf_caps
from dif.dif_parser import get_capabilities as dif_caps
from sylk.sylk_parser import get_capabilities as sylk_caps
from ods.ods_parser import get_capabilities as ods_caps
from src.python.ff_csv import get_capabilities as csv_caps


ALL_CAPS = [
    ("pbm", pbm_caps),
    ("pgm", pgm_caps),
    ("ppm", ppm_caps),
    ("xcf", xcf_caps),
    ("dif", dif_caps),
    ("sylk", sylk_caps),
    ("ods", ods_caps),
    ("csv", csv_caps),
]


class TestCrossFormatCapabilities:
    """All get_capabilities() functions should return a consistent dict."""

    @pytest.mark.parametrize("fmt,caps_fn", ALL_CAPS, ids=[f[0] for f in ALL_CAPS])
    def test_returns_dict(self, fmt, caps_fn):
        result = caps_fn()
        assert isinstance(result, dict)

    @pytest.mark.parametrize("fmt,caps_fn", ALL_CAPS, ids=[f[0] for f in ALL_CAPS])
    def test_has_format_key(self, fmt, caps_fn):
        result = caps_fn()
        assert "format" in result
        assert result["format"] == fmt

    @pytest.mark.parametrize("fmt,caps_fn", ALL_CAPS, ids=[f[0] for f in ALL_CAPS])
    def test_has_gate_number(self, fmt, caps_fn):
        result = caps_fn()
        assert "gate" in result
        assert isinstance(result["gate"], int)
        assert result["gate"] >= 1

    @pytest.mark.parametrize("fmt,caps_fn", ALL_CAPS, ids=[f[0] for f in ALL_CAPS])
    def test_has_supported_list(self, fmt, caps_fn):
        result = caps_fn()
        assert "supported" in result
        assert isinstance(result["supported"], list)

    @pytest.mark.parametrize("fmt,caps_fn", ALL_CAPS, ids=[f[0] for f in ALL_CAPS])
    def test_has_unsupported_list(self, fmt, caps_fn):
        result = caps_fn()
        assert "unsupported" in result
        assert isinstance(result["unsupported"], list)

    @pytest.mark.parametrize("fmt,caps_fn", ALL_CAPS, ids=[f[0] for f in ALL_CAPS])
    def test_commercial_not_ready(self, fmt, caps_fn):
        result = caps_fn()
        assert "commercial_product_ready" in result
        assert result["commercial_product_ready"] is False

    @pytest.mark.parametrize("fmt,caps_fn", ALL_CAPS, ids=[f[0] for f in ALL_CAPS])
    def test_supported_is_sorted(self, fmt, caps_fn):
        result = caps_fn()
        assert result["supported"] == sorted(result["supported"])

    @pytest.mark.parametrize("fmt,caps_fn", ALL_CAPS, ids=[f[0] for f in ALL_CAPS])
    def test_no_overlap(self, fmt, caps_fn):
        result = caps_fn()
        supported = set(result["supported"])
        unsupported = set(result["unsupported"])
        assert supported.isdisjoint(unsupported), f"Overlap in {fmt}: {supported & unsupported}"
