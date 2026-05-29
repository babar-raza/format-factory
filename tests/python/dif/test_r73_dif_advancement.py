"""
test_r73_dif_advancement.py — R73 Train G: DIF format track advancement.

Deepens DIF coverage: probe_dif API fields, dict-API consistency,
and stats API on corpus samples.

Sprint: FORMAT-FACTORY-R73-DELIVERY-PACKAGE-TRUTH-PRODUCT-ADVANCEMENT-GATE-READINESS-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
_src = PROJECT_ROOT / "src" / "python"
sys.path.insert(0, str(_src))

from dif.dif_parser import parse_dif, parse_dif_strict, probe_dif, get_capabilities, DifError
from dif.dif_stats import dif_stats, dif_numeric_range, dif_empty_row_count

VALID = PROJECT_ROOT / "samples" / "by-format" / "dif" / "valid"


def _first_valid() -> Path | None:
    if not VALID.exists():
        return None
    samples = list(VALID.glob("*.dif"))
    return samples[0] if samples else None


class TestDifProbeApi:
    """R73-DIF-001: probe_dif return shape."""

    def test_probe_missing_file_exists_false(self, tmp_path):
        result = probe_dif(str(tmp_path / "no.dif"))
        assert result.get("exists") is False

    def test_probe_valid_file_exists_true(self):
        f = _first_valid()
        if f is None:
            pytest.skip("No DIF corpus samples")
        result = probe_dif(str(f))
        assert result.get("exists") is True


class TestDifDictApiConsistency:
    """R73-DIF-002: dict API consistency with strict API."""

    def test_dict_api_ok_true_for_valid(self):
        f = _first_valid()
        if f is None:
            pytest.skip("No DIF corpus samples")
        result = parse_dif(str(f))
        assert result["ok"] is True

    def test_dict_api_ok_false_for_missing(self, tmp_path):
        result = parse_dif(str(tmp_path / "ghost.dif"))
        assert result["ok"] is False

    def test_dict_row_count_matches_strict(self):
        f = _first_valid()
        if f is None:
            pytest.skip("No DIF corpus samples")
        dict_result = parse_dif(str(f))
        strict_doc = parse_dif_strict(str(f))
        assert dict_result["row_count"] == len(strict_doc.rows)


class TestDifStatsApi:
    """R73-DIF-003: stats API on corpus samples."""

    def test_dif_stats_on_valid(self):
        f = _first_valid()
        if f is None:
            pytest.skip("No DIF corpus samples")
        doc = parse_dif(str(f))
        stats = dif_stats(doc)
        assert isinstance(stats, dict)
        assert "row_count" in stats or "rows" in stats or len(stats) > 0

    def test_dif_numeric_range_on_empty(self):
        result = dif_numeric_range({"rows": []})
        assert isinstance(result, dict)

    def test_dif_empty_row_count_on_empty(self):
        result = dif_empty_row_count({"rows": []})
        assert result == 0


class TestDifCapabilities:
    """R73-DIF-004: capabilities API."""

    def test_format_is_dif(self):
        caps = get_capabilities()
        assert caps["format"] == "dif"

    def test_commercial_ready_false(self):
        caps = get_capabilities()
        assert caps["commercial_product_ready"] is False
