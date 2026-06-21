"""Dogfood: Export FODS + FODT SAL fact analytics to NDJSON.

Pipeline: Load SAL facts -> compute analytics -> write NDJSON -> read back -> verify.
Proves: SAL fact data can be exported and consumed via Format Factory NDJSON codec.
Sprint: PLAN-HARDENING-EXECUTION-20260616
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import write_ndjson, load_ndjson


def _load_fods_facts() -> list[dict]:
    """Load FODS verified facts from spec-cache."""
    try:
        import yaml
    except ImportError:
        pytest.skip("PyYAML not available")
    path = _REPO / ".local" / "spec-cache" / "fods" / "1.3" / "workbench" / "verified-facts-review.yaml"
    if not path.exists():
        pytest.skip("FODS facts not available")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data.get("facts", [])


def _load_fodt_facts() -> list[dict]:
    """Load FODT verified facts from spec-cache."""
    try:
        import yaml
    except ImportError:
        pytest.skip("PyYAML not available")
    path = _REPO / ".local" / "spec-cache" / "fodt" / "odf-1.3" / "workbench" / "verified-facts-review.yaml"
    if not path.exists():
        pytest.skip("FODT facts not available")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data.get("facts", [])


class TestFodsSalFactNdjsonExport:
    """Export FODS SAL facts to NDJSON and verify."""

    def test_fods_facts_export_roundtrip(self, tmp_path):
        facts = _load_fods_facts()
        assert len(facts) >= 15, f"Expected >= 15 facts, got {len(facts)}"
        records = [
            {
                "claim_id": f.get("claim_id", ""),
                "claim": f.get("claim", ""),
                "section_id": f.get("provenance", {}).get("section_id", ""),
                "confidence": f.get("provenance", {}).get("confidence", ""),
                "format": "fods",
            }
            for f in facts
        ]
        out = tmp_path / "fods-facts.ndjson"
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == len(facts)

    def test_fods_fact_ids_unique(self):
        facts = _load_fods_facts()
        ids = [f.get("claim_id") for f in facts]
        assert len(ids) == len(set(ids)), "Duplicate claim_ids found"

    def test_fods_all_facts_have_provenance(self):
        facts = _load_fods_facts()
        for f in facts:
            assert "provenance" in f, f"Missing provenance in {f.get('claim_id')}"
            assert f["provenance"].get("format_id") == "fods"

    def test_fods_fact_count_exceeds_target(self):
        facts = _load_fods_facts()
        assert len(facts) >= 30, f"Target: 30+ facts, got {len(facts)}"


class TestFodtSalFactNdjsonExport:
    """Export FODT SAL facts to NDJSON and verify."""

    def test_fodt_facts_export_roundtrip(self, tmp_path):
        facts = _load_fodt_facts()
        assert len(facts) >= 15, f"Expected >= 15 facts, got {len(facts)}"
        records = [
            {
                "claim_id": f.get("claim_id", ""),
                "claim": f.get("claim", ""),
                "section_id": f.get("provenance", {}).get("section_id", ""),
                "confidence": f.get("provenance", {}).get("confidence", ""),
                "format": "fodt",
            }
            for f in facts
        ]
        out = tmp_path / "fodt-facts.ndjson"
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == len(facts)

    def test_fodt_fact_ids_unique(self):
        facts = _load_fodt_facts()
        ids = [f.get("claim_id") for f in facts]
        assert len(ids) == len(set(ids)), "Duplicate claim_ids found"

    def test_fodt_fact_count_exceeds_target(self):
        facts = _load_fodt_facts()
        assert len(facts) >= 25, f"Target: 25+ facts, got {len(facts)}"


class TestCrossFormatFactAnalytics:
    """Cross-format analytics on SAL facts."""

    def test_combined_fact_count(self):
        fods = _load_fods_facts()
        fodt = _load_fodt_facts()
        total = len(fods) + len(fodt)
        assert total >= 55, f"Combined target: 55+, got {total}"

    def test_combined_export_to_single_ndjson(self, tmp_path):
        fods = _load_fods_facts()
        fodt = _load_fodt_facts()
        records = []
        for f in fods:
            records.append({"claim_id": f["claim_id"], "format": "fods"})
        for f in fodt:
            records.append({"claim_id": f["claim_id"], "format": "fodt"})
        out = tmp_path / "combined-facts.ndjson"
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        fods_loaded = [r for r in loaded if r["format"] == "fods"]
        fodt_loaded = [r for r in loaded if r["format"] == "fodt"]
        assert len(fods_loaded) == len(fods)
        assert len(fodt_loaded) == len(fodt)
