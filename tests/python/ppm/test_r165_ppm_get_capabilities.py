"""
test_r165_ppm_get_capabilities.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT30-001
Added: 2026-06-10

Tests for PPM get_capabilities function (Gate 5 neutral model).
Authority: P4 (SAL-PPM-00001, SAL-PPM-00002)
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import get_capabilities


class TestGetCapabilities:

    def test_returns_dict(self):
        result = get_capabilities()
        assert isinstance(result, dict)

    def test_format_is_ppm(self):
        assert get_capabilities()["format"] == "ppm"

    def test_gate_number(self):
        assert get_capabilities()["gate"] == 5

    def test_commercial_not_ready(self):
        assert get_capabilities()["commercial_product_ready"] is False

    def test_has_supported_list(self):
        result = get_capabilities()
        assert isinstance(result["supported"], list)
        assert len(result["supported"]) > 0

    def test_has_unsupported_list(self):
        result = get_capabilities()
        assert isinstance(result["unsupported"], list)

    def test_supported_sorted(self):
        result = get_capabilities()
        assert result["supported"] == sorted(result["supported"])

    def test_unsupported_sorted(self):
        result = get_capabilities()
        assert result["unsupported"] == sorted(result["unsupported"])
