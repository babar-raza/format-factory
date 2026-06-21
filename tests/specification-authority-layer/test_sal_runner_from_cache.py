"""Integration test: sal_master_runner.py from_cache_only=True produces real workbench facts.

TC-SAL-IMPL-001 evidence: verifies the from_cache path emits real FACT-<FORMAT>-* IDs
and does NOT emit template namespace IDs (ODF-FACT-*, FODS-FACT-*).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "specification-authority-layer"))


def test_from_cache_produces_fods_facts():
    """from_cache_only=True must return >= 78 FODS facts from the real workbench."""
    from sal_master_runner import run_sal_pipeline

    result = run_sal_pipeline(["fods"], from_cache_only=True)
    fods = next(r for r in result["results"] if r["format_id"] == "fods")
    facts = fods.get("spec_facts", [])
    assert len(facts) >= 78, f"Expected >= 78 FODS facts, got {len(facts)}"


def test_from_cache_no_template_ids():
    """from_cache_only=True must not emit any template-namespace IDs."""
    from sal_master_runner import run_sal_pipeline

    result = run_sal_pipeline(["fods", "zst"], from_cache_only=True)
    all_ids = []
    for r in result["results"]:
        all_ids.extend(f["qname"] for f in r.get("spec_facts", []))

    # Template namespace IDs are forbidden: ODF-FACT-*, FODS-FACT-*, etc.
    template_ids = [
        fid for fid in all_ids
        if fid.startswith("ODF-FACT") or fid.startswith("FODS-FACT")
        or (fid.startswith("ODF-") and "FACT" in fid)
    ]
    assert len(template_ids) == 0, f"Template IDs leaked into from_cache output: {template_ids[:5]}"


def test_from_cache_fact_ids_are_workbench_prefixed():
    """All FODS facts from cache must carry FACT-FODS prefix (canonical or extended)."""
    from sal_master_runner import run_sal_pipeline

    result = run_sal_pipeline(["fods"], from_cache_only=True)
    fods = next(r for r in result["results"] if r["format_id"] == "fods")
    facts = fods.get("spec_facts", [])

    non_prefixed = [f["qname"] for f in facts if not f["qname"].startswith("FACT-FODS-")]
    assert len(non_prefixed) == 0, (
        f"Found FODS facts without FACT-FODS- prefix: {non_prefixed[:5]}"
    )


def test_from_cache_zst_facts():
    """ZST workbench must contribute facts when available (graceful if not)."""
    from sal_master_runner import run_sal_pipeline

    result = run_sal_pipeline(["zst"], from_cache_only=True)
    zst_results = [r for r in result["results"] if r["format_id"] == "zst"]
    if not zst_results:
        return  # ZST not in registry — skip
    zst = zst_results[0]
    facts = zst.get("spec_facts", [])
    # If ZST workbench exists, must have >= 15 facts
    if facts:
        assert len(facts) >= 15, f"Expected >= 15 ZST facts from cache, got {len(facts)}"
        # All must carry FACT-ZST- prefix
        non_prefixed = [f["qname"] for f in facts if not f["qname"].startswith("FACT-ZST-")]
        assert len(non_prefixed) == 0, f"ZST facts without FACT-ZST- prefix: {non_prefixed[:5]}"
