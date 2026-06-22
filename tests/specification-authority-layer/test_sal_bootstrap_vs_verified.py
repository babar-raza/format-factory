"""
test_sal_bootstrap_vs_verified.py — Bootstrap vs Verified Fact Distinction Tests

TC-SAL-HEAL-001: Verifies that sal_master_runner distinguishes template (bootstrap_only)
facts from workbench-verified facts via fact_status and source_id fields.

Four tests:
1. Format with no workbench → all facts have fact_status == "bootstrap_only"
2. Format with workbench (ZST) → workbench facts have fact_status="verified" and source_id non-null
3. fact_status="verified" cannot be emitted with source_id=None (invariant check)
4. Per-format output files are written for each processed format

Gap: GAP-SA-001 (Master runner bootstrap separation)
Sprint: spec-auth-heal-sprint-1
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "specification-authority-layer"))

from sal_master_runner import run_sal_pipeline


class TestBootstrapVsVerified:
    """Verify fact_status / source_id distinction between template and workbench facts."""

    def test_no_workbench_format_facts_are_bootstrap_only(self, tmp_path):
        """A format with no spec-cache workbench → all emitted facts are bootstrap_only."""
        # ORA has no spec-cache workbench directory; only template facts are emitted.
        # CSV was previously used here but its structural workbench has verified_with_note
        # facts (FACT-CSV-001, FACT-CSV-002) which are included as `verified`.
        result = run_sal_pipeline(formats=["ora"], output_dir=tmp_path)
        assert result["formats_processed"] == 1
        fmts = result.get("results", [])
        ora_result = next((r for r in fmts if r["format_id"] == "ora"), None)
        assert ora_result is not None, "ORA must be in results"
        facts = ora_result["spec_facts"]
        assert len(facts) > 0, "ORA should have at least template facts"
        for f in facts:
            assert f.get("fact_status") == "bootstrap_only", (
                f"ORA template fact must have fact_status='bootstrap_only', got: "
                f"{f.get('fact_status')} for qname={f.get('qname')}"
            )

    def test_workbench_format_verified_facts_have_source_id(self, tmp_path):
        """ZST (has verified workbench) → workbench facts have fact_status='verified' and source_id."""
        result = run_sal_pipeline(formats=["zst"], output_dir=tmp_path)
        zst_result = next(
            (r for r in result.get("results", []) if r["format_id"] == "zst"), None
        )
        assert zst_result is not None, "ZST must be in results"
        facts = zst_result["spec_facts"]
        workbench_facts = [f for f in facts if f.get("fact_status") == "verified"]
        assert len(workbench_facts) >= 15, (
            f"ZST should have >= 15 verified workbench facts, got {len(workbench_facts)}"
        )
        for f in workbench_facts:
            assert f.get("source_id") is not None, (
                f"Verified fact must have non-null source_id, "
                f"got None for qname={f.get('qname')}"
            )

    def test_verified_fact_status_requires_non_null_source_id(self, tmp_path):
        """Invariant: no fact may have fact_status='verified' with source_id=None."""
        result = run_sal_pipeline(formats=["fods", "zst"], output_dir=tmp_path)
        violations = []
        for entry in result.get("results", []):
            for f in entry["spec_facts"]:
                if f.get("fact_status") == "verified" and f.get("source_id") is None:
                    violations.append(
                        f"{entry['format_id']}:{f.get('qname')} "
                        f"(fact_status=verified, source_id=None)"
                    )
        assert not violations, (
            f"Invariant violated — verified facts with null source_id: {violations[:5]}"
        )

    def test_per_format_output_files_written(self, tmp_path):
        """Per-format sal-facts-<format>.json files must be written for each processed format."""
        run_sal_pipeline(formats=["fods", "zst"], output_dir=tmp_path)
        assert (tmp_path / "sal-facts-fods.json").is_file(), "sal-facts-fods.json not written"
        assert (tmp_path / "sal-facts-zst.json").is_file(), "sal-facts-zst.json not written"
        # Verify parseable JSON with spec_facts
        d = json.loads((tmp_path / "sal-facts-fods.json").read_text(encoding="utf-8"))
        assert "spec_facts" in d, "sal-facts-fods.json missing spec_facts key"
        assert len(d["spec_facts"]) > 0, "sal-facts-fods.json has empty spec_facts"
        d2 = json.loads((tmp_path / "sal-facts-zst.json").read_text(encoding="utf-8"))
        assert "spec_facts" in d2, "sal-facts-zst.json missing spec_facts key"
        assert len(d2["spec_facts"]) > 0, "sal-facts-zst.json has empty spec_facts"
