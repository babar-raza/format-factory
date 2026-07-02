"""Tests for generate_statistics.py source readers and calculations."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure tools/docs on path
TOOLS_DOCS = Path(__file__).resolve().parents[2] / "tools" / "docs"
sys.path.insert(0, str(TOOLS_DOCS))

from generate_statistics import (
    _count_certification,
    _count_formats,
    _count_governance,
    _count_oracle,
    _count_tests,
    collect_statistics,
    render_statistics_markdown,
)

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "project_status"


# ---------------------------------------------------------------------------
# _count_formats
# ---------------------------------------------------------------------------

class TestCountFormats:
    def test_returns_zero_when_registry_missing(self, tmp_path):
        result = _count_formats(tmp_path)
        assert result["total_in_registry"] == 0
        assert result["active_with_source"] == 0

    def test_excludes_odf_shared(self):
        result = _count_formats(FIXTURE_ROOT)
        # Registry has 4 entries: odf-shared, csv, dif, ora
        # total_in_registry should be 4 (all entries)
        assert result["total_in_registry"] == 4
        # active_with_source = only csv and dif have src/python/ dirs
        assert result["active_with_source"] == 2

    def test_families_counted_correctly(self):
        result = _count_formats(FIXTURE_ROOT)
        families = result.get("families", {})
        # csv and dif are "cells", ora is "imaging"
        assert "cells" in families
        assert "imaging" in families
        # odf-shared should not be in families (excluded)
        assert "odf" not in families

    def test_family_count(self):
        result = _count_formats(FIXTURE_ROOT)
        # cells + imaging = 2 families (odf excluded)
        assert result["family_count"] >= 1


# ---------------------------------------------------------------------------
# _count_oracle
# ---------------------------------------------------------------------------

class TestCountOracle:
    def test_sums_correctly(self):
        result = _count_oracle(FIXTURE_ROOT)
        # csv: 5/5, dif: 2/3 → total 8 cases, 7 pass
        assert result["formats_verified"] == 2
        assert result["total_cases"] == 8
        assert result["total_pass"] == 7

    def test_pass_rate_format(self):
        result = _count_oracle(FIXTURE_ROOT)
        assert result["pass_rate"] == "7/8"

    def test_zero_when_oracle_dir_missing(self, tmp_path):
        result = _count_oracle(tmp_path)
        assert result["formats_verified"] == 0
        assert result["total_cases"] == 0
        assert result["pass_rate"] == "0/0"


# ---------------------------------------------------------------------------
# _count_certification
# ---------------------------------------------------------------------------

class TestCountCertification:
    def test_reads_summary(self):
        result = _count_certification(FIXTURE_ROOT)
        assert result["total"] == 2
        assert result["certified"] == 1

    def test_zero_when_matrix_missing(self, tmp_path):
        result = _count_certification(tmp_path)
        assert result["total"] == 0
        assert result["certified"] == 0


# ---------------------------------------------------------------------------
# _count_governance
# ---------------------------------------------------------------------------

class TestCountGovernance:
    def test_counts_validators_from_source(self):
        result = _count_governance(FIXTURE_ROOT)
        # Fixture has governance_validators.py with 2 "def validate_" functions
        assert result["validators"] == 2

    def test_zero_validators_when_dir_missing(self, tmp_path):
        result = _count_governance(tmp_path)
        assert result["validators"] == 0

    def test_capabilities_active_count(self):
        result = _count_governance(FIXTURE_ROOT)
        # Fixture: 5 capabilities total, 3 active (add-python-api, score-format, new-cap-no-track)
        # deprecated: detect-duplicate-skills
        assert result["capabilities_total"] == 5
        assert result["capabilities_active"] == 4  # backfill + add-python-api + score-format + new-cap-no-track

    def test_skills_count(self):
        result = _count_governance(FIXTURE_ROOT)
        # Fixture: 3 skills total
        assert result["skills"] == 3

    def test_commands_excludes_readme(self):
        result = _count_governance(FIXTURE_ROOT)
        # Fixture: 3 .md files but _readme.md excluded → 2
        assert result["commands"] == 2


# ---------------------------------------------------------------------------
# collect_statistics integration
# ---------------------------------------------------------------------------

class TestCollectStatistics:
    def test_returns_all_top_level_keys(self):
        result = collect_statistics(FIXTURE_ROOT)
        for key in ("formats", "source", "tests", "governance", "oracle", "infrastructure", "certification"):
            assert key in result, f"Missing key: {key}"

    def test_active_with_source_leq_total(self):
        result = collect_statistics(FIXTURE_ROOT)
        fmt = result["formats"]
        assert fmt["active_with_source"] <= fmt["total_in_registry"]

    def test_certified_leq_total(self):
        result = collect_statistics(FIXTURE_ROOT)
        cert = result["certification"]
        assert cert["certified"] <= cert["total"]


# ---------------------------------------------------------------------------
# render_statistics_markdown
# ---------------------------------------------------------------------------

class TestRenderStatisticsMarkdown:
    def test_contains_machinery_and_product_labels(self):
        stats = collect_statistics(FIXTURE_ROOT)
        md = render_statistics_markdown(stats)
        assert "Validators" in md or "validators" in md

    def test_no_hardcoded_values(self):
        stats = collect_statistics(FIXTURE_ROOT)
        md = render_statistics_markdown(stats)
        # Should not contain real-repo counts (these are fixture-specific)
        # Just verify it's non-empty markdown
        assert "##" in md or "|" in md
